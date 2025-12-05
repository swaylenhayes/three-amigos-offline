#!/usr/bin/env python3
"""
Download models to local models directory for offline packaging.
"""

from pathlib import Path
from huggingface_hub import snapshot_download

MODEL_MAP = {
    "ligero": "mlx-community/whisper-small.en-mlx-q4",
    "equilibrado": "mlx-community/whisper-large-v3-turbo-q4",
    "preciso": "mlx-community/whisper-large-v3-turbo",
}


def download_model(repo_id: str, local_dir: Path) -> None:
    """Download a model from HuggingFace to a local directory."""
    print(f"Downloading {repo_id} to {local_dir}...")

    snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False,  # Copy files instead of symlinks for portability
    )

    print(f"✅ {repo_id} downloaded successfully!")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    models_dir = repo_root / "models"
    models_dir.mkdir(exist_ok=True)

    print("📦 Downloading models for offline packaging...\n")

    for model_name, repo_id in MODEL_MAP.items():
        target_dir = models_dir / model_name
        if target_dir.exists():
            has_files = any(target_dir.rglob("*"))
            if has_files:
                print(f"⏭️  {model_name} model already exists at {target_dir}")
                continue
            print(f"♻️  {model_name} directory is empty; re-downloading...")
        download_model(repo_id, target_dir)

    print("\n✅ All models downloaded!")
    print(f"Models location: {models_dir}")

    print("\n📊 Model sizes:")
    for model_path in sorted(p for p in models_dir.iterdir() if p.is_dir()):
        size_mb = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file()) / (1024 * 1024)
        print(f"  {model_path.name}: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
