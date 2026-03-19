"""
RSS Fetcher - Fetch podcast metadata and download audio
"""
import re
import urllib.request
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

from . import config


class RSSFetcher:
    """Fetch podcast info and download audio from RSS feed"""
    
    def __init__(self, rss_url: str):
        self.rss_url = rss_url
        self._xml: Optional[str] = None
    
    def fetch(self) -> str:
        """Download and cache RSS XML"""
        if self._xml is None:
            print(f"📥 Fetching RSS feed: {self.rss_url}")
            req = urllib.request.Request(
                self.rss_url, 
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                self._xml = resp.read().decode("utf-8")
        return self._xml
    
    def get_episodes(self) -> list[dict]:
        """Parse RSS and return all episodes"""
        xml = self.fetch()
        root = ET.fromstring(xml)
        
        episodes = []
        for item in root.findall(".//item"):
            title = item.find("title").text or ""
            enclosure = item.find("enclosure")
            audio_url = enclosure.get("url") if enclosure is not None else ""
            guid = item.find("guid").text if item.find("guid") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            
            # Extract description
            desc_elem = item.find("description")
            description = desc_elem.text if desc_elem is not None else ""
            
            # Extract duration
            duration_elem = item.find(".//{http://www.itunes.com/dtds/podcast-1.0.dtd}duration")
            duration = duration_elem.text if duration_elem is not None else ""
            
            episodes.append({
                "title": title,
                "audio_url": audio_url,
                "guid": guid,
                "pub_date": pub_date,
                "description": description,
                "duration": duration,
            })
        
        return episodes
    
    def find_episode(self, query: str) -> Optional[dict]:
        """Find episode by title or GUID"""
        episodes = self.get_episodes()
        query_lower = query.lower()
        
        # Exact GUID match
        for ep in episodes:
            if ep["guid"] == query:
                return ep
        
        # Partial title match
        for ep in episodes:
            if query_lower in ep["title"].lower():
                return ep
        
        return None
    
    def download_audio(self, url: str, dest_path: Path) -> Path:
        """Download audio file to dest_path"""
        print(f"⬇️  Downloading audio to {dest_path}")
        
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=300) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded * 100 // total
                        print(f"\r   {downloaded}/{total} MB ({pct}%)", end="", flush=True)
        
        print()  # newline
        return dest_path


def fetch_episode(rss_url: str, query: str, dest_dir: Path = None) -> dict:
    """
    Convenience function to fetch an episode
    
    Args:
        rss_url: RSS feed URL
        query: Episode title or GUID
        dest_dir: Output directory (default: config.AUDIO_DIR)
    
    Returns:
        dict with keys: episode, audio_path, audio_url
    """
    fetcher = RSSFetcher(rss_url)
    episode = fetcher.find_episode(query)
    
    if not episode:
        raise ValueError(f"Episode not found: {query}")
    
    if dest_dir is None:
        dest_dir = config.AUDIO_DIR
    
    # Sanitize filename
    safe_title = re.sub(r'[^\w\s-]', '', episode["title"])
    safe_title = re.sub(r'\s+', '_', safe_title)[:50]
    audio_path = dest_dir / f"{safe_title}.m4a"
    
    # Download if not exists
    if not audio_path.exists():
        fetcher.download_audio(episode["audio_url"], audio_path)
    
    return {
        "episode": episode,
        "audio_path": audio_path,
        "audio_url": episode["audio_url"],
    }
