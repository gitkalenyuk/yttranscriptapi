from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

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
        # Коректно дістаємо video_id навіть із посиланнями з параметрами
        if "watch?v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
        else:
            video_id = url
        
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        result = ' '.join([entry['text'] for entry in transcript])
        if not result:
            raise HTTPException(status_code=404, detail="Субтитри не знайдено")
        return result
    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="Субтитри вимкнені для цього відео")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="Cубтитри не знайдено для цієї мови")
    except VideoUnavailable:
        raise HTTPException(status_code=404, detail="Відео недоступне")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка: {e}")

@app.get("/subtitles/info")
async def get_info(url: str = Query(..., description="YouTube URL")):
    try:
        # Коректно дістаємо video_id
        if "watch?v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
        else:
            video_id = url

        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        langs = []
        for t in transcripts:
            langs.append({
                "language": t.language,
                "language_code": t.language_code,
                "is_generated": t.is_generated
            })
        return {"video_id": video_id, "available_languages": langs}
    except VideoUnavailable:
        raise HTTPException(status_code=404, detail="Відео недоступне")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
