#!/usr/bin/env python3
"""
Run episode through the pipeline

Usage:
    python run_episode.py --rss <url> --query <episode>
    python run_episode.py --rss <url> --guid <episode_guid>
    
Examples:
    python run_episode.py --rss https://feed.xyzfm.space/xxx --query "姜思达"
    python run_episode.py --rss https://feed.xyzfm.space/xxx --guid 69a67f78de29766da93b3617
"""
import argparse
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import Pipeline, config


def main():
    parser = argparse.ArgumentParser(description="Process podcast episode")
    
    parser.add_argument("--rss", required=True, help="RSS feed URL")
    parser.add_argument("--query", help="Episode title to search for")
    parser.add_argument("--guid", help="Episode GUID")
    parser.add_argument("--transcriber", default="aliyun", help="Transcriber backend")
    parser.add_argument("--fixer", default="minimax", help="Fixer backend")
    parser.add_argument("--fixer-key", help="API key for fixer")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for fixing")
    parser.add_argument("--export-format", default="text", 
                        choices=["text", "text_with_timestamps", "json"],
                        help="Export format")
    
    args = parser.parse_args()
    
    # Determine episode query
    episode_query = args.query or args.guid
    if not episode_query:
        parser.error("Either --query or --guid is required")
    
    # Set API keys from environment if not provided
    fixer_key = args.fixer_key or os.environ.get("MINIMAX_API_KEY")
    
    # Create and run pipeline
    pipeline = Pipeline(
        rss_url=args.rss,
        episode_query=episode_query,
        transcriber_backend=args.transcriber,
        fixer_backend=args.fixer,
        fixer_api_key=fixer_key,
        batch_size=args.batch_size,
    )
    
    result = pipeline.run()
    
    # Export additional formats
    from pipeline.exporter import export
    if args.export_format == "text_with_timestamps":
        export(result["srt_fixed"], format="text_with_timestamps")
    elif args.export_format == "json":
        export(result["srt_fixed"], format="json")
    
    print(f"\n📁 Results:")
    print(f"   Audio:    {result['audio_path']}")
    print(f"   SRT Raw:  {result['srt_raw']}")
    print(f"   SRT Fix:  {result['srt_fixed']}")
    print(f"   Text:     {result['text']}")


if __name__ == "__main__":
    main()
