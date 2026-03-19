"""
Transcriber - Audio to text using ASR services
"""
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Optional

from . import config


class AliyunTranscriber:
    """Transcribe audio using Aliyun Paraformer"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.DASHSCOPE_API_KEY
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY is required")
    
    def transcribe(
        self, 
        audio_path: Path, 
        language: str = "zh",
        format: str = "m4a"
    ) -> Path:
        """
        Transcribe audio file and return SRT path
        
        Args:
            audio_path: Path to audio file
            language: Language code (zh, en, etc.)
            format: Audio format
        
        Returns:
            Path to generated SRT file
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Determine output path
        srt_path = audio_path.with_suffix(".srt")
        
        print(f"⏱️  Duration: {self._get_duration(audio_path)}")
        print(f"🔧 Backend: Aliyun Paraformer (¥0.288/hour)")
        
        # Submit transcription task
        task_id = self._submit_task(audio_path, language, format)
        print(f"🚀 Submitting to Aliyun Paraformer...")
        print(f"📋 Task submitted: {task_id}")
        
        # Poll for result
        result = self._wait_for_result(task_id)
        
        # Parse and save SRT
        self._save_srt(result, srt_path)
        
        print(f"💾 Saved to {srt_path}")
        return srt_path
    
    def _get_duration(self, audio_path: Path) -> str:
        """Get audio duration (simplified)"""
        # Could use ffprobe here
        return "~"
    
    def _submit_task(self, audio_path: Path, language: str, format: str) -> str:
        """Submit transcription task to Aliyun"""
        # Read audio file
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        # Upload to Aliyun
        url = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
        
        # Create multipart form data
        import base64
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")
        
        # For large files, we need to upload first
        # This is a simplified version - in production use their SDK
        raise NotImplementedError("Use transcribe.py CLI for now")
    
    def _wait_for_result(self, task_id: str) -> dict:
        """Wait for transcription to complete"""
        # Simplified - would need actual polling
        raise NotImplementedError()
    
    def _save_srt(self, result: dict, srt_path: Path):
        """Save transcription result to SRT"""
        raise NotImplementedError()


def transcribe_audio(
    audio_path: str, 
    backend: str = "aliyun",
    api_key: str = None,
    language: str = "zh"
) -> str:
    """
    Convenience function to transcribe audio
    
    Args:
        audio_path: Path to audio file
        backend: "aliyun" or "openai"
        api_key: API key (optional, will use env)
        language: Language code
    
    Returns:
        Path to generated SRT file
    """
    audio_path = Path(audio_path)
    
    if backend == "aliyun":
        # Use the existing CLI
        import subprocess
        
        env = os.environ.copy()
        if api_key:
            env["DASHSCOPE_API_KEY"] = api_key
        
        cmd = [
            "python3", 
            str(config.ROOT / "tools" / "transcribe.py"),
            "--file", str(audio_path),
            "--backend", "aliyun",
            "--out", str(audio_path.with_suffix(".srt"))
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Transcription failed: {result.stderr}")
        
        return str(audio_path.with_suffix(".srt"))
    
    else:
        raise ValueError(f"Unsupported backend: {backend}")
