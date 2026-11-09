"""EPISODEline — Run the full animation pipeline."""
import argparse
import asyncio
import logging
import sys

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

from episodeline.character_library import CharacterFolderError
from episodeline.pipeline import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-22s │ %(message)s",
    datefmt="%H:%M:%S",
)

DEFAULT_IDEA = "The Iggies race to fix the stage before the Iggy Junior High talent show"


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EPISODEline animation pipeline.")
    parser.add_argument("idea", nargs="?", default=DEFAULT_IDEA, help="one-line idea for the episode")
    parser.add_argument("--characters-dir", help="folder of per-character design folders")
    parser.add_argument("--out", help="where to write run artifacts")
    parser.add_argument(
        "--images",
        choices=("local", "pollinations"),
        help="local procedural frames (default) or free AI frames (1 image/45s)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="no network: built-in script, local placeholder frames, procedural music",
    )
    args = parser.parse_args()

    pipeline = Pipeline(
        characters_dir=args.characters_dir,
        output_dir=args.out,
        offline=args.offline,
        images_provider=args.images,
    )

    try:
        episode = await pipeline.run(args.idea)
    except CharacterFolderError as exc:
        print(f"\n❌ Character folder problem: {exc}", file=sys.stderr)
        print("   Fix the file, or delete the folder to have it regenerated.", file=sys.stderr)
        return 1

    print("\n" + "=" * 60)
    print(f"🎬  {episode.title}")
    print(f"⏱   {episode.runtime_sec:.1f}s")
    print(f"🗂   {', '.join(episode.metadata['characters']) or '(none)'}")
    print(f"🎞   {episode.video_path or 'not rendered'}")
    print(f"🖼   {episode.thumbnail_path or 'no thumbnail'}")
    print(f"🆓  {', '.join(f'{k}={v}' for k, v in episode.metadata['providers'].items())}")
    print(f"📁  {episode.metadata['run_dir']}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
