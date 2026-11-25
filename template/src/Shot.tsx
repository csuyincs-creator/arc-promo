import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, random, staticFile, useCurrentFrame} from 'remotion';
import {FPS, G, type Segment} from './timeline';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Splits the picture into R, G and B and pushes them apart - the "hit" on a hard cut. */
export const RgbSplit: React.FC<{id: string; amount: number}> = ({id, amount}) => (
  <svg width={0} height={0} style={{position: 'absolute'}}>
    <filter id={id} x="-2%" y="-2%" width="104%" height="104%" colorInterpolationFilters="sRGB">
      <feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r" />
      <feOffset in="r" dx={amount} dy={amount * 0.18} result="r2" />
      <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g" />
      <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b" />
      <feOffset in="b" dx={-amount} dy={-amount * 0.18} result="b2" />
      <feBlend in="r2" in2="g" mode="screen" result="rg" />
      <feBlend in="rg" in2="b2" mode="screen" />
    </filter>
  </svg>
);

/**
 * One world on the arc. The camera:
 *  - punches in on the cut and settles (scale about the arc's top point, so the arc stays put),
 *  - turns the world around the circle's centre, so the surface slides under the words,
 *  - optionally rises from below, like a planet coming over the horizon,
 *  - splits RGB for the first frames of a hard cut.
 */
export const Shot: React.FC<{seg: Segment; index: number}> = ({seg, index}) => {
  const frame = useCurrentFrame();
  const dir = random(`dir-${index}-${seg.name}`) > 0.5 ? 1 : -1;
  const e = seg.energy;
  const t = frame / FPS;

  const whip = interpolate(frame, [0, 8], [-dir * 3.4 * e, 0], {...clamp, easing: Easing.out(Easing.cubic)});
  const rotation = whip + dir * t * (0.7 + 0.9 * e);

  const punch = interpolate(frame, [0, 7], [1 + 0.11 * e, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const push = 1 + 0.03 * Math.min(1, frame / Math.max(seg.dur, 1));
  const rise = seg.rise ? interpolate(frame, [0, 9], [330, 0], {...clamp, easing: Easing.out(Easing.exp)}) : 0;

  const split = index < 3 ? 0 : interpolate(frame, [0, 4], [16 * e, 0], clamp);
  // Tiny camera shake that grows as the cuts get faster.
  const shake = e > 0.7 ? (random(`sx-${index}-${frame}`) - 0.5) * 5 * (e - 0.6) : 0;
  const shakeY = e > 0.7 ? (random(`sy-${index}-${frame}`) - 0.5) * 5 * (e - 0.6) : 0;
  const filterId = `rgb-${index}`;

  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      {split > 0.4 ? <RgbSplit id={filterId} amount={split} /> : null}
      <div
        style={{
          position: 'absolute',
          left: -G.MX + shake,
          top: -G.MT + rise + shakeY,
          width: G.IW,
          height: G.IH,
          transformOrigin: `${G.CX + G.MX}px ${G.TOP + G.MT}px`,
          transform: `scale(${punch * push})`,
          filter: split > 0.4 ? `url(#${filterId})` : undefined,
        }}
      >
        <div style={{position: 'absolute', inset: 0, transformOrigin: `${G.CX + G.MX}px ${G.CY + G.MT}px`, transform: `rotate(${rotation}deg)`}}>
          <Img src={staticFile(`shots/${seg.name}.jpg`)} style={{width: G.IW, height: G.IH, display: 'block'}} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
