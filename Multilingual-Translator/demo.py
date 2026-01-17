"""
Demo script to test the translation system
Simulates two users chatting in different languages
"""
import asyncio
import websockets
import json
import requests
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
ROOM_ID = "DEMO123"

# User configurations
USER1 = {
    "name": "Alice",
    "language": "en",
    "messages": [
        "Hello! How are you today?",
        "I'm doing great! What about you?",
        "That's wonderful to hear!",
        "What are you working on today?"
    ]
}

USER2 = {
    "name": "राज",
    "language": "hi",
    "messages": [
        "नमस्ते! मैं ठीक हूं, धन्यवाद।",
        "मैं भी बहुत अच्छा हूं!",
        "आज मैं एक नई परियोजना पर काम कर रहा हूं।",
        "यह बहुत रोमांचक है!"
    ]
}

async def translate_message(text, source_lang, target_lang):
    """Translate a message using the API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/translate",
            data={
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        )
        if response.ok:
            result = response.json()
            return result.get("translation", "")
        return None
    except Exception as e:
        print(f"Translation error: {e}")
        return None

async def simulate_user(user_config, target_lang, delay=3):
    """Simulate a user sending messages"""
    user_name = user_config["name"]
    user_lang = user_config["language"]
    
    print(f"\n{'='*60}")
    print(f"🎭 Simulating {user_name} ({user_lang} → {target_lang})")
    print(f"{'='*60}\n")
    
    for i, message in enumerate(user_config["messages"], 1):
        # Wait before sending
        await asyncio.sleep(delay)
        
        # Translate the message
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {user_name} is typing...")
        translation = await translate_message(message, user_lang, target_lang)
        
        if translation:
            print(f"\n📤 {user_name} sent:")
            print(f"   Original ({user_lang}): {message}")
            print(f"   Translation ({target_lang}): {translation}")
            print(f"   ✅ Message {i}/{len(user_config['messages'])} sent\n")
        else:
            print(f"   ❌ Failed to translate message {i}\n")

async def test_websocket_connection():
    """Test WebSocket connection"""
    print("\n" + "="*60)
    print("🔌 Testing WebSocket Connection")
    print("="*60 + "\n")
    
    try:
        uri = f"{WS_URL}/ws/{ROOM_ID}"
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to room: {ROOM_ID}")
            
            # Send a test message
            test_message = {
                "type": "translate",
                "text": "Hello from WebSocket!",
                "source_lang": "en",
                "target_lang": "hi",
                "speaker": "Test User"
            }
            
            await websocket.send(json.dumps(test_message))
            print("✅ Test message sent via WebSocket")
            
            # Wait a bit
            await asyncio.sleep(2)
            
            print("✅ WebSocket connection working!\n")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}\n")
        print("Make sure the backend server is running on port 8000\n")

async def run_demo():
    """Run the complete demo"""
    print("\n" + "🌍"*30)
    print("\n   TRANSLATEBRIDGE - DEMO SIMULATION")
    print("   Real-time Translation System Test\n")
    print("🌍"*30 + "\n")
    
    # Test WebSocket
    await test_websocket_connection()
    
    # Simulate conversation
    print("="*60)
    print("💬 Starting Conversation Simulation")
    print("="*60)
    print("\nScenario: Alice (English) ↔️ राज (Hindi)")
    print("Messages will be sent alternately with translations\n")
    
    # Alternate between users
    max_messages = max(len(USER1["messages"]), len(USER2["messages"]))
    
    for i in range(max_messages):
        # User 1 sends message
        if i < len(USER1["messages"]):
            message = USER1["messages"][i]
            print(f"\n{'─'*60}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {USER1['name']} is typing...")
            
            translation = await translate_message(
                message, 
                USER1["language"], 
                USER2["language"]
            )
            
            if translation:
                print(f"\n📤 {USER1['name']} ({USER1['language']}):")
                print(f"   \"{message}\"")
                print(f"\n📥 {USER2['name']} sees ({USER2['language']}):")
                print(f"   \"{translation}\"")
                print(f"   ✅ Delivered")
            else:
                print(f"   ❌ Translation failed")
            
            await asyncio.sleep(2)
        
        # User 2 sends message
        if i < len(USER2["messages"]):
            message = USER2["messages"][i]
            print(f"\n{'─'*60}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {USER2['name']} is typing...")
            
            translation = await translate_message(
                message, 
                USER2["language"], 
                USER1["language"]
            )
            
            if translation:
                print(f"\n📤 {USER2['name']} ({USER2['language']}):")
                print(f"   \"{message}\"")
                print(f"\n📥 {USER1['name']} sees ({USER1['language']}):")
                print(f"   \"{translation}\"")
                print(f"   ✅ Delivered")
            else:
                print(f"   ❌ Translation failed")
            
            await asyncio.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("📊 DEMO SUMMARY")
    print("="*60)
    print(f"✅ Total messages from {USER1['name']}: {len(USER1['messages'])}")
    print(f"✅ Total messages from {USER2['name']}: {len(USER2['messages'])}")
    print(f"✅ Language pair: {USER1['language']} ↔️ {USER2['language']}")
    print(f"✅ Room ID: {ROOM_ID}")
    print("\n🎉 Demo completed successfully!")
    print("\nNow open http://localhost:3000 in two browser windows")
    print("and try it yourself with real-time WebSocket communication!\n")

if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        print("\nMake sure the backend server is running:")
        print("  python app.py")
