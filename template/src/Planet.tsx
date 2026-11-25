import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {G, OPENING, OPENING_IS_EARTH} from './timeline';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/**
 * The opening world (by default Earth's night side) with its sunrise glow along the limb.
 * It can sink, blur and brighten - the end card uses it so the film loops into frame 0.
 */
export const OpeningWorld: React.FC<{drop: number; glow: number; base: number; blur: number; turn: number}> = ({drop, glow, base, blur, turn}) => {
  const layer = (file: string, opacity: number, blend: 'normal' | 'screen') => (
    <div
      style={{
        position: 'absolute',
        left: -G.MX,
        top: -G.MT + drop,
        width: G.IW,
        height: G.IH,
        opacity,
        mixBlendMode: blend,
        filter: blur > 0.2 ? `blur(${blur}px)` : undefined,
        transformOrigin: `${G.CX + G.MX}px ${G.CY + G.MT}px`,
        transform: `rotate(${turn}deg)`,
      }}
    >
      <Img src={staticFile(`shots/${file}.jpg`)} style={{width: G.IW, height: G.IH, display: 'block'}} />
    </div>
  );
  return (
    <AbsoluteFill style={{backgroundColor: 'black', overflow: 'hidden'}}>
      {layer(OPENING, OPENING_IS_EARTH ? base : Math.max(base, glow * 0.6), 'normal')}
      {OPENING_IS_EARTH ? layer(`${OPENING}_glow`, glow, 'screen') : null}
    </AbsoluteFill>
  );
};

/** The Sun coming up over the arc: hot core, halo and an anamorphic streak. */
export const SunRise: React.FC<{power: number}> = ({power}) => {
  if (power <= 0.01) return null;
  const x = G.CX;
  const y = G.TOP - 4;
  const blob = (w: number, h: number, bg: string, o: number) => (
    <div style={{position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h, background: bg, opacity: o, mixBlendMode: 'screen', borderRadius: '50%'}} />
  );
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      {blob(2400 * power, 1500 * power, 'radial-gradient(closest-side, rgba(255,170,90,0.55), rgba(255,110,40,0.18) 45%, rgba(0,0,0,0))', power)}
      {blob(520 * power, 520 * power, 'radial-gradient(closest-side, #fff, rgba(255,236,200,0.9) 25%, rgba(255,160,80,0.35) 60%, rgba(0,0,0,0))', 1)}
      {blob(3600 * power, 34 * power, 'radial-gradient(closest-side, rgba(255,240,220,0.95), rgba(255,170,100,0.4) 40%, rgba(0,0,0,0))', power)}
      {blob(2200 * power, 10, 'radial-gradient(closest-side, rgba(150,190,255,0.9), rgba(0,0,0,0))', power * 0.8)}
    </AbsoluteFill>
  );
};

/** First shot: dawn on the curve of the world, the sun breaking over it on the first cut. */
export const Opening: React.FC<{dur: number}> = ({dur}) => {
  const f = useCurrentFrame();
  const glow = interpolate(f, [0, dur - 1], [0.42, 1], {...clamp, easing: Easing.in(Easing.quad)});
  const drop = interpolate(f, [0, dur], [26, 0], {...clamp, easing: Easing.out(Easing.quad)});
  const sun = interpolate(f, [dur * 0.32, dur], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
  return (
    <AbsoluteFill>
      <OpeningWorld drop={drop} glow={glow} base={1} blur={0} turn={-f * 0.03} />
      <SunRise power={sun} />
    </AbsoluteFill>
  );
};
