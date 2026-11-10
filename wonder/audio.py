"""Voice (TTS), background music and sound effects. Everything is generated or
synthesised here, so there are no copyright issues."""
import asyncio
import os
import shutil
import subprocess
import wave

import numpy as np

SR = 24000
VOICE = os.environ.get("WP_VOICE", "en-US-AnaNeural")  # a friendly child voice
RATE = os.environ.get("WP_RATE", "-8%")                 # a bit slower for toddlers


def _read_wav(path):
    with wave.open(path, "rb") as w:
        n = w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
        if w.getnchannels() == 2:
            data = data.reshape(-1, 2).mean(axis=1)
        sr = w.getframerate()
    if sr != SR:
        idx = np.linspace(0, len(data) - 1, int(len(data) * SR / sr))
        data = np.interp(idx, np.arange(len(data)), data)
    return data


def _to_wav(src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(SR), dst], check=True)


def _edge(text, mp3):
    import edge_tts

    async def run():
        await edge_tts.Communicate(text, VOICE, rate=RATE, pitch="+4Hz").save(mp3)
    asyncio.run(run())


def _espeak(text, wav):
    subprocess.run(["espeak-ng", "-v", "en-us+f3", "-s", "135", "-p", "65", "-w", wav, text], check=True)


_engine = None


def tts(text, out_wav):
    """Synthesise `text` into a mono wav. Returns samples (float32, SR)."""
    global _engine
    tmp = out_wav + ".src"
    if _engine in (None, "edge"):
        try:
            _edge(text, tmp + ".mp3")
            _to_wav(tmp + ".mp3", out_wav)
            _engine = "edge"
            return _trim(_read_wav(out_wav))
        except Exception as e:  # network blocked, etc.
            if _engine == "edge":
                raise
            print(f"[tts] edge-tts unavailable ({type(e).__name__}); falling back to espeak-ng")
            _engine = "espeak"
    if not shutil.which("espeak-ng"):
        raise RuntimeError("No TTS engine available (install edge-tts or espeak-ng)")
    _espeak(text, tmp + ".wav")
    _to_wav(tmp + ".wav", out_wav)
    return _trim(_read_wav(out_wav))


def _trim(x, thr=0.01):
    nz = np.where(np.abs(x) > thr)[0]
    if len(nz) == 0:
        return x
    a = max(0, nz[0] - int(0.03 * SR))
    b = min(len(x), nz[-1] + int(0.08 * SR))
    return x[a:b]


def engine_name():
    return _engine


# ------------------------------------------------------------------ music & sfx
def _env(n, a=0.01, r=0.3):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def _tone(freq, dur, kind="sine", vol=1.0, a=0.01, r=0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * freq * t
    if kind == "tri":
        y = 2 / np.pi * np.arcsin(np.sin(ph))
    elif kind == "bell":
        y = np.sin(ph) * 0.7 + 0.3 * np.sin(2 * ph) * np.exp(-t * 6)
        y *= np.exp(-t * 3)
    else:
        y = np.sin(ph)
    return y * _env(n, a, r) * vol


def note_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music(duration, seed=0):
    """Gentle looping lullaby-style background music (C major pentatonic)."""
    rng = np.random.default_rng(seed)
    bpm = 96
    beat = 60 / bpm
    n = int(duration * SR) + SR
    out = np.zeros(n)
    prog = [[48, 52, 55], [45, 48, 52], [41, 45, 48], [43, 47, 50]]  # C Am F G
    penta = [60, 62, 64, 67, 69, 72, 74, 76]
    # pre-compose a 4-bar melody and repeat it, so it feels like a tune
    melody = []
    for bar in range(4):
        for step in range(8):
            if rng.random() < 0.72:
                melody.append((bar * 8 + step, rng.choice(penta), rng.choice([1, 1, 2])))
    t = 0.0
    loop = 0
    while t < duration + 1:
        for bar, chord in enumerate(prog):
            start = t + bar * 4 * beat
            for m in chord:
                y = _tone(note_hz(m), 4 * beat, "sine", 0.07, a=0.4, r=1.2)
                i = int(start * SR)
                out[i:i + len(y)] += y[: max(0, n - i)]
            y = _tone(note_hz(chord[0] - 12), 4 * beat, "tri", 0.08, a=0.05, r=1.0)
            i = int(start * SR)
            out[i:i + len(y)] += y[: max(0, n - i)]
        for step, m, ln in melody:
            if loop % 2 == 1 and step % 8 == 0:
                m += 2 if m < 74 else -3
            y = _tone(note_hz(m), ln * beat / 2 + 0.2, "bell", 0.13, a=0.005, r=0.25)
            i = int((t + step * beat / 2) * SR)
            out[i:i + len(y)] += y[: max(0, n - i)]
        t += 16 * beat
        loop += 1
    return out[: int(duration * SR)]


def sfx(name):
    if name == "pop":
        n = int(0.12 * SR)
        t = np.arange(n) / SR
        f = 500 + 900 * (t / t[-1])
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * 0.35
    if name == "ding":
        return (_tone(note_hz(84), 0.8, "bell", 0.35) + _tone(note_hz(88), 0.8, "bell", 0.25)) * 0.8
    if name == "cheer":
        y = np.zeros(int(0.9 * SR))
        for k, m in enumerate([72, 76, 79, 84]):
            s = _tone(note_hz(m), 0.35, "bell", 0.3)
            i = int(k * 0.12 * SR)
            y[i:i + len(s)] += s[: len(y) - i]
        return y
    if name == "whoosh":
        n = int(0.4 * SR)
        noise = np.random.default_rng(1).standard_normal(n)
        k = np.ones(40) / 40
        y = np.convolve(noise, k, mode="same")
        return y * np.sin(np.linspace(0, np.pi, n)) * 0.25
    if name == "tick":
        return _tone(1800, 0.05, "sine", 0.15, a=0.001, r=0.04)
    return np.zeros(1)


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
