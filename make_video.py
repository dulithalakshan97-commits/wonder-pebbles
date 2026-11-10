#!/usr/bin/env python3
"""Generate one Wonder Pebbles episode.

Usage:  python make_video.py [--episode N] [--out out/]
By default it makes the next episode after the last one logged in episodes.csv,
so every run makes a new one (rotating numbers, colors/shapes, ABCs, science).
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image

from wonder import audio, render
from wonder.content import build_episode, CHANNEL
from wonder.icons import sprite, shape_sprite
from wonder.mascot import pebble

LEAD = 0.25  # silence before narration in each segment


def episode_for_today():
    """Next episode = one after the last episode logged in episodes.csv, so every
    run (scheduled or a manual click) makes a new episode."""
    try:
        rows = [l.split(",") for l in open("episodes.csv").read().splitlines()[1:] if l.strip()]
        done = [int(r[1]) for r in rows if len(r) > 1 and r[1].isdigit()]
        if done:
            return max(done) + 1
    except FileNotFoundError:
        pass
    return 0


def build_audio(ep, workdir):
    segs = ep["segs"]
    voices, timeline = [], []
    t = 0.0
    for i, s in enumerate(segs):
        if s["text"]:
            v = audio.tts(s["text"], os.path.join(workdir, f"v{i:03d}.wav"))
        else:
            v = np.zeros(1)
        dur = max(1.2, LEAD + len(v) / audio.SR + s["pause"])
        timeline.append((t, dur, s))
        voices.append((t + LEAD, v))
        t += dur
    total = t
    n = int(total * audio.SR) + audio.SR
    voice = np.zeros(n)
    for start, v in voices:
        i = int(start * audio.SR)
        voice[i:i + len(v)] += v[: n - i]
    # sound effects
    fx = np.zeros(n)
    prev = None

    def add(sound, at):
        i = int(at * audio.SR)
        if i < n:
            fx[i:i + len(sound)] += sound[: n - i]

    for start, dur, s in timeline:
        p = s["params"]
        if s["layout"] != prev and prev is not None:
            add(audio.sfx("whoosh"), start)
        prev = s["layout"]
        if p.get("pop") or s["layout"] in ("object", "word", "title"):
            add(audio.sfx("pop"), start + 0.02)
        if s["layout"] == "fact":
            for k in range(len(p["icons"])):
                add(audio.sfx("pop"), start + 0.35 * k + 0.02)
        if p.get("highlight") and not p.get("pop"):
            add(audio.sfx("tick"), start)
        if p.get("reveal") or p.get("cheer"):
            add(audio.sfx("cheer"), start)
        if s["layout"] == "choose" and not p.get("reveal"):
            for k in range(3):
                add(audio.sfx("tick"), start + dur - 3 + k)
    # music, ducked under the voice
    mus = audio.music(total + 1, seed=ep["seed"])[:n]
    if len(mus) < n:
        mus = np.pad(mus, (0, n - len(mus)))
    act = np.convolve((np.abs(voice) > 0.02).astype(float), np.ones(int(0.3 * audio.SR)) / (0.3 * audio.SR), "same")
    mus *= 1.0 - 0.55 * np.clip(act * 3, 0, 1)
    fade = int(1.5 * audio.SR)
    mus[:fade] *= np.linspace(0, 1, fade)
    end = int(total * audio.SR)
    mus[end - fade:end] *= np.linspace(1, 0, fade)
    mix = voice * 0.95 + mus * 0.55 + fx * 0.6
    peak = np.max(np.abs(mix)) or 1
    mix = mix / peak * 0.89
    mix = mix[:end]
    # per-frame mouth envelope
    spf = audio.SR / render.FPS
    nfr = int(total * render.FPS) + 1
    env = np.array([np.sqrt(np.mean(voice[int(k * spf):int((k + 1) * spf)] ** 2)) if int(k * spf) < n else 0
                    for k in range(nfr)])
    env = env / (np.percentile(env[env > 0], 95) if np.any(env > 0) else 1)
    return timeline, mix, np.clip(env, 0, 1), total


def make_thumbnail(ep, path):
    bg = render.Background(ep["hue"], ep["seed"]).draw(0).resize((1280, 720), Image.LANCZOS)
    th = ep["thumb"]
    if "shape" in th:
        spr = shape_sprite(th["shape"], tuple(th["color"]))
    elif "letter" in th and "icon" in th:
        spr = render.text_sprite(th["letter"], 380, render.PALETTE[ord(th["letter"]) % 8])
    else:
        spr = sprite(th["icon"], tuple(th["tint"]) if th.get("tint") else None)
    render.paste(bg, render.glow(200, (255, 255, 255)), 860, 330)
    render.paste(bg, spr, 860, 330, 440 if spr.width >= 300 else None, rot=-6)
    if "letter" in th and "icon" in th:
        render.paste(bg, sprite(th["icon"]), 1120, 520, 230, rot=8)
    render.paste(bg, pebble(3, False, True), 230, 480, 380, rot=-4)
    txt = render.rainbow_text(th["text"], 130)
    if txt.width > 1180:
        txt = render.resized(txt, 1180)
    render.paste(bg, txt, 640, 640)
    bg.convert("RGB").save(path, quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", type=int, default=None)
    ap.add_argument("--out", default="out")
    ap.add_argument("--preview", type=float, default=0, help="only render the first N seconds (for testing)")
    a = ap.parse_args()
    epn = a.episode if a.episode is not None else int(os.environ.get("EPISODE") or episode_for_today())
    ep = build_episode(epn)
    os.makedirs(a.out, exist_ok=True)
    work = os.path.join(a.out, "work")
    os.makedirs(work, exist_ok=True)
    t0 = time.time()
    print(f"Episode {epn} [{ep['series']}]: {ep['title']}")
    timeline, mix, env, total = build_audio(ep, work)
    print(f"  narration: {len(timeline)} segments, {total:.1f}s, TTS engine={audio.engine_name()}")
    if a.preview:
        cut = [x for x in timeline if x[0] < a.preview]
        timeline = cut
        total = cut[-1][0] + cut[-1][1]
        mix = mix[: int(total * audio.SR)]
    wav = os.path.join(work, "mix.wav")
    audio.write_wav(wav, mix)
    mp4 = os.path.join(a.out, "video.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{render.W}x{render.H}", "-r", str(render.FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", os.environ.get("X264_PRESET", "veryfast"), "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nfr = render.render(ep, timeline, env, mp4, proc)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")
    make_thumbnail(ep, os.path.join(a.out, "thumbnail.jpg"))
    meta = {
        "episode": epn,
        "series": ep["series"],
        "title": ep["title"][:100],
        "description": (
            f"{ep['desc']}\n\n"
            f"{CHANNEL} makes gentle, colourful learning cartoons for toddlers and preschoolers (ages 2-5): "
            "numbers, colors, shapes, the ABCs and simple science, taught by Pebble the friendly pebble.\n\n"
            "Watch together! Pause when Pebble asks a question and let your little one answer.\n\n"
            "#kidslearning #toddlerlearning #preschool #wonderpebbles"
        ),
        "tags": ep["tags"] + ["wonder pebbles", "kids cartoon", "learning for toddlers", "educational video for kids"],
        "duration": round(total, 1),
    }
    with open(os.path.join(a.out, "metadata.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(f"  rendered {nfr} frames in {time.time() - t0:.0f}s -> {mp4}")


if __name__ == "__main__":
    main()
