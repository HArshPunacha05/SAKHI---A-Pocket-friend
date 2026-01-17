#!/usr/bin/env python3
"""
Sakhi — A Pocket Friend
CLI entrypoint for real-time voice translation.
"""

import argparse
import logging
import sys

from sakhi.realtime import run_realtime_translator


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Reduce noise from some libraries
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('torch').setLevel(logging.WARNING)


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Sakhi — A Pocket Friend: Real-time voice translation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # English to Hindi
  python run_sakhi.py --src en --tgt hi
  
  # Auto-detect source language, translate to Tamil
  python run_sakhi.py --src auto --tgt ta
  
  # Use smaller models for low memory
  python run_sakhi.py --src en --tgt kn --whisper-model tiny
  
  # Custom chunk length
  python run_sakhi.py --src en --tgt te --chunk-sec 5

Supported languages: en (English), hi (Hindi), te (Telugu), ta (Tamil), kn (Kannada)
        """
    )
    
    parser.add_argument(
        "--src",
        type=str,
        required=True,
        choices=["en", "hi", "te", "ta", "kn", "auto"],
        help="Source language (use 'auto' for automatic detection)"
    )
    
    parser.add_argument(
        "--tgt",
        type=str,
        required=True,
        choices=["en", "hi", "te", "ta", "kn"],
        help="Target language"
    )
    
    parser.add_argument(
        "--chunk-sec",
        type=float,
        default=3.0,
        help="Audio chunk length in seconds (default: 3.0)"
    )
    
    parser.add_argument(
        "--whisper-model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    
    parser.add_argument(
        "--mbart-model",
        type=str,
        default="facebook/mbart-large-50-many-to-many-mmt",
        help="MBART model name from Hugging Face (default: facebook/mbart-large-50-many-to-many-mmt)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    # Validate arguments
    if args.src == args.tgt:
        print(f"Error: Source and target languages cannot be the same ({args.src})")
        sys.exit(1)
    
    if args.chunk_sec <= 0:
        print(f"Error: Chunk length must be positive (got {args.chunk_sec})")
        sys.exit(1)
    
    # Print welcome message
    print("\n" + "="*60)
    print("🌏 Sakhi — A Pocket Friend")
    print("   Real-time Voice Translation")
    print("="*60)
    print(f"   Source: {args.src.upper()}")
    print(f"   Target: {args.tgt.upper()}")
    print(f"   Chunk: {args.chunk_sec}s")
    print(f"   Whisper: {args.whisper_model}")
    print(f"   MBART: {args.mbart_model}")
    print("="*60 + "\n")
    
    # Check for common issues
    try:
        import sounddevice as sd
        # Test microphone access
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if not input_devices:
            print("⚠️  Warning: No input devices (microphone) detected!")
            print("   Please connect a microphone and try again.\n")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Error checking audio devices: {e}")
        print("   Make sure PortAudio is installed:")
        print("   - Windows: Download from http://www.portaudio.com/")
        print("   - Linux: sudo apt-get install portaudio19-dev")
        print("   - macOS: brew install portaudio\n")
        sys.exit(1)
    
    # Run translator
    try:
        run_realtime_translator(
            src_lang=args.src,
            tgt_lang=args.tgt,
            chunk_seconds=args.chunk_sec,
            whisper_model=args.whisper_model,
            mbart_model=args.mbart_model,
        )
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋\n")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
