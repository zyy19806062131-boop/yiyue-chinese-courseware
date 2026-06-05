# Tone Trainer

A small Python web service for the Mandarin tone melody trainer.

## Run Locally

```bash
python tone_trainer_server.py
```

Open `http://127.0.0.1:8765/`.

The service expects two JSON inputs:

- `trainer_data.json` or `trainer_data.private.json`
- `access_codes.private.json`

For local development, keep those files beside `tone_trainer_server.py`. They are ignored by Git.

## Deploy on Render

This repository includes `render.yaml` for a Render Blueprint web service.

During Blueprint creation, Render will ask for:

- `ACCESS_CODES_JSON`: the full JSON contents of `access_codes.private.json`

The training deck/audio data is committed as `trainer_data.json` so Render does
not need a very large environment variable. Do not commit access codes to
GitHub.
