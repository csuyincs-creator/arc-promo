import React from 'react';
import {AbsoluteFill, interpolate, random, staticFile, useCurrentFrame} from 'remotion';
import {SEGMENTS} from './timeline';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Warm white flash on the hardest hits. */
export const Flashes: React.FC = () => {
  const frame = useCurrentFrame();
  let a = 0;
  for (const s of SEGMENTS) {
    if (!s.flash) continue;
    a = Math.max(a, interpolate(frame - s.from, [-1, 0, 4], [0, 0.55, 0], clamp));
  }
  return a > 0 ? <AbsoluteFill style={{backgroundColor: '#fff3e2', opacity: a, mixBlendMode: 'screen'}} /> : null;
};

/** Drifting light leaks - film burned at the edges - that swell with the music. */
export const LightLeaks: React.FC<{strength: number}> = ({strength}) => {
  const frame = useCurrentFrame();
  const t = frame / 25;
  const pulse = SEGMENTS.reduce((acc, s) => Math.max(acc, interpolate(frame - s.from, [0, 6], [s.energy, 0], clamp)), 0);
  const o = strength * (0.1 + 0.9 * pulse);
  const x1 = -6 + 10 * Math.sin(t * 0.7);
  const y1 = 20 + 15 * Math.cos(t * 0.9);
  const x2 = 104 - 8 * Math.sin(t * 0.5 + 1);
  const y2 = 30 + 25 * Math.sin(t * 1.1);
  return (
    <AbsoluteFill
      style={{
        mixBlendMode: 'screen',
        opacity: o,
        background: `radial-gradient(ellipse 45% 60% at ${x1}% ${y1}%, rgba(255,120,40,0.55), rgba(255,60,90,0.18) 45%, rgba(0,0,0,0) 70%),
                     radial-gradient(ellipse 40% 55% at ${x2}% ${y2}%, rgba(255,190,90,0.45), rgba(200,60,160,0.15) 50%, rgba(0,0,0,0) 72%)`,
      }}
    />
  );
};

/** Grain that changes every frame, and a soft vignette. */
export const Film: React.FC = () => {
  const frame = useCurrentFrame();
  const k = frame % 6;
  const ox = Math.floor(random(`gx${frame}`) * 512);
  const oy = Math.floor(random(`gy${frame}`) * 512);
  return (
    <>
      <AbsoluteFill
        style={{
          backgroundImage: `url(${staticFile(`grain${k}.png`)})`,
          backgroundSize: '256px 256px',
          backgroundPosition: `${ox}px ${oy}px`,
          mixBlendMode: 'overlay',
          opacity: 0.22,
        }}
      />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 75% 70% at 50% 52%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.5) 100%)'}} />
    </>
  );
};
