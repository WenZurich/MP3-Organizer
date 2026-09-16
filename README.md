# MP3 Organizer

Apple-inspired Windows MP3 organizer for YouTube / local music collections.

## Download Windows EXE

Open **Actions** → **Build Windows EXE** → latest successful run → download the **MP3-Organizer-Windows** artifact.

The artifact contains `MP3 Organizer.exe`; Python is not required to run the EXE.

## Features

- Local / YouTube-first smart Artist + Title cleanup
- Low-confidence review highlighting and sortable confidence column
- Batch Album / Album Artist / Compilation metadata
- Random embedded cover art
- Background processing with progress and ETA
- Malformed ID3 repair and verification
- Safe two-phase renaming with rollback

## Build locally

```powershell
py -m pip install -r requirements.txt
py mp3_organizer_v6_5_0.py
```

Windows EXE builds are produced automatically by GitHub Actions.
