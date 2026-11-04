"""Rebuild using bundled audio utilities, without TTS or the original skill checkout."""
import argparse
from pathlib import Path
from scene import run
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['stills','animatic','pilot','draft','final'],default='final')
    args=parser.parse_args()
    run(args.mode,Path(__file__).resolve().parent/'runtime')
