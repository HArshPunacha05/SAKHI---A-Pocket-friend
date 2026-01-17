from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json
import base64
from typing import Dict, List
from translation_graph import TranslationGraph
from audio_handler import AudioHandler
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Multilingual Real-time Translator")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
translation_graph = TranslationGraph(api_key=os.getenv("GROQ_API_KEY"))
audio_handler = AudioHandler()

# Store active connections
active_connections: Dict[str, List[WebSocket]] = {}


@app.get("/")
async def root():
    return {
        "message": "Multilingual Real-time Translation API",
        "endpoints": {
            "websocket": "/ws/{room_id}",
            "translate": "/translate",
            "audio_translate": "/audio/translate"
        }
    }


@app.post("/translate")
async def translate_text(
    text: str,
    source_lang: str,
    target_lang: str
):
    """Translate text from source language to target language"""
    result = await translation_graph.translate(text, source_lang, target_lang)
    return result


@app.post("/audio/translate")
async def translate_audio(
    audio_file: UploadFile = File(...),
    source_lang: str = "en",
    target_lang: str = "hi"
):
    """Translate audio from source language to target language"""
    # Save uploaded audio temporarily
    audio_bytes = await audio_file.read()
    
    # Transcribe audio
    transcription = audio_handler.transcribe_audio(audio_bytes, source_lang)
    
    if not transcription:
        return {"error": "Could not transcribe audio"}
    
    # Translate
    translation_result = await translation_graph.translate(
        transcription,
        source_lang,
        target_lang
    )
    
    # Convert to speech
    audio_output = audio_handler.text_to_speech(
        translation_result["translation"],
        target_lang
    )
    
    return {
        "original_text": transcription,
        "translated_text": translation_result["translation"],
        "audio_base64": base64.b64encode(audio_output).decode('utf-8')
    }


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time translation"""
    await websocket.accept()
    
    # Add to room
    if room_id not in active_connections:
        active_connections[room_id] = []
    active_connections[room_id].append(websocket)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process based on message type
            if message["type"] == "translate":
                result = await translation_graph.translate(
                    message["text"],
                    message["source_lang"],
                    message["target_lang"]
                )
                
                # Send to all connections in room
                for connection in active_connections[room_id]:
                    if connection != websocket:
                        await connection.send_json({
                            "type": "translation",
                            "original": message["text"],
                            "translated": result["translation"],
                            "source_lang": message["source_lang"],
                            "target_lang": message["target_lang"],
                            "speaker": message.get("speaker", "unknown")
                        })
                        
    except WebSocketDisconnect:
        active_connections[room_id].remove(websocket)
        if not active_connections[room_id]:
            del active_connections[room_id]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)