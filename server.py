from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://bcnbiojdaejdoikimnebjmoagjpcngok", "https://youtube-video-chat.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

class VideoQueryRequest(BaseModel):
    video_id: str
    query: str

class FollowupRequest(BaseModel):
    video_id: str
    followup_query: str

@app.get("/")
def home():
    return "Welcome"

@app.post("/process")
async def process_query(request: VideoQueryRequest):
    video_id = request.video_id
    query = request.query
    print(f"Received request: video_id={video_id}, query={query}")

    # fetch YouTube transcript
    try:
        transcript = get_transcript(video_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Transcript failure")

    # get answer from OpenAI
    answer, timestamp = get_answer(transcript, query)
    timestamp_url = f"https://www.youtube.com/watch?v={video_id}&t={int(timestamp)}s" if timestamp is not None else None

    return {"answer": answer, "timestamp": timestamp, "timestamp_url": timestamp_url}

@app.post("/ask_followup")
async def ask_followup(request: FollowupRequest):
    video_id = request.video_id
    followup_query = request.followup_query

    # get transcript
    transcript = get_transcript(video_id)

    # get follow-up answer
    answer, timestamp = get_answer(transcript, followup_query)
    timestamp_url = f"https://www.youtube.com/watch?v={video_id}&t={int(timestamp)}s" if timestamp is not None else None

    return {"answer": answer, "timestamp": timestamp, "timestamp_url": timestamp_url}

def get_transcript(video_id):
    """Fetch the YouTube transcript."""
    print("getting transcript...")
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print("transcript success")
    return transcript

def get_answer(transcript, query):
    """Query OpenAI to get an answer based on the transcript and the user's question."""
    text = " ".join([item['text'] for item in transcript])
    prompt = f"Given the following transcript, answer the question concisely:\n\n{text}\n\nQuestion: {query}\nAnswer:"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    
    answer = response['choices'][0]['message']['content'].strip()
    timestamp = next((item['start'] for item in transcript if item['text'] in answer), None)
    return answer, timestamp
