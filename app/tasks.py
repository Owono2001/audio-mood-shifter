import os
import time
from datetime import datetime, timedelta # Keep this if used by cleanup or other tasks
from celery import shared_task, current_task
from flask import current_app 

# Import the NEW core processing function for effects
from app.services.audio_processor import apply_audio_effects_core 
# The line that was previously here importing 'process_audio_file_core' MUST be removed.

import logging
logger = logging.getLogger(__name__) # Celery worker will configure this logger

@shared_task(bind=True)
def process_audio_task_effects(self, input_filepath, original_filename, output_filename_base, output_format, effects_chain):
    """
    Celery task to apply a chain of audio effects.
    """
    logger.info(f"Celery effects task {self.request.id} started for {original_filename} with effects: {effects_chain}")
    
    output_folder = current_app.config['PROCESSED_FOLDER']
    output_filepath = os.path.join(output_folder, f"{output_filename_base}.{output_format}")

    try:
        self.update_state(state='PROGRESS', meta={'status': 'Initializing effects processing...', 'progress': 1, 'original_filename': original_filename})
        
        def update_celery_meta(state, meta):
            meta['original_filename'] = original_filename
            self.update_state(state=state, meta=meta)

        # Call the new core function for applying effects
        success, result_or_error = apply_audio_effects_core(
            input_path=input_filepath,
            output_path=output_filepath,
            output_format=output_format,
            effects_chain=effects_chain,
            task_update_meta_func=update_celery_meta
        )

        if success:
            logger.info(f"Effects task {self.request.id} completed successfully. Output: {result_or_error}")
            return {'status': 'Effects applied successfully!', 'progress': 100, 'result_filename': result_or_error, 'original_filename': original_filename}
        else:
            logger.error(f"Effects task {self.request.id} failed for {original_filename}. Error: {result_or_error}")
            if self.AsyncResult(self.request.id).state != 'FAILURE': # Ensure state is set if not already
                 self.update_state(state='FAILURE', meta={'status': f'Effect processing error: {result_or_error}', 'progress': 0, 'original_filename': original_filename})
            return {'status': f'Error applying effects: {result_or_error}', 'progress': 0, 'original_filename': original_filename, 'error_details': result_or_error}

    except Exception as e:
        logger.critical(f"Critical error in Celery effects task {self.request.id} for {original_filename}: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'status': f'Critical task error: {str(e)}', 'progress': 0, 'original_filename': original_filename})
        return {'status': f'Critical Error: {str(e)}', 'progress': 0, 'original_filename': original_filename, 'error_details': str(e)}
    finally:
        # Clean up the original uploaded file
        if os.path.exists(input_filepath):
            try:
                os.remove(input_filepath)
                logger.info(f"Cleaned up uploaded file for effects task: {input_filepath}")
            except OSError as e:
                logger.error(f"Error cleaning up uploaded file {input_filepath} for effects task: {e}")


@shared_task(name='app.tasks.cleanup_old_files_task') # Explicit name for beat schedule
def cleanup_old_files_task(max_age_days=7): # Default value if not passed
    """
    Celery Beat task to clean up old files from upload and processed directories.
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    processed_folder = current_app.config['PROCESSED_FOLDER']
    
    try:
        max_age_days_config = current_app.config.get('CLEANUP_MAX_FILE_AGE_DAYS', str(max_age_days))
        max_age_days_int = int(max_age_days_config)
    except ValueError:
        logger.warning(
            f"Invalid value for CLEANUP_MAX_FILE_AGE_DAYS in config: '{max_age_days_config}'. "
            f"Using default {max_age_days} days."
        )
        max_age_days_int = int(max_age_days)

    now = time.time()
    cutoff = now - (max_age_days_int * 24 * 60 * 60)

    logger.info(f"Running cleanup task. Deleting files older than {max_age_days_int} days.")
    
    cleaned_count = 0
    for folder_path in [upload_folder, processed_folder]:
        if not os.path.isdir(folder_path):
            logger.warning(f"Cleanup: Folder '{folder_path}' does not exist. Skipping.")
            continue
        try:
            for filename in os.listdir(folder_path):
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath): 
                    try:
                        file_modification_time = os.path.getmtime(filepath)
                        if file_modification_time < cutoff:
                            os.remove(filepath)
                            logger.info(f"Cleanup: Deleted old file '{filepath}'")
                            cleaned_count += 1
                    except FileNotFoundError:
                        logger.warning(f"Cleanup: File '{filepath}' not found during deletion attempt. Skipping.")
                    except OSError as e:
                        logger.error(f"Cleanup: Error deleting file '{filepath}': {e}")
        except Exception as e:
             logger.error(f"Cleanup: Error listing files in folder '{folder_path}': {e}", exc_info=True)

    logger.info(f"Cleanup task finished. Deleted {cleaned_count} old files.")
    return f"Cleaned up {cleaned_count} files older than {max_age_days_int} days."
