"""
Exporter - Export transcripts to various formats
"""
import re
from pathlib import Path
from typing import Optional


class SRTExporter:
    """Export SRT to various formats"""
    
    def __init__(self, srt_path: str):
        self.srt_path = Path(srt_path)
        if not self.srt_path.exists():
            raise FileNotFoundError(f"SRT not found: {srt_path}")
        
        self._segments = None
    
    @property
    def segments(self) -> list[dict]:
        """Parse SRT segments"""
        if self._segments is None:
            self._segments = self._parse_srt()
        return self._segments
    
    def _parse_srt(self) -> list[dict]:
        """Parse SRT file into segments"""
        segments = []
        current = {}
        
        with open(self.srt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split by double newline
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            # Parse index
            try:
                idx = int(lines[0])
            except ValueError:
                continue
            
            # Parse timestamp
            timestamp = lines[1]
            if '-->' not in timestamp:
                continue
            
            start, end = timestamp.split('-->')
            start = start.strip()
            end = end.strip()
            
            # Text is remaining lines
            text = '\n'.join(lines[2:])
            
            segments.append({
                "index": idx,
                "start": start,
                "end": end,
                "text": text,
            })
        
        return segments
    
    def to_text(self) -> str:
        """Export as plain text (no timestamps)"""
        lines = [seg["text"] for seg in self.segments]
        return "\n\n".join(lines)
    
    def to_text_with_timestamps(self) -> str:
        """Export as text with timestamps"""
        lines = []
        for seg in self.segments:
            lines.append(f"[{seg['start']}] {seg['text']}")
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """Export as JSON"""
        import json
        return json.dumps(self.segments, ensure_ascii=False, indent=2)
    
    def save_text(self, output_path: str = None) -> str:
        """Save as plain text"""
        if output_path is None:
            output_path = self.srt_path.with_suffix(".txt")
        
        text = self.to_text()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        return str(output_path)
    
    def save_text_with_timestamps(self, output_path: str = None) -> str:
        """Save as text with timestamps"""
        if output_path is None:
            output_path = self.srt_path.with_suffix("_with_time.txt")
        
        text = self.to_text_with_timestamps()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        return str(output_path)


def export(
    srt_path: str,
    format: str = "text",
    output_path: str = None,
) -> str:
    """
    Convenience function to export SRT
    
    Args:
        srt_path: Path to SRT file
        format: "text", "text_with_timestamps", or "json"
        output_path: Output path (optional)
    
    Returns:
        Path to exported file
    """
    exporter = SRTExporter(srt_path)
    
    if format == "text":
        return exporter.save_text(output_path)
    elif format == "text_with_timestamps":
        return exporter.save_text_with_timestamps(output_path)
    elif format == "json":
        if output_path is None:
            output_path = srt_path.replace(".srt", ".json")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(exporter.to_json())
        return output_path
    else:
        raise ValueError(f"Unknown format: {format}")
