"""
Fixer - Fix ASR transcript errors using LLM
"""
import os
import subprocess
from pathlib import Path
from typing import Optional

from . import config


def fix_transcript(
    srt_path: str,
    episode_name: str = None,
    show_notes: str = None,
    batch_size: int = 50,
    backend: str = "minimax",
    api_key: str = None,
    output_path: str = None,
) -> str:
    """
    Fix ASR transcript using LLM
    
    Args:
        srt_path: Path to input SRT file
        episode_name: Episode identifier
        show_notes: Show notes for context
        batch_size: Segments per batch
        backend: LLM backend (minimax, qwen)
        api_key: API key (optional)
        output_path: Output path (optional)
    
    Returns:
        Path to fixed SRT file
    """
    srt_path = Path(srt_path)
    
    if output_path is None:
        output_path = srt_path.with_name(srt_path.stem + "_fixed.srt")
    else:
        output_path = Path(output_path)
    
    # Build command
    cmd = [
        "python3",
        str(config.ROOT / "tools" / "fix_transcript.py"),
        "--srt", str(srt_path),
        "--episode", episode_name or srt_path.stem,
        "--out", str(output_path),
        "--backend", backend,
        "--batch-size", str(batch_size),
    ]
    
    # Set API key in environment
    env = os.environ.copy()
    if api_key:
        if backend == "minimax":
            env["MINIMAX_API_KEY"] = api_key
        elif backend == "qwen":
            env["DASHSCOPE_API_KEY"] = api_key
    
    # Run fix
    print(f"🔧 Running LLM fix on {srt_path}")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"STDERR: {result.stderr}")
        raise RuntimeError(f"Fix failed: {result.stderr}")
    
    # Print summary
    for line in result.stdout.split("\n"):
        if "Total:" in line or "fixes" in line.lower():
            print(f"  {line.strip()}")
    
    return str(output_path)


class TranscriptFixer:
    """Class-based interface for transcript fixing"""
    
    def __init__(
        self,
        backend: str = "minimax",
        api_key: str = None,
        batch_size: int = 50,
    ):
        self.backend = backend
        self.api_key = api_key or config.MINIMAX_API_KEY
        self.batch_size = batch_size
    
    def fix(
        self,
        srt_path: str,
        episode_name: str = None,
        show_notes: str = None,
        output_path: str = None,
    ) -> str:
        """Fix a transcript file"""
        return fix_transcript(
            srt_path=srt_path,
            episode_name=episode_name,
            show_notes=show_notes,
            batch_size=self.batch_size,
            backend=self.backend,
            api_key=self.api_key,
            output_path=output_path,
        )
