# YouTube Transcript API Server

A Flask-based API server that fetches and formats YouTube video transcripts.

## Features

- Fetch transcripts from YouTube videos
- Support for TXT and SRT output formats
- CORS enabled for cross-origin requests
- Production-ready with Gunicorn server

## API Endpoints

### GET /status
Health check endpoint to verify server status.

### GET /transcript
Fetch a video transcript.

Parameters:
- `videoId` (required): YouTube video ID
- `format` (optional): Output format ('txt' or 'srt', default: 'txt')

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
python server.py
```

The server will start at `http://localhost:5000`

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn server:app`
   - Python Version: 3.8.0

The configuration is already set up in `render.yaml`

## Environment Variables

- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Set to 'development' for debug mode

## Example Usage

```bash
# Get transcript in TXT format
curl "https://your-app.onrender.com/transcript?videoId=VIDEO_ID&format=txt"

# Get transcript in SRT format
curl "https://your-app.onrender.com/transcript?videoId=VIDEO_ID&format=srt"
``` 