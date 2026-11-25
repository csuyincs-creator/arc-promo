"""
Turns the music into the edit: where every cut lands, which hits are big, when the end card starts.

    # Copy the cut rhythm of an existing video (its audio becomes the soundtrack):
    python analyze_music.py --video reference.mp4 --out workspace

    # Or cut to any audio track (onset detection + the accelerating arc-promo rhythm):
    python analyze_music.py --audio song.mp3 --out workspace [--start 0] [--length 20] [--end-card 15.9]

Writes:
    <out>/public/music.wav         the soundtrack, trimmed (48 kHz stereo)
    <out>/src/data/timeline.json   {fps, duration, cuts[], endCard, bigHits[], source}

The rhythm in audio mode copies the shape of the original promo: three slow shots (~1.0-1.3 s),
then cuts that speed up from ~0.55 s to ~0.2 s, each snapped to the strongest onset nearby,
and an end card at ~80% of the length on a strong hit.
"""
import argparse
import json
import os
import re
import subprocess

import numpy as np

FPS = 25


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def snap(t):
    return round(round(t * FPS) / FPS, 3)


def extract_audio(src, dst, start=0.0, length=None):
    cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(start), '-i', src]
    if length:
        cmd += ['-t', str(length)]
    run(cmd + ['-vn', '-ac', '2', '-ar', '48000', dst])


def duration_of(path):
    out = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]).stdout
    return float(out.strip())


# ----------------------------------------------------------------------------- video mode
def cuts_from_video(video, threshold=0.12, min_gap=0.15):
    """Scene-change scores per frame; every peak above threshold is a cut."""
    res = subprocess.run(
        ['ffmpeg', '-hide_banner', '-i', video, '-vf', "scale=320:-2,select='gte(scene,0)',metadata=print:key=lavfi.scene_score", '-an', '-f', 'null', '-'],
        capture_output=True, text=True,
    )
    times, scores, t = [], [], None
    for line in res.stderr.splitlines():
        m = re.search(r'pts_time:([0-9.]+)', line)
        if m:
            t = float(m.group(1))
        m = re.search(r'scene_score=([0-9.]+)', line)
        if m and t is not None:
            times.append(t)
            scores.append(float(m.group(1)))
    cuts = []
    for t, s in zip(times, scores):
        if s < threshold:
            continue
        if cuts and t - cuts[-1][0] < min_gap:
            if s > cuts[-1][1]:
                cuts[-1] = (t, s)
            continue
        cuts.append((t, s))
    return cuts


# ----------------------------------------------------------------------------- audio mode
def onset_envelope(path, sr=22050, hop=256, n_fft=1024):
    pcm = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.float32)
    n = 1 + (len(x) - n_fft) // hop
    frames = np.lib.stride_tricks.as_strided(x, shape=(n, n_fft), strides=(x.strides[0] * hop, x.strides[0]))
    mag = np.abs(np.fft.rfft(frames * np.hanning(n_fft), axis=1))
    logm = np.log1p(mag * 10)
    flux = np.maximum(logm[1:] - logm[:-1], 0).sum(axis=1)
    flux = np.concatenate([[0], flux])
    # adaptive threshold: subtract a moving median
    k = int(0.4 * sr / hop)
    pad = np.pad(flux, k, mode='edge')
    med = np.array([np.median(pad[i:i + 2 * k + 1]) for i in range(len(flux))])
    env = np.maximum(flux - med, 0)
    env /= env.max() + 1e-9
    t = np.arange(len(env)) * hop / sr
    return t, env


def peaks(t, env, min_gap=0.09):
    """Local maxima of the onset envelope, strongest first within min_gap."""
    idx = np.where((env[1:-1] > env[:-2]) & (env[1:-1] >= env[2:]) & (env[1:-1] > 0.04))[0] + 1
    order = idx[np.argsort(-env[idx])]
    chosen = []
    for i in order:
        if all(abs(t[i] - t[j]) >= min_gap for j in chosen):
            chosen.append(i)
    chosen.sort()
    return [(float(t[i]), float(env[i])) for i in chosen]


def plan_cuts(onsets, duration, end_card=None):
    """Pick cuts that follow the arc-promo rhythm, each snapped to the best onset near its target."""
    if end_card is None:
        target = duration * 0.795
        near = [(t, s) for t, s in onsets if abs(t - target) < 0.8]
        end_card = max(near, key=lambda p: p[1] - abs(p[0] - target) * 0.5)[0] if near else target
    end_card = snap(end_card)

    def interval(t):
        if t < 3.3 * end_card / 15.96:  # the slow opening (scaled to the song length)
            return 1.1 * end_card / 15.96
        p = (t - 3.3 * end_card / 15.96) / (end_card * (1 - 3.3 / 15.96))
        return 0.55 - 0.35 * min(1.0, max(0.0, p)) ** 0.8

    cuts = [0.0]
    while True:
        cur = cuts[-1]
        want = interval(cur)
        lo, hi = cur + want * 0.65, cur + want * 1.45
        if hi >= end_card - 0.12:
            break
        cand = [(t, s) for t, s in onsets if lo <= t <= hi]
        if cand:
            nxt = max(cand, key=lambda p: p[1] - 0.6 * abs(p[0] - (cur + want)) / want)[0]
        else:
            nxt = cur + want
        cuts.append(snap(nxt))
    return [c for c in cuts if c < end_card - 0.1], end_card


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--video')
    src.add_argument('--audio')
    ap.add_argument('--out', required=True, help='workspace folder (the Remotion project)')
    ap.add_argument('--start', type=float, default=0.0, help='audio mode: where in the song to start (s)')
    ap.add_argument('--length', type=float, default=None, help='audio mode: film length (s); default = whole track, max 30')
    ap.add_argument('--end-card', type=float, default=None, help='force the end-card time (s)')
    ap.add_argument('--threshold', type=float, default=0.12, help='video mode: scene-change threshold')
    a = ap.parse_args()

    os.makedirs(os.path.join(a.out, 'public'), exist_ok=True)
    os.makedirs(os.path.join(a.out, 'src', 'data'), exist_ok=True)
    wav = os.path.join(a.out, 'public', 'music.wav')

    if a.video:
        extract_audio(a.video, wav)
        duration = duration_of(wav)
        found = cuts_from_video(a.video, a.threshold)
        # The end card is the last cut followed by a long hold (or a forced time).
        end_card = a.end_card
        if end_card is None:
            holds = [t for i, (t, _) in enumerate(found) if (found[i + 1][0] if i + 1 < len(found) else duration) - t > 1.5 and duration - t > 2]
            end_card = holds[-1] if holds else duration * 0.795
        end_card = snap(end_card)
        cuts = [0.0] + [snap(t) for t, _ in found if 0.2 < t < end_card - 0.1]
        strength = {snap(t): s for t, s in found}
        big = [c for c in cuts[3:] if strength.get(c, 0) >= 0.9]
        source = f'video:{os.path.basename(a.video)}'
    else:
        full = duration_of(a.audio)
        length = a.length or min(30.0, full - a.start)
        extract_audio(a.audio, wav, a.start, length)
        duration = duration_of(wav)
        t, env = onset_envelope(wav)
        onsets = peaks(t, env)
        cuts, end_card = plan_cuts(onsets, duration, a.end_card)
        st = {snap(t_): s for t_, s in onsets}
        strengths = sorted((st.get(c, 0) for c in cuts[3:]), reverse=True)
        bar = strengths[max(0, len(strengths) // 5 - 1)] if strengths else 1
        big = [c for c in cuts[3:] if st.get(c, 0) >= bar and st.get(c, 0) > 0.35]
        source = f'audio:{os.path.basename(a.audio)}@{a.start}s'

    timeline = {
        'fps': FPS,
        'duration': round(duration, 3),
        'cuts': cuts,
        'endCard': end_card,
        'bigHits': big,
        'source': source,
    }
    json.dump(timeline, open(os.path.join(a.out, 'src', 'data', 'timeline.json'), 'w'), indent=1)
    gaps = np.diff(cuts + [end_card])
    print(f'{len(cuts)} shots before the end card at {end_card}s (film {duration:.2f}s); '
          f'shot lengths {gaps.max():.2f}s -> {gaps[-5:].mean():.2f}s; {len(big)} big hits')
    print('cuts:', ' '.join(f'{c:.2f}' for c in cuts))


if __name__ == '__main__':
    main()
