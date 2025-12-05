#!/usr/bin/env python3
"""
Dos Amigos - Offline Whisper-based Speech-to-Text with multiple MLX tiers.
"""

import sys
import subprocess
import tempfile
import os
import argparse
from pathlib import Path

try:
    import sounddevice as sd
    import numpy as np
    import scipy.io.wavfile as wavfile
    from pynput import keyboard
except ImportError as e:
    print(f"Missing core dependency: {e}")
    print("Run the setup script first: python scripts/setup_offline.py")
    sys.exit(1)

MODEL_MAP = {
    "ligero": {
        "repo": "mlx-community/whisper-small.en-mlx-q4",
        "local_dir": "ligero",
        "description": "Lightweight & fast",
    },
    "equilibrado": {
        "repo": "mlx-community/whisper-large-v3-turbo-q4",
        "local_dir": "equilibrado",
        "description": "Balanced speed and quality",
    },
    "preciso": {
        "repo": "mlx-community/whisper-large-v3-turbo",
        "local_dir": "preciso",
        "description": "Maximum accuracy",
    },
}


class DosAmigos:
    def __init__(self, amigo_type: str = "equilibrado", model_path: str | None = None):
        self.amigo_type = amigo_type.lower()
        self.model_config = MODEL_MAP.get(self.amigo_type)

        if not self.model_config:
            raise ValueError(f"Unknown amigo type: {self.amigo_type}")

        self.model_path = model_path
        self.model = None
        self.is_recording = False
        self.recording_data = []
        self.sample_rate = 16000
        self.hotkey = keyboard.Key.alt_r  # Right Option key as toggle

        print(f"Initializing Dos Amigos with {self.amigo_type.upper()} model...")
        self.load_model()
        print(f"✓ {self.amigo_type.upper()} amigo loaded successfully!")
        print(f"✓ Toggle key: Right Option")
        print("✓ Ready! Press Right Option to start/stop recording.")

    def find_local_model(self) -> str | None:
        """Find the local model directory for the selected amigo."""
        script_dir = Path(__file__).resolve().parent
        candidate_roots = [
            script_dir / "models",
            script_dir.parent / "models",
            Path.cwd() / "models",
        ]

        for root in candidate_roots:
            model_dir = root / self.model_config["local_dir"]
            if model_dir.exists():
                model_files = list(model_dir.rglob("*.safetensors")) + list(model_dir.rglob("*.mlx"))
                if model_files:
                    print(f"Found local {self.amigo_type} model at: {model_dir}")
                    return str(model_dir)
        return None

    def load_model(self) -> None:
        try:
            self.load_whisper_model()
        except Exception as e:
            print(f"Error loading {self.amigo_type} amigo: {e}")
            print("Make sure you've run the setup script and have the model files.")
            if self.amigo_type != "ligero":
                print("Try using --model ligero for the lightweight amigo.")
            sys.exit(1)

    def load_whisper_model(self) -> None:
        """Load Whisper MLX model."""
        try:
            import mlx_whisper
        except ImportError:
            raise ImportError("mlx-whisper not installed. Install with: uv pip install mlx-whisper")

        if self.model_path:
            self.model_path_or_repo = self.model_path
        else:
            local_path = self.find_local_model()
            if local_path and Path(local_path).exists():
                self.model_path_or_repo = local_path
            else:
                print(f"Local {self.amigo_type.title()} model not found, using {self.model_config['repo']}...")
                self.model_path_or_repo = self.model_config["repo"]

        print(f"{self.amigo_type.title()} model configured: {self.model_path_or_repo}")
        self.model = self.model_path_or_repo  # Store the path/repo for transcribe()

    def audio_callback(self, indata, frames, time, status):
        """Callback for audio recording"""
        if status:
            print(f"Audio status: {status}")

        if self.is_recording:
            self.recording_data.append(indata.copy())

    def start_recording(self):
        """Start audio recording"""
        if self.is_recording:
            return

        print("🎤 Recording... Press Right Option again to stop.")
        self.is_recording = True
        self.recording_data = []

        # Start audio stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32,
            callback=self.audio_callback,
            blocksize=1024
        )
        self.stream.start()

    def stop_recording(self):
        """Stop recording and transcribe"""
        if not self.is_recording:
            return

        self.is_recording = False
        self.stream.stop()
        self.stream.close()

        if not self.recording_data:
            print("No audio recorded.")
            return

        print(f"🛑 Recording stopped. Transcribing with {self.amigo_type.upper()} amigo...")

        # Concatenate recorded audio
        audio_data = np.concatenate(self.recording_data, axis=0)
        audio_data = audio_data.flatten()

        # Save to temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_path = temp_file.name
        temp_file.close()  # Close the file handle so we can write to it

        # Convert to 16-bit PCM WAV
        audio_int16 = (audio_data * 32767).astype(np.int16)
        wavfile.write(temp_path, self.sample_rate, audio_int16)

        try:
            transcription = self.transcribe_audio(temp_path)

            if transcription and transcription.strip():
                print(f"📝 Transcription: {transcription}")
                self.paste_text(transcription)
            else:
                print("❌ No speech detected or transcription failed.")

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            import traceback
            traceback.print_exc()  # This will show the full error

        finally:
            # Clean up temp file
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except Exception as e:
                print(f"Debug: Error cleaning up temp file: {e}")

    def transcribe_audio(self, audio_path):
        """Transcribe audio using the selected model"""
        try:
            return self.transcribe_with_whisper(audio_path)
        except Exception as e:
            print(f"Transcription error with {self.amigo_type}: {e}")
            return ""

    def transcribe_with_whisper(self, audio_path):
        """Transcribe using Whisper MLX"""

        # Validate audio file exists and has content
        if not os.path.exists(audio_path):
            print(f"Error: Audio file does not exist: {audio_path}")
            return ""

        file_size = os.path.getsize(audio_path)
        if file_size == 0:
            print(f"Error: Audio file is empty: {audio_path}")
            return ""

        try:
            import mlx_whisper
        except ImportError as e:
            print(f"Import error: {e}")
            return ""

        try:
            result = mlx_whisper.transcribe(
                audio_path,
                path_or_hf_repo=self.model,  # This is the model path or repo
                language="en",  # English optimized
                fp16=True       # Use half precision for memory efficiency
            )

            if result is None:
                print("Warning: Transcription returned None - likely audio loading failed")
                return ""

            if isinstance(result, dict):
                if 'text' in result:
                    text = result['text'].strip()
                    return text
                elif 'segments' in result and result['segments']:
                    text_parts = []
                    for segment in result['segments']:
                        if 'text' in segment:
                            text_parts.append(segment['text'])
                    combined_text = ' '.join(text_parts).strip()
                    return combined_text
                else:
                    print(f"Warning: Unexpected result format: {result}")
                    return str(result).strip()
            else:
                fallback_text = str(result).strip()
                return fallback_text

        except Exception as e:
            print(f"MLX Whisper transcription error: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def remove_filler_words(self, text):
        """Remove filler words like 'um' from transcription"""
        import re

        text = re.sub(r'\b[Uu]m\b', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def paste_text(self, text):
        """Paste text to the current application using clipboard"""
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))

            subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to keystroke "v" using command down'
            ])

            print("✅ Text pasted to active application!")

        except Exception as e:
            print(f"❌ Failed to paste text: {e}")
            print(f"📋 Copied to clipboard: {text}")

    def on_hotkey_press(self, key):
        """Handle hotkey press events"""
        if key == self.hotkey:
            if not self.is_recording:
                self.start_recording()
            else:
                self.stop_recording()

    def run(self):
        """Main application loop"""
        print("\n" + "="*60)
        print(f"🎙️  Dos Amigos RUNNING ({self.amigo_type.upper()} AMIGO)")
        print("="*60)
        print("Toggle key: Right Option")
        print("Press Ctrl+C to quit")
        print("="*60 + "\n")

        with keyboard.Listener(on_press=self.on_hotkey_press) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                if self.is_recording:
                    self.stop_recording()
                sys.exit(0)


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Dos Amigos Offline - Whisper MLX tiers with auto paste.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Amigos:
  🪽 Ligero: whisper-small.en-mlx-q4
  ⚖️  Equilibrado: whisper-large-v3-turbo-q4 (default)
  🎯 Preciso: whisper-large-v3-turbo

Examples:
  uv run python src/dos_amigos.py                    # Use Equilibrado (default)
  uv run python src/dos_amigos.py --model ligero     # Use Ligero explicitly
  uv run python src/dos_amigos.py --model preciso    # Use Preciso
  uv run python src/dos_amigos.py --path /custom/model/path  # Use custom model path
        """
    )

    parser.add_argument(
        '--model', '-m',
        choices=list(MODEL_MAP.keys()),
        default='equilibrado',
        help='Amigo to use for transcription (default: equilibrado)'
    )

    parser.add_argument(
        '--path', '-p',
        type=str,
        help='Custom path to model directory',
    )

    parser.add_argument(
        '--list-models',
        action='store_true',
        help='List available local models and exit',
    )

    args = parser.parse_args()

    if args.list_models:
        print("🔍 Scanning for local models...")
        script_dir = Path(__file__).parent
        models_dir = script_dir.parent / "models"

        if models_dir.exists():
            print(f"\nModels directory: {models_dir}")
            for key, config in MODEL_MAP.items():
                model_path = models_dir / config["local_dir"]
                if model_path.exists() and (
                    any(model_path.rglob("*.safetensors"))
                    or any(model_path.rglob("*.mlx"))
                ):
                    size_mb = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file()) / (1024 * 1024)
                    print(f"  {key} ({model_path.name}): {size_mb:.1f} MB")
                else:
                    print(f"  {key} ({model_path.name}): not found")
        else:
            print("❌ Models directory not found.")

        return

    try:
        app = DosAmigos(amigo_type=args.model, model_path=args.path)
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
