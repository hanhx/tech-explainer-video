#!/usr/bin/env python3
"""Deterministic, original action SFX. NumPy only; exports mono 48 kHz PCM WAV.

Use as a starting palette, not a finished mix. The caller sets event timing and
gain; a clock tick is ONE tick, so cadence comes from the visible clock.
"""
from __future__ import annotations

import argparse
import hashlib
import wave
from pathlib import Path

import numpy as np

SR = 48000
KINDS = (
    'motion_swish', 'motion_sweep', 'motion_land',
    'mouse_down', 'mouse_up', 'mouse_click', 'keyboard_tap',
    'clock_tick', 'clock_tock',
)


def synth_action(kind: str, sr: int = SR) -> np.ndarray:
    """Return finite float64 mono samples, peak <= .8, exact zero at both ends."""
    if kind not in KINDS:
        raise ValueError(f'unknown action sound: {kind}; choose from {KINDS}')
    if sr < 8000:
        raise ValueError('sample rate must be at least 8000 Hz')
    if kind == 'mouse_click':
        down, up = synth_action('mouse_down', sr), synth_action('mouse_up', sr)
        x = np.zeros(round(.12 * sr))
        x[:len(down)] += down
        i = round(.07 * sr)
        x[i:i + len(up)] += up * .82
        return x

    duration = {
        'motion_swish': .30, 'motion_sweep': .65, 'motion_land': .18,
        'mouse_down': .045, 'mouse_up': .035, 'keyboard_tap': .06,
        'clock_tick': .055, 'clock_tock': .065,
    }[kind]
    t = np.arange(round(duration * sr), dtype=np.float64) / sr
    seed = int.from_bytes(hashlib.sha256(kind.encode()).digest()[:8], 'big')
    rng = np.random.default_rng(seed)

    def noise(center: float, width: float) -> np.ndarray:
        # Smooth frequency rolloff avoids harsh full-band white-noise hiss.
        f = np.fft.rfftfreq(len(t), 1 / sr)
        spectrum = np.fft.rfft(rng.standard_normal(len(t)))
        y = np.fft.irfft(spectrum * np.exp(-.5 * ((f - center) / width) ** 2), n=len(t))
        return y / max(float(np.max(np.abs(y))), 1e-12)

    if kind.startswith('motion_s'):
        sweep = kind == 'motion_sweep'
        f0, f1 = (210, 570) if sweep else (680, 250)
        phase = 2 * np.pi * (f0 * t + (f1 - f0) * t * t / (2 * duration))
        x = (.52 * noise(1250 if sweep else 1800, 900) + .22 * np.sin(phase))
        x *= np.sin(np.pi * t / duration) ** 1.8
    elif kind == 'motion_land':
        x = np.sin(2 * np.pi * (180 * t - 210 * t * t)) * np.exp(-30 * t)
        x += .12 * noise(1600, 800) * np.exp(-80 * t)
    else:
        freq, decay, air = {
            'mouse_down': (1300, 145, .58), 'mouse_up': (1850, 180, .45),
            'keyboard_tap': (680, 95, .50),
            'clock_tick': (2350, 130, .26), 'clock_tock': (1540, 110, .28),
        }[kind]
        x = ((1 - air) * np.sin(2 * np.pi * freq * t) + air * noise(freq, 900)) * np.exp(-decay * t)

    # Brief smooth ramps remove boundary discontinuities without cutting attack.
    n = min(round(.002 * sr), len(x) // 4)
    ramp = .5 - .5 * np.cos(np.linspace(0, np.pi, n))
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    x *= .8 / max(float(np.max(np.abs(x))), 1e-12)
    x[0] = x[-1] = 0.
    return x


def write_wav(path: Path, samples: np.ndarray, sr: int = SR) -> None:
    with wave.open(str(path), 'wb') as wav:
        wav.setparams((1, 2, sr, 0, 'NONE', 'not compressed'))
        wav.writeframes(np.rint(np.clip(samples, -1, 1) * 32767).astype('<i2').tobytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--kinds', nargs='+', choices=KINDS, default=list(KINDS))
    args = parser.parse_args()
    paths = [(kind, args.out / f'{kind}.wav') for kind in dict.fromkeys(args.kinds)]
    existing = [str(path) for _, path in paths if path.exists()]
    if existing:
        parser.error('refusing to replace existing sounds: ' + ', '.join(existing))
    args.out.mkdir(parents=True, exist_ok=True)
    for kind, path in paths:
        write_wav(path, synth_action(kind))
        print(path)


if __name__ == '__main__':
    main()
