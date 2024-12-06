# ttstt - TableTop Simulator TerrainTool

Simple HTTP echo server that responds back with whatver you sent it in plain text.  Intended as debugging/testing tool.

👉 The "echoed" body (if a body was included in the original request) will auto-format json and form data for legibility.

## Run
```bash
# from source
python -m ttstt

# prod
gunicorn -w 2 -b "0.0.0.0" ttstt.__main__:app
```