"""
Podcast Processing Pipeline

Usage:
    from pipeline import Pipeline
    
    p = Pipeline(rss_url="...", episode_query="...")
    result = p.run()
"""
from .fetcher import RSSFetcher, fetch_episode
from .transcriber import transcribe_audio, AliyunTranscriber
from .fixer import fix_transcript, TranscriptFixer
from .exporter import export, SRTExporter
from . import config

__all__ = [
    "Pipeline",
    "RSSFetcher", 
    "fetch_episode",
    "transcribe_audio",
    "AliyunTranscriber",
    "fix_transcript", 
    "TranscriptFixer",
    "export",
    "SRTExporter",
    "config",
]


class Pipeline:
    """
    End-to-end podcast processing pipeline
    
    Usage:
        pipeline = Pipeline(
            rss_url="https://feed.example.com/podcast.xml",
            episode_query="Episode Title",
            transcriber_backend="aliyun",
            fixer_backend="minimax",
        )
        result = pipeline.run()
    """
    
    def __init__(
        self,
        rss_url: str,
        episode_query: str,
        transcriber_backend: str = "aliyun",
        fixer_backend: str = "minimax",
        fixer_api_key: str = None,
        batch_size: int = 50,
        output_dir: str = None,
    ):
        self.rss_url = rss_url
        self.episode_query = episode_query
        self.transcriber_backend = transcriber_backend
        self.fixer_backend = fixer_backend
        self.fixer_api_key = fixer_api_key
        self.batch_size = batch_size
        self.output_dir = Path(output_dir) if output_dir else config.TRANSCRIPT_DIR
        
        # Results
        self.episode = None
        self.audio_path = None
        self.srt_raw_path = None
        self.srt_fixed_path = None
    
    def run(self) -> dict:
        """Run the full pipeline"""
        print(f"🚀 Starting pipeline for: {self.episode_query}")
        print(f"📡 RSS: {self.rss_url}")
        print()
        
        # Step 1: Fetch
        print("=" * 40)
        print("Step 1: Fetching episode...")
        fetch_result = fetch_episode(
            rss_url=self.rss_url,
            query=self.episode_query,
            dest_dir=config.AUDIO_DIR,
        )
        self.episode = fetch_result["episode"]
        self.audio_path = fetch_result["audio_path"]
        print(f"✅ Downloaded: {self.audio_path}")
        print()
        
        # Step 2: Transcribe
        print("=" * 40)
        print("Step 2: Transcribing...")
        self.srt_raw_path = transcribe_audio(
            audio_path=str(self.audio_path),
            backend=self.transcriber_backend,
        )
        print(f"✅ Transcribed: {self.srt_raw_path}")
        print()
        
        # Step 3: Fix
        print("=" * 40)
        print("Step 3: Fixing with LLM...")
        self.srt_fixed_path = fix_transcript(
            srt_path=self.srt_raw_path,
            episode_name=self.episode["title"],
            batch_size=self.batch_size,
            backend=self.fixer_backend,
            api_key=self.fixer_api_key,
        )
        print(f"✅ Fixed: {self.srt_fixed_path}")
        print()
        
        # Step 4: Export
        print("=" * 40)
        print("Step 4: Exporting...")
        text_path = export(self.srt_fixed_path, format="text")
        print(f"✅ Exported text: {text_path}")
        print()
        
        print("=" * 40)
        print("🎉 Pipeline complete!")
        
        return {
            "episode": self.episode,
            "audio_path": self.audio_path,
            "srt_raw": self.srt_raw_path,
            "srt_fixed": self.srt_fixed_path,
            "text": text_path,
        }
