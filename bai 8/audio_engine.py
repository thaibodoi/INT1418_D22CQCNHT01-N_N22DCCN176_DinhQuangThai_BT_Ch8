import numpy as np
import scipy.io.wavfile as wav
import librosa
import os

class AudioEngine:
    def __init__(self, sample_rate=22050):
        self.sr = sample_rate
        self.sounds_dir = "sounds"
        if not os.path.exists(self.sounds_dir):
            os.makedirs(self.sounds_dir)

    def generate_sample_sounds(self):
        """Generate 5 distinct WAV files to demonstrate indexing."""
        duration = 2.0  # seconds
        t = np.linspace(0, duration, int(self.sr * duration))

        # 1. Sine High (1000 Hz) - Clear Pitch
        s1 = 0.5 * np.sin(2 * np.pi * 1000 * t)
        wav.write(os.path.join(self.sounds_dir, "sine_high.wav"), self.sr, s1.astype(np.float32))

        # 2. Sine Low (200 Hz) - Low Pitch
        s2 = 0.5 * np.sin(2 * np.pi * 200 * t)
        wav.write(os.path.join(self.sounds_dir, "sine_low.wav"), self.sr, s2.astype(np.float32))

        # 3. White Noise - High Bandwidth, No Pitch
        s3 = 0.2 * np.random.uniform(-1, 1, len(t))
        wav.write(os.path.join(self.sounds_dir, "white_noise.wav"), self.sr, s3.astype(np.float32))

        # 4. Square Wave - "Bright" sound with many harmonics
        s4 = 0.3 * np.sign(np.sin(2 * np.pi * 440 * t))
        wav.write(os.path.join(self.sounds_dir, "square_bright.wav"), self.sr, s4.astype(np.float32))

        # 5. Pulsed Loud - Varied Loudness
        s5 = 0.8 * np.sin(2 * np.pi * 440 * t) * (np.sin(2 * np.pi * 2 * t) > 0)
        wav.write(os.path.join(self.sounds_dir, "pulsed_loud.wav"), self.sr, s5.astype(np.float32))

        return [
            "sine_high.wav",
            "sine_low.wav",
            "white_noise.wav",
            "square_bright.wav",
            "pulsed_loud.wav"
        ]

    def extract_features(self, file_path):
        """Extract physical audio properties based on Muscle Fish standard."""
        y, sr = librosa.load(file_path, sr=self.sr)

        # 1. Loudness (RMS)
        rms = librosa.feature.rms(y=y)
        loudness = float(np.mean(rms))

        # 2. Pitch (Frequency)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        # Simplify: get mean pitch where magnitude is high
        pitch_indices = np.argmax(magnitudes, axis=0)
        pitch_vals = pitches[pitch_indices, range(pitches.shape[1])]
        valid_pitches = pitch_vals[pitch_vals > 0]
        pitch = float(np.mean(valid_pitches)) if len(valid_pitches) > 0 else 0.0

        # 3. Brightness (Spectral Centroid)
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        brightness = float(np.mean(centroid))

        # 4. Bandwidth (Spectral Bandwidth)
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        avg_bandwidth = float(np.mean(bandwidth))

        # 5. Harmonicity (Simplified as Zero Crossing Rate or Harmony/Percussion ratio)
        # Here we use Zero Crossing Rate as a proxy for 'noisiness' vs 'harmonicity'
        zcr = librosa.feature.zero_crossing_rate(y)
        harmonicity = 1.0 - float(np.mean(zcr)) # 1 = harmonic, 0 = noisy

        return {
            "loudness": round(loudness, 4),
            "pitch": round(pitch, 2),
            "brightness": round(brightness, 2),
            "bandwidth": round(avg_bandwidth, 2),
            "harmonicity": round(harmonicity, 4)
        }

if __name__ == "__main__":
    engine = AudioEngine()
    files = engine.generate_sample_sounds()
    print(f"Generated {len(files)} sounds in 'sounds/' directory.")
    for f in files:
        path = os.path.join("sounds", f)
        feats = engine.extract_features(path)
        print(f"Features for {f}: {feats}")
