# 📦 Three Amigos Offline Release Notes

## v1.3.0 — 2025-12-04
- Project renamed to **Three Amigos Offline**; release artifacts use the `three-amigos-offline-v1.3.*` naming.
- All three MLX Whisper tiers (ligero, equilibrado, preciso) download with full metadata (config + weights) to avoid missing-file errors during transcription.
- Setup now targets Python 3.12 + `uv` by default and recognizes locally downloaded MLX archives when listing models.
- Packaging: regenerated the offline archive (`three-amigos-offline-v1.3.zip`) and split into GitHub-sized parts (`.partaa`, `.partab`, `.partac`).

### Checksums
- `three-amigos-offline-v1.3.zip`: `23da50465e104c32c63929d0245e8efc949fd50c615c49d6e7dfdea02ac6a7ea`
- `three-amigos-offline-v1.3.zip.partaa`: `f665ab26b7e1e8f876cebb8ada4ba6aaae652c0e40a33b37fb1176f738ac813c`
- `three-amigos-offline-v1.3.zip.partab`: `129828d989248dd183128aa7a07c7b85dfd67610b919a7aee2124412b3ebbd0e`
- `three-amigos-offline-v1.3.zip.partac`: `a863136978586684036562c9c786d6efe0376d65783f0d32c9d7a865ba7118f8`

## v1.2.0 — 2025-11-14
- Upgraded the bundled Parakeet amigo to `parakeet-tdt-0.6b-v3` for better accuracy and stability on Apple Silicon.
- Added automatic filler-word filtering (removes standalone “um”) to keep Parakeet transcripts clean when they are auto-pasted.
- Refreshed the setup guide and packaging instructions so the release download matches the new version naming.
- Regenerated the offline release archive (`dos-amigos-offline-v1.2.zip`) and split it into GitHub-friendly parts: `.partaa` and `.partab`.

### Checksums
- `dos-amigos-offline-v1.2.zip`: `58614564176fc9f3116e7ee530c47a9f3617bcfef9c19c58a77e4ab9b0130153`
- `dos-amigos-offline-v1.2.zip.partaa`: `138e1611cc2cb19a4689221c80b54e46851fb39148acbf0a8039bd4905d47bcc`
- `dos-amigos-offline-v1.2.zip.partab`: `bc806f7225df703102c9ccb2de80316807edb452509e9a5d25939f6c5592de36`

## v1.1.0
- First public offline drop featuring both amigos (Whisper Small MLX + Parakeet TDT 0.6B v2) with push-to-talk and auto-paste on macOS.
- Added setup automation via `src/scripts/setup_offline.py` and instructions for combining split archives from GitHub Releases.
