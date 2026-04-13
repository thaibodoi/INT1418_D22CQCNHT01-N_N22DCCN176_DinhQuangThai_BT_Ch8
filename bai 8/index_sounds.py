from audio_engine import AudioEngine
from database_manager import DatabaseManager
import os

def index_all():
    engine = AudioEngine()
    db = DatabaseManager()
    
    # Generate if not exists
    if not os.path.exists("sounds"):
        engine.generate_sample_sounds()
    
    files = [f for f in os.listdir("sounds") if f.endswith(".wav")]
    print(f"Indexing {len(files)} files...")
    
    for f in files:
        path = os.path.join("sounds", f)
        features = engine.extract_features(path)
        db.add_audio(f, features)
        print(f"Indexed {f}: {features}")

if __name__ == "__main__":
    index_all()
