#!/usr/bin/env python3
"""
播客知识库检索工具

Usage:
  python tools/search.py list                        列出所有已整理集
  python tools/search.py search --tag topic:ai       按标签检索
  python tools/search.py search --person li-jigang   按人物检索
  python tools/search.py search --text "心力"        全文检索
  python tools/search.py show wrzx-e45               显示单集详情
  python tools/search.py people                      列出所有人物
  python tools/search.py tags                        显示标签统计
"""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("缺少依赖，请先运行: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
EPISODES_DIR = ROOT / "podcasts"


# ── 数据模型 ────────────────────────────────────────────────────────────────

@dataclass
class Episode:
    id: str
    podcast_id: str
    episode_number: int
    title: str
    air_date: str
    duration_seconds: int
    host_ids: list
    guest_ids: list
    tags: list
    summary: str
    key_concepts: list
    status: str
    quality: dict
    file_path: Path
    body: str = ""

    def duration_str(self) -> str:
        if not self.duration_seconds:
            return "未知"
        h = self.duration_seconds // 3600
        m = (self.duration_seconds % 3600) // 60
        return f"{h}h{m:02d}m" if h else f"{m}m"

    def tag_values(self, namespace: str) -> list:
        prefix = f"{namespace}:"
        return [t[len(prefix):] for t in self.tags if t.startswith(prefix)]

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


@dataclass
class Person:
    id: str
    name: str
    aliases: list
    bio: str
    affiliations: list
    tags: list

    def field_values(self) -> list:
        return [t[len("field:"):] for t in self.tags if t.startswith("field:")]


@dataclass
class Podcast:
    id: str
    name: str
    description: str
    host_ids: list
    total_episodes: int
    status: str
    tags: list


# ── 数据加载 ────────────────────────────────────────────────────────────────

class DataLoader:
    def __init__(self, root: Path):
        self.root = root

    def load_all(self):
        podcasts = self._load_podcasts()
        people = self._load_people()
        episodes = self._load_episodes()
        return podcasts, people, episodes

    def _load_podcasts(self) -> dict:
        result = {}
        podcast_dir = DATA_DIR / "podcasts"
        if not podcast_dir.exists():
            return result
        for f in podcast_dir.glob("*.yaml"):
            with open(f, encoding="utf-8") as fp:
                data = yaml.safe_load(fp)
            if data and "id" in data:
                result[data["id"]] = Podcast(
                    id=data.get("id", ""),
                    name=data.get("name", ""),
                    description=data.get("description", ""),
                    host_ids=data.get("host_ids", []),
                    total_episodes=data.get("total_episodes", 0),
                    status=data.get("status", ""),
                    tags=data.get("tags", []),
                )
        return result

    def _load_people(self) -> dict:
        result = {}
        people_dir = DATA_DIR / "people"
        if not people_dir.exists():
            return result
        for f in people_dir.glob("*.yaml"):
            with open(f, encoding="utf-8") as fp:
                data = yaml.safe_load(fp)
            if data and "id" in data:
                result[data["id"]] = Person(
                    id=data.get("id", ""),
                    name=data.get("name", ""),
                    aliases=data.get("aliases", []),
                    bio=data.get("bio", ""),
                    affiliations=data.get("affiliations", []),
                    tags=data.get("tags", []),
                )
        return result

    def _load_episodes(self) -> list:
        result = []
        for md_file in EPISODES_DIR.rglob("*.md"):
            if md_file.name == "README.md":
                continue
            episode = self._parse_episode_file(md_file)
            if episode:
                result.append(episode)
        return sorted(result, key=lambda e: e.episode_number)

    def _parse_episode_file(self, path: Path) -> Optional[Episode]:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        try:
            data = yaml.safe_load(parts[1])
        except yaml.YAMLError:
            return None

        if not data or "id" not in data:
            return None

        quality = data.get("quality", {})
        return Episode(
            id=data.get("id", ""),
            podcast_id=data.get("podcast_id", ""),
            episode_number=data.get("episode_number", 0),
            title=data.get("title", ""),
            air_date=str(data.get("air_date", "")),
            duration_seconds=data.get("duration_seconds", 0),
            host_ids=data.get("host_ids", []),
            guest_ids=data.get("guest_ids", []),
            tags=data.get("tags", []),
            summary=data.get("summary", ""),
            key_concepts=data.get("key_concepts", []),
            status=data.get("status", ""),
            quality=quality if isinstance(quality, dict) else {},
            file_path=path,
            body=parts[2].strip(),
        )


# ── 检索引擎 ────────────────────────────────────────────────────────────────

class QueryEngine:
    def __init__(self, podcasts, people, episodes):
        self.podcasts = podcasts
        self.people = people
        self.episodes = episodes

    def filter(self,
               tags=None,
               person_id=None,
               podcast_id=None,
               text=None,
               status=None) -> list:
        results = self.episodes[:]

        if podcast_id:
            results = [e for e in results if e.podcast_id == podcast_id]

        if tags:
            for tag in tags:
                results = [e for e in results if e.has_tag(tag)]

        if person_id:
            results = [e for e in results
                       if person_id in e.host_ids or person_id in e.guest_ids]

        if status:
            results = [e for e in results if e.status == status]

        if text:
            tl = text.lower()
            results = [e for e in results
                       if tl in e.title.lower()
                       or tl in e.summary.lower()
                       or any(tl in c.lower() for c in e.key_concepts)
                       or tl in e.body.lower()]

        return results

    def resolve_person(self, query: str) -> Optional[str]:
        """按 ID、姓名或别名查找人物，返回 ID"""
        if query in self.people:
            return query
        for p in self.people.values():
            if p.name == query or query in p.aliases:
                return p.id
        return None


# ── CLI ─────────────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
DIM    = "\033[2m"


def c(text, color): return f"{color}{text}{RESET}"


class CLI:
    def __init__(self):
        loader = DataLoader(ROOT)
        self.podcasts, self.people, self.episodes = loader.load_all()
        self.engine = QueryEngine(self.podcasts, self.people, self.episodes)

    def run(self):
        parser = argparse.ArgumentParser(
            prog="search",
            description="播客知识库检索工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__doc__,
        )
        sub = parser.add_subparsers(dest="command")

        # list
        p_list = sub.add_parser("list", help="列出已整理集数")
        p_list.add_argument("--podcast", help="限定播客 ID")
        p_list.add_argument("--status", help="按状态过滤 (completed/draft)")

        # search
        p_search = sub.add_parser("search", help="多条件检索")
        p_search.add_argument("--tag", "-t", action="append",
                              help="按标签 (可多次: -t topic:ai -t mood:reflective)")
        p_search.add_argument("--person", "-p",
                              help="按人物 (ID 或姓名)")
        p_search.add_argument("--text", help="全文检索")
        p_search.add_argument("--podcast", help="限定播客 ID")

        # show
        p_show = sub.add_parser("show", help="显示单集详情")
        p_show.add_argument("episode", help="集 ID 或集数 (如 wrzx-e45 或 45)")

        # people
        sub.add_parser("people", help="列出所有人物")

        # tags
        sub.add_parser("tags", help="显示标签统计")

        args = parser.parse_args()
        if not args.command:
            parser.print_help()
            return

        getattr(self, f"cmd_{args.command}")(args)

    # ── 命令实现 ──────────────────────────────────────────────────────────────

    def cmd_list(self, args):
        episodes = self.engine.filter(
            podcast_id=getattr(args, "podcast", None),
            status=getattr(args, "status", None),
        )
        print(f"\n{c('已整理集数', BOLD)} ({len(episodes)} 集)\n")
        self._print_table(episodes)

    def cmd_search(self, args):
        person_id = None
        if args.person:
            person_id = self.engine.resolve_person(args.person)
            if not person_id:
                print(f"未找到人物: {args.person}")
                print("提示: 运行 'python tools/search.py people' 查看所有人物 ID")
                return

        episodes = self.engine.filter(
            tags=args.tag,
            person_id=person_id,
            text=args.text,
            podcast_id=getattr(args, "podcast", None),
        )

        if not episodes:
            print("未找到匹配结果")
            return

        filters = []
        if args.tag:
            filters.extend([f"标签={t}" for t in args.tag])
        if args.person:
            filters.append(f"人物={args.person}")
        if args.text:
            filters.append(f"全文=\"{args.text}\"")

        print(f"\n{c('检索结果', BOLD)}: {', '.join(filters) if filters else '全部'}")
        print(f"找到 {c(len(episodes), GREEN)} 集\n")
        self._print_table(episodes)

    def cmd_show(self, args):
        target = args.episode
        for e in self.episodes:
            if e.id == target or str(e.episode_number) == target:
                self._print_detail(e)
                return
        print(f"未找到集: {target}")

    def cmd_people(self, args):
        if not self.people:
            print("未找到人物数据（检查 data/people/ 目录）")
            return

        print(f"\n{c('人物列表', BOLD)} ({len(self.people)} 人)\n")
        print(f"{'ID':<20} {'姓名':<8} {'领域':<25} 简介")
        print(c("─" * 75, DIM))
        for p in sorted(self.people.values(), key=lambda x: x.id):
            fields = ", ".join(p.field_values()) or "-"
            bio_short = p.bio[:28] + ("…" if len(p.bio) > 28 else "")
            print(f"{c(p.id, CYAN):<29} {p.name:<8} {fields:<25} {bio_short}")

    def cmd_tags(self, args):
        all_tags: set = set()
        for e in self.episodes:
            all_tags.update(e.tags)

        ns_map: dict = {}
        for tag in sorted(all_tags):
            if ":" in tag:
                ns, val = tag.split(":", 1)
                ns_map.setdefault(ns, []).append(val)

        print(f"\n{c('标签统计', BOLD)} (共 {len(all_tags)} 个标签，来自 {len(self.episodes)} 集)\n")
        for ns in sorted(ns_map):
            print(f"{c(ns + ':', YELLOW)}")
            for val in sorted(ns_map[ns]):
                count = sum(1 for e in self.episodes if f"{ns}:{val}" in e.tags)
                bar = "█" * count
                print(f"  {val:<25} {c(bar, GREEN)} {count}")
            print()

    # ── 渲染工具 ──────────────────────────────────────────────────────────────

    def _person_name(self, pid: str) -> str:
        p = self.people.get(pid)
        return p.name if p else pid

    def _print_table(self, episodes: list):
        if not episodes:
            print(c("  (无)", DIM))
            return
        print(f"{'#':<5} {'标题':<32} {'嘉宾':<10} {'日期':<12} 话题标签")
        print(c("─" * 75, DIM))
        for e in episodes:
            guests = [self._person_name(g) for g in e.guest_ids]
            guest_str = (", ".join(guests) or "-")[:10]
            topics = ", ".join(e.tag_values("topic"))[:22]
            num = c(f"E{e.episode_number}", CYAN)
            print(f"{num:<14} {e.title[:30]:<32} {guest_str:<10} "
                  f"{e.air_date:<12} {c(topics, DIM)}")
        print()

    def _print_detail(self, e: Episode):
        sep = c("═" * 60, CYAN)
        print(f"\n{sep}")
        print(f"{c(f'E{e.episode_number}', CYAN)}  {c(e.title, BOLD)}")
        print(sep)

        hosts = [self._person_name(h) for h in e.host_ids]
        guests = [self._person_name(g) for g in e.guest_ids]
        print(f"  播客   {self.podcasts.get(e.podcast_id, type('P',(),{'name':e.podcast_id})()).name}")
        print(f"  主播   {', '.join(hosts)}")
        print(f"  嘉宾   {', '.join(guests)}")
        print(f"  日期   {e.air_date}   时长 {e.duration_str()}")
        print(f"  状态   {e.status}")

        if e.summary:
            print(f"\n{c('摘要', BOLD)}")
            print(f"  {e.summary}")

        if e.key_concepts:
            print(f"\n{c('关键概念', BOLD)}")
            print(f"  {' · '.join(e.key_concepts)}")

        if e.tags:
            print(f"\n{c('标签', BOLD)}")
            ns_map: dict = {}
            for tag in e.tags:
                ns, val = tag.split(":", 1) if ":" in tag else ("other", tag)
                ns_map.setdefault(ns, []).append(val)
            for ns, vals in sorted(ns_map.items()):
                print(f"  {c(ns, YELLOW)}: {', '.join(vals)}")

        quality = e.quality
        if quality:
            flags = [k.replace("has_", "") for k, v in quality.items() if v]
            missing = [k.replace("has_", "") for k, v in quality.items() if not v]
            if flags:
                print(f"\n  {c('✓', GREEN)} 含 {', '.join(flags)}", end="")
            if missing:
                print(f"   {c('✗', DIM)} 缺 {', '.join(missing)}", end="")
            print()

        print(f"\n  {c('文件', DIM)}: {e.file_path.relative_to(ROOT)}")
        print()


if __name__ == "__main__":
    CLI().run()
