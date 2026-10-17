"""Prepare the Motion film for the site's home page (D109).

Takes the MP4 exported from the Motion chat, checks it against the brief
(size, frame rate, length), re-encodes it only when it is over the host's
per-file limit, and writes:

  site/film/opening_<theme>.mp4         the film as served, one per site theme
  site/film/opening_<theme>_poster.jpg  the frame shown before play
  results/film/film_<theme>.json        size, length, encoding and the transcript

The video goes under site/ because Quarto leaves out files linked from
outside it (scripts/check_site.py), as src.banner writes site/preview.png.

The transcript is the brief's card wording (build_motion_handoff.CARDS)
filled from the numbers the film was given, with the lines Motion added on
screen (ADDED) after their cards; the film's own wording is checked against
it by hand before publication (claude-motion-handoff).

ffmpeg comes from the separate conda env `media`, so the project env stays
as environment.yml describes it.

Usage, from the repo root:
    python scripts/prepare_film.py PATH_TO_EXPORT.mp4 --theme dark
    python scripts/prepare_film.py --transcript   (rewrite only the transcripts)
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_dashboard  # noqa: E402
import build_motion_handoff as handoff  # noqa: E402
from deploy_site import FILE_LIMIT_BYTES  # noqa: E402

OUT = ROOT / "results" / "film"
SERVED = ROOT / "site" / "film"
THEMES = ("dark", "light")
BIN = Path.home() / "miniforge3" / "envs" / "media" / "Library" / "bin"
# Room under the host's limit for a re-encode to land in.
TARGET_BYTES = int(FILE_LIMIT_BYTES * 0.9)
# Where the poster frame is taken, in seconds: inside Scene 1, after its
# title has settled (re-check against the film's scene table).
POSTER_AT = 6.0
# On-screen lines Motion added beyond the cards, as (index of the card they
# follow, line). Read off the frames of both exports on 2026-10-17 and
# approved by the owner (DECISIONS 2026-10-14 and 2026-10-17). The
# diagram's and charts' own labels are figure content and stay out.
ADDED = (
    (2, "AK, YT and NorCal are filed separately for not fitting cleanly into either group."),
    (3, "What El Niño does to winter rain. December to February precipitation, as a "
        "share of each region’s average winter. Each row is scaled to its own largest "
        "swing."),
    (4, "Burned area, as a multiple of each region’s typical season, on a log scale. "
        "Each row is scaled to its own largest swing."),
)


def probe(path: Path) -> dict:
    out = subprocess.run([str(BIN / "ffprobe.exe"), "-v", "error", "-print_format", "json",
                          "-show_format", "-show_streams", str(path)],
                         capture_output=True, text=True, check=True)
    info = json.loads(out.stdout)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    num, den = (int(v) for v in video["r_frame_rate"].split("/"))
    return {"bytes": path.stat().st_size, "seconds": round(float(info["format"]["duration"]), 2),
            "width": video["width"], "height": video["height"], "fps": round(num / den, 3),
            "codec": video["codec_name"],
            "audio": any(s["codec_type"] == "audio" for s in info["streams"])}


def problems(info: dict) -> list[str]:
    film = handoff.FILM
    found = []
    if (info["width"], info["height"]) != (film["width"], film["height"]):
        found.append(f"{info['width']} x {info['height']}, brief says "
                     f"{film['width']} x {film['height']}")
    if abs(info["fps"] - film["fps"]) > 0.01:
        found.append(f"{info['fps']} fps, brief says {film['fps']}")
    if info["seconds"] > film["max_seconds"] + 0.5:
        found.append(f"{info['seconds']} s, brief says {film['max_seconds']} s at most")
    return found


def encode(src: Path, dst: Path, seconds: float) -> None:
    """H.264 at a bitrate that lands under TARGET_BYTES, no audio, the
    index at the front so playback starts before the whole file loads."""
    kbps = int(TARGET_BYTES * 8 / seconds / 1000)
    subprocess.run([str(BIN / "ffmpeg.exe"), "-y", "-v", "error", "-i", str(src), "-an",
                    "-c:v", "libx264", "-preset", "slow", "-b:v", f"{kbps}k",
                    "-maxrate", f"{kbps}k", "-bufsize", f"{2 * kbps}k", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(dst)], check=True)


def transcript() -> list[str]:
    data = build_dashboard.payload()
    fill = {**data["counts"], **data["meta"], "title": data["text"]["title"]}
    lines = []
    for index, card in enumerate(handoff.CARDS):
        lines.append(card.format(**fill))
        lines += [line for after, line in ADDED if after == index]
    return lines


def rewrite_transcripts(out: Path = OUT) -> list[Path]:
    """Replace the transcript in each existing record, leaving the rest as
    written when the film was prepared."""
    done = []
    for theme in THEMES:
        path = out / f"film_{theme}.json"
        if not path.exists():
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        record["transcript"] = transcript()
        path.write_bytes(json.dumps(record, ensure_ascii=False, indent=1).encode("utf-8"))
        done.append(path)
    return done


def build(src: Path, theme: str, out: Path = OUT, served: Path = SERVED) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    served.mkdir(parents=True, exist_ok=True)
    given = probe(src)
    found = problems(given)
    dst = served / f"opening_{theme}.mp4"
    poster = served / f"opening_{theme}_poster.jpg"
    reencoded = given["bytes"] > TARGET_BYTES or given["audio"]
    if reencoded:
        encode(src, dst, given["seconds"])
    else:
        shutil.copyfile(src, dst)
    subprocess.run([str(BIN / "ffmpeg.exe"), "-y", "-v", "error", "-ss", str(POSTER_AT),
                    "-i", str(dst), "-frames:v", "1", "-q:v", "3", str(poster)], check=True)
    record = {"source": src.name, "given": given, "served": probe(dst), "reencoded": reencoded,
              "problems": found, "poster_at_seconds": POSTER_AT, "transcript": transcript()}
    (out / f"film_{theme}.json").write_bytes(json.dumps(record, ensure_ascii=False, indent=1)
                                    .encode("utf-8"))
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("src", type=Path, nargs="?")
    parser.add_argument("--theme", choices=THEMES)
    parser.add_argument("--transcript", action="store_true",
                        help="rewrite only the transcripts of the existing records")
    args = parser.parse_args()
    if args.transcript:
        for path in rewrite_transcripts():
            print(path.relative_to(ROOT))
        return
    if args.src is None or args.theme is None:
        parser.error("give the export and --theme, or --transcript")
    record = build(args.src, args.theme)
    print(json.dumps({k: record[k] for k in ("given", "served", "reencoded", "problems")},
                     indent=1))


if __name__ == "__main__":
    main()
