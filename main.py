from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI(
    title="YouTube Transcript API",
    description="API для отримання субтитрів з YouTube",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "YouTube Transcript API", 
        "version": "1.0.0",
        "endpoints": {
            "/subtitles": "GET субтитри",
            "/subtitles/info": "GET доступні мови",
            "/health": "GET перевірка"
        }
    }

@app.get("/health")
async def health():
    return {"status": "ok", "message": "API працює"}

@app.get("/subtitles", response_class=PlainTextResponse)
async def get_subtitles(
    url: str = Query(..., description="YouTube URL"),
    lang: str = Query("uk", description="Мова ('uk','en','auto')")
):
    try:
        video_id = url.split("v=")[-1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        result = ' '.join([entry['text'] for entry in transcript])
        if not result:
            raise HTTPException(status_code=404, detail="Субтитри не знайдено")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка: {e}")

@app.get("/subtitles/info")
async def get_info(url: str = Query(...)):
    try:
        video_id = url.split("v=")[-1].split("&")[0]
        langs = YouTubeTranscriptApi.list_transcripts(video_id)
        available = [t.language_code for t in langs]
        return {"video_id": video_id, "available_languages": available}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
