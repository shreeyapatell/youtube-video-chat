from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS for your Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://bcnbiojdaejdoikimnebjmoagjpcngok"],  # Replace with your Chrome extension's ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

class VideoQueryRequest(BaseModel):
    video_id: str
    query: str

class FollowupRequest(BaseModel):
    video_id: str
    followup_query: str

@app.post("/process/")
async def process_query(request: VideoQueryRequest):
    video_id = request.video_id
    query = request.query

    # Fetch YouTube transcript
    try:
        transcript = get_transcript(video_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Transcript not found")

    # Get answer from OpenAI
    answer, timestamp = get_answer(transcript, query)
    timestamp_url = f"https://www.youtube.com/watch?v={video_id}&t={int(timestamp)}s" if timestamp is not None else None

    return {"answer": answer, "timestamp": timestamp, "timestamp_url": timestamp_url}

@app.post("/ask_followup/")
async def ask_followup(request: FollowupRequest):
    video_id = request.video_id
    followup_query = request.followup_query

    # Get transcript
    transcript = get_transcript(video_id)

    # Get follow-up answer
    answer, timestamp = get_answer(transcript, followup_query)
    timestamp_url = f"https://www.youtube.com/watch?v={video_id}&t={int(timestamp)}s" if timestamp is not None else None

    return {"answer": answer, "timestamp": timestamp, "timestamp_url": timestamp_url}

def get_transcript(video_id):
    """Fetch the YouTube transcript."""
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
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
