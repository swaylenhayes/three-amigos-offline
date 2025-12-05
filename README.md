# 🎙️ Dos Amigos Offline

Three powerful amigos for automatic speech recognition! Run push-to-talk, auto-paste ASR from terminal, using offline open source MLX Whisper tiers optimized for Mac.

## 🆕 What's New in v1.2
- Bundled Parakeet Amigo now ships with the upgraded `parakeet-tdt-0.6b-v3` checkpoint for extra accuracy.
- Parakeet transcripts automatically strip filler “um” words before being pasted.
- Regenerated the offline archive (`dos-amigos-offline-v1.2.zip`) split into GitHub-sized parts.
- Read the full [release notes](RELEASE_NOTES.md).

## 🧑‍🤝‍🧑 The Three Amigos

- **🪽 El Ligero**
        - Lightweight & fastest
        - Model: [mlx-community/whisper-small.en-mlx-q4](https://huggingface.co/mlx-community/whisper-small.en-mlx-q4)
- **⚖️  El Equilibrado (default)**
        - Balanced speed and quality
        - Model: [mlx-community/whisper-large-v3-turbo-q4](https://huggingface.co/mlx-community/whisper-large-v3-turbo-q4)
- **🎯 El Preciso**
        - Maximum accuracy
        - Model: [mlx-community/whisper-large-v3-turbo](https://huggingface.co/mlx-community/whisper-large-v3-turbo)

## 🚀 Download and Setup Instructions

### Download
👉 [Download from releases](https://github.com/laywen-sashe/dos-amigos-offline/releases).

### Setup
1. Due to GitHub's 2GB limit, download both parts:
1. 📦 dos-amigos-offline-v1.2.zip.partaa
2. 📦 dos-amigos-offline-v1.2.zip.partab
3. Combine both parts `cat dos-amigos-offline-v1.2.zip.part* > dos-amigos-offline-v1.2.zip`
4. Extract `unzip dos-amigos-offline-v1.2.zip`
5. Change directories `cd dos-amigos-offline-v1.2`
6. Run `uv run python src/scripts/setup_offline.py`
7. Activate `source .venv/bin/activate`
7. Run `uv run python src/dos_amigos.py`
8. Press Right Option to record.
9. Press Right Option again to stop recording and paste your recorded text!

### Model options

Use the `--model` flag (default: `equilibrado`) when launching:

```bash
uv run python src/dos_amigos.py --model ligero
uv run python src/dos_amigos.py --model equilibrado
uv run python src/dos_amigos.py --model preciso
```

| Flag           | Repo                                       | Local folder            | Notes                      |
| -------------- | ------------------------------------------ | ----------------------- | -------------------------- |
| `ligero`       | `mlx-community/whisper-small.en-mlx-q4`    | `./models/ligero`       | Lightest and fastest       |
| `equilibrado`* | `mlx-community/whisper-large-v3-turbo-q4`  | `./models/equilibrado`  | Default balanced option    |
| `preciso`      | `mlx-community/whisper-large-v3-turbo`     | `./models/preciso`      | Highest accuracy (largest) |

Download all three tiers without symlinks for easy offline packaging:

```bash
uv run python src/scripts/download_models.py
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file.
