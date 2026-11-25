import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {FONT1, FONT2} from './ArcText';
import {OpeningWorld} from './Planet';
import {END_CARD, PROJECT, TOTAL, type EndCardSpec} from './timeline';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Chars: React.FC<{text: string; start: number; step: number; end: number; style: React.CSSProperties}> = ({text, start, step, end, style}) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [end - 6, end], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
  return (
    <div style={{display: 'flex', justifyContent: 'center', flexWrap: 'wrap', ...style}}>
      {Array.from(text).map((ch, i) => {
        const p = interpolate(f - start - i * step, [0, 9], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              whiteSpace: 'pre',
              opacity: p * (1 - out),
              filter: `blur(${(1 - p) * 14 + out * 10}px)`,
              transform: `translateY(${(1 - p) * 18 - out * 8}px) scale(${1 + (1 - p) * 0.25 + out * 0.06})`,
            }}
          >
            {ch}
          </span>
        );
      })}
    </div>
  );
};

/** A highlight that sweeps across the title once. */
const Sheen: React.FC<{at: number; children: React.ReactNode}> = ({at, children}) => {
  const f = useCurrentFrame();
  const x = interpolate(f, [at, at + 16], [-30, 130], {...clamp, easing: Easing.inOut(Easing.quad)});
  return (
    <div style={{position: 'relative'}}>
      {children}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `linear-gradient(100deg, rgba(255,255,255,0) ${x - 12}%, rgba(255,236,210,0.85) ${x}%, rgba(255,255,255,0) ${x + 12}%)`,
          mixBlendMode: 'overlay',
          pointerEvents: 'none',
        }}
      />
    </div>
  );
};

const Card: React.FC<{card: EndCardSpec; from: number; to: number}> = ({card, from, to}) => {
  const len1 = Array.from(card.line1).length;
  const len2 = Array.from(card.line2 ?? '').length;
  if ((card.kind ?? 'line') === 'title') {
    return (
      <div style={{position: 'absolute', top: 400, left: 0, right: 0}}>
        <Sheen at={from + 11}>
          <Chars text={card.line1} start={from} step={4} end={to} style={{fontFamily: FONT1, fontSize: Math.min(104, 1300 / Math.max(1, len1)), fontWeight: 500, letterSpacing: '0.32em', paddingLeft: '0.32em'}} />
        </Sheen>
        {card.line2 ? <Chars text={card.line2} start={from + 4} step={0.7} end={to} style={{fontFamily: FONT2, fontSize: 22, letterSpacing: '0.5em', marginTop: 14, opacity: 0.85}} /> : null}
      </div>
    );
  }
  const step2 = Math.min(0.5, 8 / Math.max(1, len2));
  return (
    <div style={{position: 'absolute', top: 430, left: 120, right: 120}}>
      <Chars text={card.line1} start={from} step={Math.min(1.6, 14 / Math.max(1, len1))} end={to} style={{fontFamily: FONT1, fontSize: Math.min(54, 1500 / Math.max(1, len1)), fontWeight: 500, letterSpacing: '0.12em'}} />
      {card.line2 ? <Chars text={card.line2} start={from + 9} step={step2} end={to} style={{fontFamily: FONT2, fontStyle: 'italic', fontSize: 27, marginTop: 20, opacity: 0.9}} /> : null}
    </div>
  );
};

/** From the end-card time to the end: the cards, then the dawn rises again into the first frame (it loops). */
export const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  const len = TOTAL - END_CARD;
  const cards = PROJECT.endCards ?? [];
  const riseAt = Math.round(len * 0.785);
  const rise = interpolate(f, [riseAt, len - 1], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const enter = interpolate(f, [0, 8], [0, 1], clamp);
  const slot = (riseAt - 2) / Math.max(1, cards.length);
  return (
    <AbsoluteFill style={{backgroundColor: PROJECT.endColor ?? '#0b0e13'}}>
      <AbsoluteFill style={{opacity: 0.5 + 0.5 * rise}}>
        <OpeningWorld drop={interpolate(rise, [0, 1], [360, 26])} glow={(0.6 - 0.18 * rise) * enter} base={rise} blur={22 * (1 - rise)} turn={0} />
      </AbsoluteFill>
      <AbsoluteFill style={{color: '#f6f2ea', textShadow: '0 0 30px rgba(0,0,0,0.6)', textAlign: 'center'}}>
        {cards.map((c, i) => (
          <Card key={i} card={c} from={Math.round(i * slot) + 3} to={Math.round((i + 1) * slot)} />
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
