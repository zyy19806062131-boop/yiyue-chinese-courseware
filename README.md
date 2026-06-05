# Tone Trainer

A small Python web service for the Mandarin tone melody trainer.

## Run Locally

```bash
python tone_trainer_server.py
```

Open `http://127.0.0.1:8765/`.

The service expects two private JSON inputs:

- `trainer_data.private.json`
- `access_codes.private.json`

For local development, keep those files beside `tone_trainer_server.py`. They are ignored by Git.

## Deploy on Render

This repository includes `render.yaml` for a Render Blueprint web service.

During Blueprint creation, Render will ask for:

- `TRAINER_DATA_JSON`: the full JSON contents of `trainer_data.private.json`
- `ACCESS_CODES_JSON`: the full JSON contents of `access_codes.private.json`

Do not commit those private values to GitHub.
