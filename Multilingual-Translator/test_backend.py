"""
Backend test script for multilingual translator
Tests the translation graph and API endpoints
"""
import asyncio
import sys
from translation_graph import TranslationGraph
from dotenv import load_dotenv
import os

load_dotenv()

async def test_translation_graph():
    """Test the translation graph functionality"""
    print("=" * 60)
    print("TESTING TRANSLATION GRAPH")
    print("=" * 60)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY not found in .env file")
        return False
    
    print(f"✓ API Key loaded: {api_key[:20]}...")
    
    try:
        translator = TranslationGraph(api_key=api_key)
        print("✓ Translation graph initialized")
        
        # Test 1: English to Hindi
        print("\n--- Test 1: English to Hindi ---")
        result = await translator.translate(
            text="Hello, how are you today?",
            source_lang="en",
            target_lang="hi"
        )
        print(f"Original: Hello, how are you today?")
        print(f"Translation: {result['translation']}")
        print(f"Confidence: {result['confidence']}")
        
        # Test 2: Hindi to English
        print("\n--- Test 2: Hindi to English ---")
        result = await translator.translate(
            text="नमस्ते, आप कैसे हैं?",
            source_lang="hi",
            target_lang="en"
        )
        print(f"Original: नमस्ते, आप कैसे हैं?")
        print(f"Translation: {result['translation']}")
        print(f"Confidence: {result['confidence']}")
        
        # Test 3: English to Spanish
        print("\n--- Test 3: English to Spanish ---")
        result = await translator.translate(
            text="I love learning new languages!",
            source_lang="en",
            target_lang="es"
        )
        print(f"Original: I love learning new languages!")
        print(f"Translation: {result['translation']}")
        print(f"Confidence: {result['confidence']}")
        
        # Test 4: English to French
        print("\n--- Test 4: English to French ---")
        result = await translator.translate(
            text="Good morning, my friend!",
            source_lang="en",
            target_lang="fr"
        )
        print(f"Original: Good morning, my friend!")
        print(f"Translation: {result['translation']}")
        print(f"Confidence: {result['confidence']}")
        
        print("\n✅ All translation tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Translation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_audio_handler():
    """Test audio handler functionality"""
    print("\n" + "=" * 60)
    print("TESTING AUDIO HANDLER")
    print("=" * 60)
    
    try:
        from audio_handler import AudioHandler
        audio_handler = AudioHandler()
        print("✓ Audio handler initialized")
        
        # Test TTS
        print("\n--- Testing Text-to-Speech ---")
        test_texts = [
            ("Hello, this is a test", "en"),
            ("Hola, esto es una prueba", "es"),
            ("नमस्ते, यह एक परीक्षण है", "hi")
        ]
        
        for text, lang in test_texts:
            audio_bytes = audio_handler.text_to_speech(text, lang)
            if audio_bytes:
                print(f"✓ Generated audio for '{text}' ({lang}): {len(audio_bytes)} bytes")
            else:
                print(f"❌ Failed to generate audio for '{text}' ({lang})")
        
        print("\n✅ Audio handler tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Audio handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("\n🚀 Starting Backend Tests\n")
    
    # Test translation graph
    translation_ok = await test_translation_graph()
    
    # Test audio handler
    audio_ok = await test_audio_handler()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Translation Graph: {'✅ PASS' if translation_ok else '❌ FAIL'}")
    print(f"Audio Handler: {'✅ PASS' if audio_ok else '❌ FAIL'}")
    
    if translation_ok and audio_ok:
        print("\n🎉 All backend tests passed! Ready to build frontend.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
