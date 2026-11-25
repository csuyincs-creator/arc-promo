import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {G, PROJECT} from './timeline';

// Primary line (on top) and secondary line (hugging the curve). Defaults suit Chinese + English on macOS.
export const FONT1 = PROJECT.fonts?.line1 ?? '"Songti SC", "STSong", "Noto Serif SC", "Noto Serif CJK SC", serif';
export const FONT2 = PROJECT.fonts?.line2 ?? '"Iowan Old Style", "Palatino", "Georgia", serif';
const SIZE1 = PROJECT.textSize?.line1;
const SIZE2 = PROJECT.textSize?.line2 ?? 32;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const isCJK = (s: string) => /[぀-ヿ㐀-鿿가-힯]/.test(s);

/** Upper half of a circle concentric with the horizon, drawn left to right over the top. */
const arcPath = (r: number) => `M ${G.CX - r} ${G.CY} A ${r} ${r} 0 0 1 ${G.CX + r} ${G.CY}`;

/**
 * A phrase set on curves that follow the horizon. Letters arrive one by one while the
 * whole phrase lifts off the arc and sharpens from a blur.
 */
export const ArcText: React.FC<{line1: string; line2?: string; start: number; end: number; scale: number; ink: 'light' | 'dark'; id: string}> = ({
  line1,
  line2,
  start,
  end,
  scale,
  ink,
  id,
}) => {
  const frame = useCurrentFrame();
  const local = frame - start;
  const out = interpolate(frame, [end - 3, end], [1, 0], clamp);
  if (local < 0 || out <= 0) return null;

  // Defaults: 84 px for CJK, 100 px for a Latin phrase standing alone, 72 px for a Latin line above a second line.
  const size1 = (SIZE1 ?? (isCJK(line1) ? 84 : line2 ? 72 : 100)) * scale;
  const size2 = SIZE2 * scale;
  const gap = 24 + 6 * scale;
  const r2 = G.R + gap;
  const r1 = line2 ? r2 + size2 * 1.05 + 16 * scale : G.R + gap;
  const color = ink === 'light' ? '#fbf8f2' : '#15130f';
  const glow = ink === 'light' ? 'rgba(0,0,0,0.6)' : 'rgba(255,250,240,0.7)';
  const blur = interpolate(local, [0, 8], [10, 0], {...clamp, easing: Easing.out(Easing.cubic)});
  const lift = interpolate(local, [0, 10], [26 * scale, 0], {...clamp, easing: Easing.out(Easing.back(1.4))});

  const letters = (text: string, delay: number) =>
    Array.from(text).map((ch, i) => (
      <tspan key={i} fillOpacity={interpolate(local - delay - i * 1.5, [0, 5], [0, 1], clamp)}>
        {ch}
      </tspan>
    ));

  return (
    <svg
      width={1920}
      height={1080}
      style={{position: 'absolute', inset: 0, opacity: out, overflow: 'visible', filter: `blur(${blur}px) drop-shadow(0 1px ${3 * scale}px ${glow}) drop-shadow(0 0 ${22 * scale}px ${glow})`}}
    >
      <defs>
        <path id={`${id}-1`} d={arcPath(r1 + lift)} />
        <path id={`${id}-2`} d={arcPath(r2 + lift * 0.6)} />
      </defs>
      <text fill={color} fontFamily={FONT1} fontSize={size1} fontWeight={500} letterSpacing={size1 * (isCJK(line1) ? 0.18 : 0.03)}>
        <textPath href={`#${id}-1`} startOffset="50%" textAnchor="middle">
          {letters(line1, 0)}
        </textPath>
      </text>
      {line2 ? (
        <text fill={color} fontFamily={FONT2} fontSize={size2} letterSpacing={size2 * (isCJK(line2) ? 0.18 : 0.08)} opacity={0.92}>
          <textPath href={`#${id}-2`} startOffset="50%" textAnchor="middle">
            {letters(line2, 3)}
          </textPath>
        </text>
      ) : null}
    </svg>
  );
};
