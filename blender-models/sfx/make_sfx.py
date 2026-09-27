"""
Synthesize the game's sound effects (no samples, all procedural) and write them
as .ogg (upload these to Roblox) plus .mp3 copies.

    python3 sfx/make_sfx.py         -> sfx/out/*.ogg, *.mp3, sfx_report.txt

Loops are made seamless by crossfading the tail into the head.
"""

import os

import lameenc
import numpy as np
import soundfile as sf
from scipy import signal

SR = 44100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
rng = np.random.default_rng(7)


# ------------------------------------------------------------- helpers ----

def t_axis(dur):
    return np.arange(int(SR * dur)) / SR


def noise(dur):
    return rng.standard_normal(int(SR * dur))


def pink(dur):
    """1/f-ish noise via filtering white noise."""
    w = noise(dur)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w)


def band(x, lo, hi, order=4):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lowpass(x, f, order=4):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def highpass(x, f, order=4):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def sweep_band(x, f0, f1, q=4.0, steps=64):
    """Band-pass whose centre moves from f0 to f1 (log) over the sound."""
    out = np.zeros_like(x)
    n = len(x)
    edges = np.linspace(0, n, steps + 1).astype(int)
    win = np.hanning(2 * (edges[1] - edges[0]) + 2)
    for k in range(steps):
        fc = f0 * (f1 / f0) ** (k / max(1, steps - 1))
        lo, hi = fc / (1 + 1 / q), min(fc * (1 + 1 / q), SR / 2 - 100)
        a, b = max(0, edges[k] - (edges[1] - edges[0])), min(n, edges[k + 1] + (edges[1] - edges[0]))
        seg = band(x[a:b], lo, hi, order=2)
        w = np.hanning(len(seg))
        out[a:b] += seg * w
    return out


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    sus = max(0, n - a - d - r)
    e = np.concatenate([np.linspace(0, 1, a, endpoint=False), np.linspace(1, s, d, endpoint=False),
                        np.full(sus, s), np.linspace(s, 0, r)])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def exp_decay(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def make_loop(x, fade=0.25):
    """Crossfade the end into the start so the sound loops without a click."""
    f = int(fade * SR)
    head, body, tail = x[:f], x[f:-f], x[-f:]
    ramp = np.linspace(0, 1, f)
    return np.concatenate([tail * (1 - ramp) + head * ramp, body])


def normalize(x, peak_db=-1.0):
    p = np.max(np.abs(x)) or 1
    return x / p * 10 ** (peak_db / 20)


def fade_edges(x, fin=0.003, fout=0.02):
    a, b = int(fin * SR), int(fout * SR)
    x = x.copy()
    x[:a] *= np.linspace(0, 1, a)
    x[-b:] *= np.linspace(1, 0, b)
    return x


def write(name, x, loop=False, peak_db=-1.0):
    os.makedirs(OUT, exist_ok=True)
    x = normalize(x, peak_db)
    if not loop:
        x = fade_edges(x)
    sf.write(os.path.join(OUT, name + ".ogg"), x.astype(np.float32), SR, format="OGG", subtype="VORBIS")
    enc = lameenc.Encoder()
    enc.set_bit_rate(160)
    enc.set_in_sample_rate(SR)
    enc.set_channels(1)
    enc.set_quality(2)
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()
    with open(os.path.join(OUT, name + ".mp3"), "wb") as f:
        f.write(enc.encode(pcm) + enc.flush())
    rms = 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
    seam = abs(x[0] - x[-1]) if loop else 0
    return f"{name:16s} {len(x) / SR:5.2f}s  RMS {rms:6.1f} dBFS  {'loop, seam jump %.4f' % seam if loop else 'one-shot'}"


# -------------------------------------------------------------- sounds ----

def carve_loop():
    """Board edge carving through packed snow: hissy band noise + crunchy grains."""
    dur = 3.0
    t = t_axis(dur + 0.25)
    hiss = band(noise(dur + 0.25), 700, 5200) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.9 * t))
    grains = np.zeros_like(t)
    idx = rng.integers(0, len(t), 900)
    grains[idx] = rng.uniform(-1, 1, len(idx))
    grains = band(grains, 1500, 7000) * 1.8
    body = lowpass(pink(dur + 0.25), 900) * 0.6
    x = hiss + grains + body
    return make_loop(x)


def wind_loop():
    """Rushing wind at speed: low rumble + a slowly moving whistle band."""
    dur = 6.0
    t = t_axis(dur + 0.5)
    rumble = lowpass(pink(dur + 0.5), 500) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.23 * t))
    whistle_src = noise(dur + 0.5)
    whistle = sweep_band(whistle_src, 380, 900, q=9, steps=48)
    whistle += sweep_band(whistle_src[::-1].copy(), 700, 420, q=9, steps=48)
    gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.17 * t + 1.0) ** 2
    x = rumble * 1.2 + whistle * 0.7 * gust
    return make_loop(x, fade=0.5)


def grind_loop():
    """Metal rail grind: scrape noise + inharmonic metallic partials that wobble."""
    dur = 2.0
    t = t_axis(dur + 0.25)
    scrape = band(noise(dur + 0.25), 1800, 9000) * (0.7 + 0.3 * np.abs(np.sin(2 * np.pi * 7 * t)))
    partials = np.zeros_like(t)
    for f, a in ((1220, 0.5), (2710, 0.35), (4130, 0.25), (6020, 0.15)):
        wob = 1 + 0.004 * np.sin(2 * np.pi * rng.uniform(3, 6) * t)
        partials += a * np.sin(2 * np.pi * f * wob * t + rng.uniform(0, 6))
    x = scrape * 0.8 + partials * 0.35 * (0.8 + 0.2 * np.sin(2 * np.pi * 3 * t))
    return make_loop(x)


def campfire_loop():
    """Crackling fire: soft low roar + random pops and crackles."""
    dur = 6.0
    n = int(SR * (dur + 0.5))
    roar = lowpass(pink(dur + 0.5), 700) * 0.5
    crack = np.zeros(n)
    for _ in range(140):
        at = rng.integers(0, n - 4000)
        ln = rng.integers(80, 1400)
        burst = rng.standard_normal(ln) * exp_decay(ln, rng.uniform(0.001, 0.008))
        crack[at:at + ln] += burst * rng.uniform(0.3, 1.0)
    crack = highpass(crack, 900)
    return make_loop(roar + crack * 1.2, fade=0.5)


def land_thump():
    """Landing: low body thud + snow crunch burst."""
    n = int(SR * 0.7)
    t = np.arange(n) / SR
    f = 95 * np.exp(-t * 6) + 45
    thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * exp_decay(n, 0.12)
    crunch = band(noise(0.7), 400, 6000) * exp_decay(n, 0.09)
    grains = np.zeros(n)
    idx = rng.integers(0, int(SR * 0.25), 220)
    grains[idx] = rng.uniform(-1, 1, len(idx))
    grains = band(grains, 1200, 8000) * exp_decay(n, 0.15)
    return thud * 1.0 + crunch * 0.55 + grains * 1.2


def jump_pop():
    """Ollie pop: board flex 'thwack' + short upward whoosh."""
    n = int(SR * 0.45)
    t = np.arange(n) / SR
    click = band(noise(0.45), 1500, 7000) * exp_decay(n, 0.008)
    thwack = np.sin(2 * np.pi * (160 + 80 * t) * t) * exp_decay(n, 0.05)
    whoosh = sweep_band(noise(0.45), 500, 2600, q=3, steps=24) * env_adsr(n, 0.05, 0.1, 0.5, 0.25)
    return click * 1.0 + thwack * 0.7 + whoosh * 0.8


def trick_whoosh():
    """Spin / flip whoosh: band sweep up then down with a doppler-ish swell."""
    dur = 0.75
    n = int(SR * dur)
    src = noise(dur)
    up = sweep_band(src, 350, 3200, q=3.5, steps=40)
    e = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return up * e


def trick_success():
    """Reward chime: bright bell arpeggio (C6 E6 G6 C7)."""
    notes = [1046.5, 1318.5, 1568.0, 2093.0]
    total = int(SR * 1.3)
    x = np.zeros(total)
    for k, f in enumerate(notes):
        start = int(SR * 0.07 * k)
        n = total - start
        t = np.arange(n) / SR
        tone = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * exp_decay(n, 0.08)
                + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * exp_decay(n, 0.03))
        x[start:] += tone * exp_decay(n, 0.35) * (0.9 - 0.1 * k)
    shimmer = band(noise(1.3), 6000, 12000) * exp_decay(total, 0.25) * 0.08
    return x + shimmer


def powder_burst():
    """Soft 'poof' of powder snow (for landing in deep snow / spraying)."""
    n = int(SR * 0.6)
    poof = lowpass(noise(0.6), 1800) * env_adsr(n, 0.01, 0.08, 0.4, 0.45)
    sparkle = band(noise(0.6), 3000, 9000) * exp_decay(n, 0.1) * 0.4
    return poof + sparkle


def equip_click():
    """Strapping in: buckle ratchet clicks + plastic clack."""
    n = int(SR * 0.6)
    x = np.zeros(n)
    for k, at in enumerate((0.0, 0.07, 0.13, 0.18, 0.32)):
        s = int(at * SR)
        ln = 900
        c = band(rng.standard_normal(ln), 2500, 9000) * exp_decay(ln, 0.004)
        c += np.sin(2 * np.pi * 1800 * np.arange(ln) / SR) * exp_decay(ln, 0.006) * 0.5
        x[s:s + ln] += c * (1.4 if k == 4 else 1.0)
    return x


def ui_select():
    """Short friendly UI blip for menus (board select)."""
    n = int(SR * 0.18)
    t = np.arange(n) / SR
    f = 700 + 900 * t / 0.18
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_adsr(n, 0.005, 0.04, 0.6, 0.1)


SOUNDS = {
    "carve_loop": (carve_loop, True),
    "wind_loop": (wind_loop, True),
    "grind_loop": (grind_loop, True),
    "campfire_loop": (campfire_loop, True),
    "land_thump": (land_thump, False),
    "jump_pop": (jump_pop, False),
    "trick_whoosh": (trick_whoosh, False),
    "trick_success": (trick_success, False),
    "powder_burst": (powder_burst, False),
    "equip_click": (equip_click, False),
    "ui_select": (ui_select, False),
}

if __name__ == "__main__":
    lines = []
    for name, (fn, loop) in SOUNDS.items():
        lines.append(write(name, fn(), loop=loop))
    report = "\n".join(lines)
    with open(os.path.join(OUT, "sfx_report.txt"), "w") as f:
        f.write(report + "\n")
    print(report)
