import React from 'react';
import {AbsoluteFill, Audio, Easing, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {ArcText} from './ArcText';
import {Film, Flashes, LightLeaks} from './Effects';
import {EndCard} from './EndCard';
import {Opening} from './Planet';
import {Shot} from './Shot';
import {END_CARD, FIRST_CUT, GROW_FROM, PHRASES, PROJECT, SEGMENTS, SLOW_END, TOTAL, segmentAt} from './timeline';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const Arc: React.FC = () => {
  const frame = useCurrentFrame();
  const segIndex = segmentAt(frame);
  const seg = SEGMENTS[segIndex];

  // The last phrase grows a step on every cut, popping into each new size.
  const step = Math.max(0, segIndex - GROW_FROM);
  const popped = interpolate(frame - seg.from, [0, 4], [step - 1, step], {...clamp, easing: Easing.out(Easing.back(2))});
  const lastScale = PROJECT.growLast === false ? 1 : 1 + 0.14 * Math.max(0, step >= 1 ? popped : step);

  const leak = frame < SLOW_END ? 0.55 : frame < END_CARD ? 0.45 : 0.12;
  const openFlash = interpolate(frame, [FIRST_CUT - 4, FIRST_CUT, FIRST_CUT + 6], [0, 0.85, 0], clamp);

  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <Audio src={staticFile('music.wav')} />

      {SEGMENTS.map((s, i) => {
        const tail = SEGMENTS[i + 1]?.rise ? 10 : 0; // stay underneath while the next world rises over us
        if (i === 0) {
          return (
            <Sequence key={`0-${s.name}`} from={0} durationInFrames={s.dur} name="Opening">
              <Opening dur={s.dur} />
            </Sequence>
          );
        }
        return (
          <Sequence key={`${i}-${s.name}`} from={s.from} durationInFrames={Math.min(s.dur + tail, END_CARD - s.from)} name={s.name}>
            <Shot seg={s} index={i} />
          </Sequence>
        );
      })}

      {PHRASES.map((p, k) => (
        <ArcText key={k} id={`p${k}`} line1={p.line1} line2={p.line2} start={p.from} end={p.to} ink={seg.ink} scale={k === PHRASES.length - 1 ? lastScale : 1} />
      ))}

      <Sequence from={END_CARD} durationInFrames={TOTAL - END_CARD} name="End card">
        <EndCard />
      </Sequence>

      <LightLeaks strength={leak} />
      <Flashes />
      {openFlash > 0 ? <AbsoluteFill style={{backgroundColor: '#fff6ea', opacity: openFlash}} /> : null}
      <Film />
    </AbsoluteFill>
  );
};
