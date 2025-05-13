# Guide: Crafting Audio Moods with Effects

Welcome to the Audio Mood Shifter! This guide explains the available effects and provides suggestions on how to combine them to evoke specific moods and atmospheres in your music or soundscapes. While "professional" implies clarity and balance, "mood" is about emotional impact and character.

**General Tips Before You Start:**

1.  **Source Quality Matters:** A good starting point is always beneficial. Effects transform, but they don't magically fix poor recordings.
2.  **Subtlety Can Be Powerful:** Often, a slight touch of an effect is more impactful than an overwhelming amount. Always compare your effected sound with the original.
3.  **Listen Critically:** Use good headphones or speakers. Pay attention to how effects alter the feeling of the audio.
4.  **Context is Everything:** The "right" settings depend on the original audio, the genre, and the specific emotion you want to convey.
5.  **Order of Effects:** The effects are applied sequentially as they appear on the UI. Changing the order can dramatically change the outcome. Experiment! (e.g., Gain before a filter sounds different than after).

---

### Understanding the Building Blocks (Effects Overview)

Here's a quick look at each effect and its general potential for mood shaping:

**1. Volume / Gain**

* **What it does:** Makes things louder or quieter.
* **Mood Impact:** Can create drama (sudden loudness/quietness, though this tool applies it globally), intimacy (quieter), or intensity (louder).
* **Parameters:** `Gain (dB)` (0dB = no change).
* **Tips:** Be careful with large boosts to avoid digital distortion (clipping).

**2. High-Pass Filter (HPF) / (Remove Lows)**

* **What it does:** Cuts out low frequencies (bass, rumble).
* **Mood Impact:** Can make audio sound thinner, "smaller," clearer, less powerful, or more focused on mid/high details. Useful for creating a sense of distance or an "old radio" feel.
* **Parameters:** `Cutoff Frequency (Hz)` (e.g., 80Hz, 200Hz, 1000Hz).
* **Tips:** High cutoffs can make things sound very thin or tinny.

**3. Low-Pass Filter (LPF) / (Muffle/Remove Highs)**

* **What it does:** Cuts out high frequencies (treble, hiss, airiness).
* **Mood Impact:** Can make audio sound darker, warmer, muffled, distant, "underwater," or more subdued.
* **Parameters:** `Cutoff Frequency (Hz)` (e.g., 10kHz, 5kHz, 1kHz).
* **Tips:** Low cutoffs can make things sound very unclear or "muddy."

**4. Speed & Pitch Change**

* **What it does (Pydub's `speedup`):** Changes playback speed, which also changes pitch.
* **Mood Impact:**
    * **Faster/Higher Pitch:** Can sound energetic, frantic, comical ("chipmunk"), or childlike.
    * **Slower/Lower Pitch:** Can sound sluggish, heavy, ominous, "demonic," or grand.
* **Parameters:** `Speed Factor` (1.0 = normal; >1.0 = faster/higher; <1.0 = slower/lower).
* **Tips:** Extreme changes can sound very artificial (which might be the goal!).

**5. Simple Echo**

* **What it does:** Adds distinct repetitions of the sound.
* **Mood Impact:** Can create a sense of space, rhythm, psychedelia, emptiness, or call-and-response.
* **Parameters:** `Delay (ms)`, `Decay Factor (0.1-0.8)`.
* **Tips:**
    * Short delays (50-150ms, "slapback") can sound retro or add subtle thickness.
    * Longer delays synced to a beat (if you know the tempo) create rhythmic patterns.
    * High decay makes echoes last longer, potentially creating a wash of sound.

**6. Simple Reverb**

* **What it does:** Simulates the reflections of sound in a space.
* **Mood Impact:** Creates a sense of environment, depth, atmosphere. Can make sounds feel intimate (small room), grand (cathedral), eerie (cave-like), or dreamy.
* **Parameters:** `Wet Level (0-1)`, `Room Size (0-1)`.
* **Tips:**
    * `Wet Level`: How much reverb vs. original sound. Higher wet = more "reverberant" and distant.
    * `Room Size`: Influences the perceived size and tail of the reverb.
    * Your "Simple Reverb" is basic; use it for general atmosphere rather than precise room simulation.

---

### Crafting Moods: Example Effect Chains & Settings

Here are some starting points for creating different moods. Remember to adjust parameters based on your specific audio! The order listed is a suggestion for how you might enable and tweak them on the UI.

**A. Eerie / Mysterious / Spooky**

* **Goal:** Create a sense of unease, suspense, or the supernatural.
* **Effect Chain & Starting Points:**
    1.  **Simple Reverb:**
        * `Wet Level`: 0.4 - 0.7 (more reverb than dry)
        * `Room Size`: 0.6 - 0.9 (simulate a large, echoing, or undefined space)
    2.  **Simple Echo (Optional, for added weirdness):**
        * `Delay`: 400 - 800ms (longer, less rhythmic delays)
        * `Decay Factor`: 0.3 - 0.5 (so echoes don't overpower but add to the atmosphere)
    3.  **Speed & Pitch Change (Optional, for voices or specific sounds):**
        * `Speed Factor`: 0.85 - 0.95 (slightly slowed down, lower pitch) OR 1.05 - 1.15 (slightly sped up and higher, for an unsettling feel).
    4.  **Low-Pass Filter (Optional, for darkness):**
        * `Cutoff Frequency`: 2000 - 4000Hz (to remove some clarity and add a muffled, dark quality).
    5.  **Gain (Subtle):**
        * `Gain (dB)`: Potentially -3dB to -6dB to make it feel more distant or hushed.

**B. Energetic / Exciting / Upbeat**

* **Goal:** Make the audio feel lively, bright, and driving.
* **Effect Chain & Starting Points:**
    1.  **Gain:**
        * `Gain (dB)`: +1 to +3dB (a slight boost for energy, be careful of clipping).
    2.  **High-Pass Filter:**
        * `Cutoff Frequency`: 50 - 80Hz (to clean up any low-end mud that might reduce punch, but don't cut too much bass if it's a full music track).
    3.  **Speed & Pitch Change (Subtle, if appropriate):**
        * `Speed Factor`: 1.01 - 1.05 (a very slight speed-up can add excitement, but use with caution as it changes pitch).
    4.  **Simple Echo (Optional, for rhythmic drive):**
        * `Delay`: Sync to tempo if possible (e.g., 125ms or 250ms for a 120 BPM track's 16th or 8th notes).
        * `Decay Factor`: 0.2 - 0.4 (short, punchy echoes).
    5.  **Simple Reverb (Subtle):**
        * `Wet Level`: 0.1 - 0.25 (just enough to add some life, not wash it out).
        * `Room Size`: 0.2 - 0.5 (smaller, brighter sounding space).

**C. Calm / Relaxing / Dreamy**

* **Goal:** Create a smooth, spacious, and soothing atmosphere.
* **Effect Chain & Starting Points:**
    1.  **Low-Pass Filter:**
        * `Cutoff Frequency`: 6000 - 12000Hz (to gently soften high frequencies, making it less harsh).
    2.  **Simple Reverb:**
        * `Wet Level`: 0.3 - 0.6 (generous reverb for a sense of space).
        * `Room Size`: 0.5 - 0.8 (larger, smoother reverb).
    3.  **Simple Echo (Optional, for gentle movement):**
        * `Delay`: 500 - 1000ms (long, slow echoes).
        * `Decay Factor`: 0.4 - 0.6 (let the echoes linger and blend).
    4.  **Gain (Optional):**
        * `Gain (dB)`: Potentially -1 to -3dB if the original is too loud for a calm feel.
    5.  **Speed & Pitch Change (Optional, very subtle):**
        * `Speed Factor`: 0.95 - 0.98 (a very slight slowdown can sometimes add to a dreamy feel).

**D. Vintage / Nostalgic / Lo-Fi**

* **Goal:** Make the audio sound like an older recording (e.g., old radio, vinyl, cassette).
* **Effect Chain & Starting Points:**
    1.  **High-Pass Filter:**
        * `Cutoff Frequency`: 100 - 300Hz (old systems often lacked deep bass).
    2.  **Low-Pass Filter:**
        * `Cutoff Frequency`: 3000 - 6000Hz (old systems also lacked high-frequency extension).
    3.  **Gain (Optional):**
        * `Gain (dB)`: May need slight adjustments depending on the filtering.
    4.  **Speed & Pitch Change (Optional, for "tape wow/flutter" feel):**
        * `Speed Factor`: Very subtly vary around 1.0 (e.g., 0.99 or 1.01). This effect is hard to achieve perfectly without dedicated modulation.
    5.  **Simple Echo (Optional, for "old tape echo" feel):**
        * `Delay`: 150 - 300ms
        * `Decay Factor`: 0.2 - 0.4 (a bit of a degraded echo).
    * *(To truly get a lo-fi vibe, adding some noise/hiss/crackle would be another step, which isn't an effect in this tool yet).*

**E. Sci-Fi / Futuristic / Alien**

* **Goal:** Create otherworldly, synthetic, or technological soundscapes.
* **Effect Chain & Starting Points:**
    1.  **Speed & Pitch Change:**
        * `Speed Factor`: Experiment wildly! High values (e.g., 1.5-2.0) for robotic/small alien sounds, or very low (0.5-0.7) for large, slow entities.
    2.  **Simple Echo:**
        * `Delay`: Short, metallic delays (50-100ms) or long, sweeping delays (700ms+).
        * `Decay Factor`: Can vary from very short (0.1-0.2 for metallic) to long (0.6-0.7 for spacey).
    3.  **Simple Reverb:**
        * `Wet Level`: 0.4 - 0.8 (often very reverberant).
        * `Room Size`: 0.5 - 0.9 (can be large and unnatural sounding).
    4.  **Low-Pass / High-Pass Filters (Creative):**
        * Use extreme filter settings to create "transmission" effects or highlight unusual frequencies.
        * LPF Cutoff: e.g., 2000Hz for a muffled comms sound.
        * HPF Cutoff: e.g., 1000Hz for a thin, robotic sound.

**F. Dark / Intense / Aggressive**

* **Goal:** Create a sense of power, tension, or aggression.
* **Effect Chain & Starting Points:**
    1.  **Gain:**
        * `Gain (dB)`: +2 to +6dB (louder can feel more intense, watch for clipping).
    2.  **Low-Pass Filter (Subtle, for focus):**
        * `Cutoff Frequency`: 8000 - 12000Hz (can sometimes add focus by removing distracting highs, or make it feel "heavier").
    3.  **Speed & Pitch Change (Optional):**
        * `Speed Factor`: 0.9 - 0.98 (slightly lower pitch can add weight or menace).
    4.  **Simple Reverb (Short & Dark):**
        * `Wet Level`: 0.1 - 0.3
        * `Room Size`: 0.2 - 0.4 (a tight, perhaps slightly dark space).
    * *(True "aggression" often comes from distortion or heavy compression, which are more advanced effects not yet in this tool).*

---

**Final Important Note:**

These are just starting points! The "music standard" for moods is subjective and vast. The best way to master the Audio Mood Shifter is to:

* **Experiment:** Try extreme settings, then subtle ones.
* **Combine:** See how different effects interact.
* **Listen:** Constantly compare the processed audio to the original.
* **Reference:** Listen to music that evokes the mood you're trying to achieve and try to deconstruct how sound is being used.

Happy mood shifting!
