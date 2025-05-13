import os
import logging
from pydub import AudioSegment
from pydub.effects import low_pass_filter as pydub_low_pass
from pydub.effects import high_pass_filter as pydub_high_pass # Import high_pass_filter
# from scipy.signal import butter, lfilter # Keep for potential custom SciPy filters if needed later
import numpy as np
import math # For log10 in reverb

logger = logging.getLogger(__name__)

# --- Effect Helper Functions ---

def _apply_gain(audio_segment, gain_db):
    """Applies a gain change in dB."""
    logger.info(f"Applying gain of {gain_db} dB.")
    if not isinstance(gain_db, (int, float)):
        logger.warning(f"Invalid gain_db type: {gain_db}. Must be a number. Skipping gain.")
        return audio_segment
    return audio_segment + float(gain_db)

def _apply_high_pass_filter_effect(audio_segment, cutoff_hz):
    """Applies a high-pass filter using Pydub's built-in."""
    logger.info(f"Applying high-pass filter effect with cutoff {cutoff_hz} Hz.")
    if not isinstance(cutoff_hz, (int, float)) or cutoff_hz <= 0:
        logger.warning(f"Invalid high-pass cutoff frequency: {cutoff_hz}. Must be positive. Skipping filter.")
        return audio_segment
    # Pydub's high_pass_filter expects int
    if cutoff_hz >= audio_segment.frame_rate / 2: # Check against Nyquist
        logger.warning(f"High-pass cutoff {int(cutoff_hz)}Hz is too high for sample rate {audio_segment.frame_rate}Hz. Skipping filter.")
        return audio_segment
    return pydub_high_pass(audio_segment, int(cutoff_hz))

def _apply_low_pass_filter(audio_segment, cutoff_hz):
    """Applies a low-pass filter using Pydub's built-in."""
    logger.info(f"Applying low-pass filter with cutoff {cutoff_hz} Hz.")
    if not isinstance(cutoff_hz, (int, float)) or cutoff_hz <= 0:
        logger.warning(f"Invalid low-pass cutoff frequency: {cutoff_hz}. Must be positive. Skipping filter.")
        return audio_segment
    # Pydub's low_pass_filter expects int
    if cutoff_hz >= audio_segment.frame_rate / 2: # Check against Nyquist
        logger.warning(f"Low-pass cutoff {int(cutoff_hz)}Hz is too high for sample rate {audio_segment.frame_rate}Hz. Skipping filter.")
        return audio_segment
    return pydub_low_pass(audio_segment, int(cutoff_hz))

def _apply_speed_pitch(audio_segment, factor):
    """Changes speed and pitch."""
    logger.info(f"Applying speed/pitch change with factor {factor}.")
    if not isinstance(factor, (int, float)):
        logger.warning(f"Invalid speed factor type: {factor}. Must be a number. Skipping effect.")
        return audio_segment
    if factor == 1.0: 
        logger.info("Speed factor is 1.0, no change applied.")
        return audio_segment
    if factor <= 0:
        logger.warning(f"Speed factor must be positive. Value was {factor}. Skipping effect.")
        return audio_segment
    try:
        # Pydub's speedup changes both speed and pitch.
        return audio_segment.speedup(playback_speed=float(factor), chunk_size=150, crossfade=100)
    except Exception as e:
        logger.error(f"Error during Pydub speedup with factor {factor}: {e}", exc_info=True)
        return audio_segment

def _apply_echo(audio_segment, delay_ms, decay_factor):
    """Applies a simple echo."""
    logger.info(f"Applying echo with delay {delay_ms}ms and decay {decay_factor}.")
    if not isinstance(delay_ms, (int, float)) or delay_ms <= 0:
        logger.warning(f"Invalid echo delay_ms: {delay_ms}. Skipping.")
        return audio_segment
    if not isinstance(decay_factor, (int, float)) or not (0 < decay_factor < 1): # Decay factor should be between 0 and 1 (exclusive of 0)
        logger.warning(f"Invalid echo decay_factor: {decay_factor}. Must be between 0 (exclusive) and 1 (exclusive). Skipping.")
        return audio_segment

    output_audio = audio_segment
    if len(audio_segment) > 0:
        # dB = 20 * log10(amplitude_ratio)
        db_reduction = 20 * math.log10(decay_factor) # Use math.log10
        
        delay_segment = AudioSegment.silent(duration=int(delay_ms), frame_rate=audio_segment.frame_rate)
        echoed_sound = audio_segment + db_reduction # Attenuate the segment for the echo
        
        full_echo_segment = delay_segment + echoed_sound
        output_audio = output_audio.overlay(full_echo_segment)
    else:
        logger.warning("Cannot apply echo to empty audio segment.")
    return output_audio

def _apply_reverb_simple(audio_segment, wet_level=0.3, room_size=0.5):
    """
    Applies a very simple algorithmic reverb by mixing multiple delayed, attenuated copies.
    This is a basic reverb and won't sound like professional studio reverb.
    wet_level: How much of the reverberated signal to mix (0.0 to 1.0).
    room_size: Affects delay times and decay (0.0 to 1.0).
    """
    logger.info(f"Applying simple reverb with wet_level: {wet_level}, room_size: {room_size}")
    if not (0 <= wet_level <= 1 and 0 <= room_size <= 1):
        logger.warning("Invalid reverb parameters (wet_level/room_size out of 0-1 range). Skipping effect.")
        return audio_segment
    if wet_level == 0:
        logger.info("Reverb wet_level is 0. Skipping reverb effect.")
        return audio_segment
    if len(audio_segment) == 0:
        logger.warning("Cannot apply reverb to empty audio segment.")
        return audio_segment

    dry_signal = audio_segment
    # Initialize wet_signal as silent, with the same duration as the dry signal
    # This ensures overlay works correctly if dry_signal is shorter than some echos.
    wet_signal = AudioSegment.silent(duration=len(dry_signal), frame_rate=dry_signal.frame_rate)

    # Define some delay taps based on room_size (these are just examples)
    # These delays are short and aim for a dense early reflection feel + some tail
    base_delays_ms = [23, 37, 53, 71, 97, 131, 173, 223] # Prime-ish numbers often used
    delays = [int(d * (0.5 + room_size * 1.5)) for d in base_delays_ms] # Scale delays
    
    # Define decay for each tap (more decay for longer delays, influenced by room_size)
    base_decays = [0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35]
    decays = [d * (1.0 - room_size * 0.5) for d in base_decays] # Larger room_size = slower decay (less attenuation)

    for i in range(len(delays)):
        delay_ms = delays[i]
        decay_factor = max(0.01, decays[i]) # Ensure decay_factor is not zero for log

        if delay_ms > 0:
            # Create echo tap: silence for delay, then the attenuated original sound
            attenuated_tap_sound = dry_signal + (20 * math.log10(decay_factor))
            echo_tap = AudioSegment.silent(duration=delay_ms, frame_rate=dry_signal.frame_rate) + attenuated_tap_sound
            
            # Mix this tap into the wet_signal. Overlay will extend wet_signal if needed.
            wet_signal = wet_signal.overlay(echo_tap)

    if len(wet_signal) == 0: return dry_signal

    # Mix dry and wet signals based on wet_level
    # A simple approach: scale dry by (1-wet_level) and wet by wet_level, then combine.
    # Pydub handles gain in dB.
    # Dry part: gain based on (1 - wet_level)
    # Wet part: gain based on wet_level
    
    # To avoid issues with log(0), add a small epsilon if wet_level is 0 or 1
    # However, if wet_level is 0, we returned early. If 1, dry_gain_db would be -infinity.
    
    dry_gain_db = -120.0 # Effectively silent if wet_level is 1.0
    if wet_level < 1.0:
        dry_gain_db = 20 * math.log10(1.0 - wet_level + 1e-6) # Add epsilon

    wet_gain_db = 20 * math.log10(wet_level + 1e-6)

    mixed_audio = (dry_signal + dry_gain_db).overlay(wet_signal + wet_gain_db)
    
    return mixed_audio


# --- Main Effects Processing Function ---
def apply_audio_effects_core(
    input_path, 
    output_path, 
    output_format="wav",
    effects_chain=None, 
    task_update_meta_func=None
    ):
    if effects_chain is None: effects_chain = []
    try:
        logger.info(f"Effects processing: Input='{input_path}', Output='{output_path}', Format={output_format}")
        if task_update_meta_func: task_update_meta_func(state='PROGRESS', meta={'status': 'Loading audio...', 'progress': 5})
        audio = AudioSegment.from_file(input_path)
        logger.info(f"Loaded: Duration={len(audio)/1000.0:.2f}s, Channels={audio.channels}, SR={audio.frame_rate}Hz")

        current_progress = 10
        num_effects = len(effects_chain)
        progress_step = (80 - current_progress) / num_effects if num_effects > 0 else 0

        for i, effect_config in enumerate(effects_chain):
            effect_name = effect_config.get('name')
            if not effect_name:
                logger.warning(f"Skipping effect {i}: missing 'name'. Config: {effect_config}")
                continue
            
            logger.info(f"Applying {i+1}/{num_effects}: '{effect_name}' with {effect_config}")
            if task_update_meta_func: task_update_meta_func(state='PROGRESS', meta={'status': f'Applying: {effect_name.replace("_", " ").title()}', 'progress': int(current_progress)})

            if effect_name == 'gain':
                audio = _apply_gain(audio, effect_config.get('gain_db', 0.0)) # Default to 0dB
            elif effect_name == 'high_pass_filter':
                audio = _apply_high_pass_filter_effect(audio, effect_config.get('cutoff_hz', 80)) # Default 80Hz
            elif effect_name == 'low_pass_filter':
                audio = _apply_low_pass_filter(audio, effect_config.get('cutoff_hz', 5000)) # Default 5000Hz
            elif effect_name == 'speed_pitch':
                audio = _apply_speed_pitch(audio, effect_config.get('factor', 1.0)) # Default 1.0 (no change)
            elif effect_name == 'echo':
                audio = _apply_echo(audio, effect_config.get('delay_ms', 500), effect_config.get('decay_factor', 0.5))
            elif effect_name == 'reverb':
                audio = _apply_reverb_simple(audio, effect_config.get('wet_level', 0.3), effect_config.get('room_size', 0.5))
            else:
                logger.warning(f"Unknown effect: '{effect_name}'. Skipping.")
            current_progress += progress_step
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        logger.info(f"Exporting to '{output_path}' as '{output_format}'...")
        if task_update_meta_func: task_update_meta_func(state='PROGRESS', meta={'status': 'Exporting file...', 'progress': 90})
        
        export_params = {"format": "wav"} # Default
        if output_format.lower() == "mp3": export_params = {"format": "mp3", "bitrate": "192k"}
        elif output_format.lower() == "m4a": export_params = {"format": "ipod"}
        audio.export(output_path, **export_params)
        
        logger.info("Effects processing complete.")
        if task_update_meta_func: task_update_meta_func(state='SUCCESS', meta={'status': 'Effects applied!', 'progress': 100, 'result_filename': os.path.basename(output_path)})
        return True, os.path.basename(output_path)
    except Exception as e:
        logger.error(f"Error in apply_audio_effects_core for '{input_path}': {e}", exc_info=True)
        if task_update_meta_func: task_update_meta_func(state='FAILURE', meta={'status': f'Error applying effects: {str(e)}', 'progress': 0})
        if os.path.exists(output_path):
            try: os.remove(output_path)
            except OSError as oe: logger.error(f"Could not remove partial output '{output_path}': {oe}")
        return False, str(e)
    finally: pass

# Optional: Original _high_pass_filter_original_scipy can be kept or removed
# def _high_pass_filter_original_scipy(audio_segment, cutoff_hz, sample_rate):
#    logger.info(f"Applying SciPy high-pass filter with cutoff {cutoff_hz} Hz.")
#    # ... (implementation as before) ...
#    pass