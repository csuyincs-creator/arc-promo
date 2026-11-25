/**
 * Everything the edit needs, derived from three data files:
 *   data/timeline.json  - from analyze_music.py: cut times, big hits, end-card time, length
 *   data/project.json   - the message, the shot order, the end cards, fonts
 *   data/manifest.json  - from gen_shots.py: each shot's ink (light/dark text over it)
 */
import manifest from './data/manifest.json';
import project from './data/project.json';
import timeline from './data/timeline.json';

export const FPS: number = timeline.fps;
export const TOTAL = Math.floor(timeline.duration * FPS);
export const END_CARD = Math.round(timeline.endCard * FPS);

/** Geometry shared with gen_shots.py, in 1080p units (the shots are drawn at 2x). */
export const G = {R: 1850, TOP: 648, CX: 960, CY: 648 + 1850, MX: 160, MT: 120, IW: 2240, IH: 1200};

export type Phrase = {line1: string; line2?: string};
export type EndCardSpec = {line1: string; line2?: string; kind?: 'title' | 'line'};
type Project = {
  phrases: Phrase[];
  order: string[];
  opening?: string;
  textStart?: number | null;
  growLast?: boolean;
  endCards?: EndCardSpec[];
  fonts?: {line1?: string; line2?: string};
  textSize?: {line1?: number; line2?: number};
  endColor?: string;
  ink?: Record<string, 'light' | 'dark'>;
};
export const PROJECT = project as unknown as Project;
type Manifest = Record<string, {ink: 'light' | 'dark'; type?: string}>;
const MANIFEST = manifest as unknown as Manifest;

export const OPENING = PROJECT.opening ?? 'earth_rise';
export const OPENING_IS_EARTH = MANIFEST[OPENING]?.type === 'earth_rise';

const CUTS: number[] = [...timeline.cuts, timeline.endCard];
const SLOW = CUTS[Math.min(3, CUTS.length - 1)]; // the first three shots are the slow intro
const nearestCut = (t: number) => CUTS.slice(0, -1).reduce((a, b) => (Math.abs(b - t) < Math.abs(a - t) ? b : a));

// When the words start, and where each phrase hands over to the next (equal time, snapped to cuts).
const textStart = PROJECT.textStart ?? timeline.endCard * 0.53;
const P = PROJECT.phrases.length;
const bounds = Array.from({length: Math.max(0, P - 1)}, (_, k) => nearestCut(textStart + ((k + 1) * (timeline.endCard - textStart)) / P));

export const PHRASES = PROJECT.phrases.map((p, k) => ({
  ...p,
  from: Math.round((k === 0 ? textStart : bounds[k - 1]) * FPS),
  to: k === P - 1 ? END_CARD : Math.round(bounds[k] * FPS),
}));

export type Segment = {
  name: string;
  from: number;
  dur: number;
  ink: 'light' | 'dark';
  /** 0..1: how hard the cut hits (zoom punch, RGB split, shake). */
  energy: number;
  /** The world rises from below over the previous one (at each new phrase). */
  rise: boolean;
  flash: boolean;
};

const bigHits: number[] = timeline.bigHits;
const textSeg = CUTS.findIndex((c, i) => c <= textStart && CUTS[i + 1] > textStart);
const riseTimes = new Set([CUTS[textSeg], ...bounds].filter((t) => t >= SLOW));

export const SEGMENTS: Segment[] = CUTS.slice(0, -1).map((t, i) => {
  const name = i === 0 ? OPENING : PROJECT.order[(i - 1) % PROJECT.order.length];
  const from = Math.round(t * FPS);
  const progress = Math.max(0, (t - SLOW) / Math.max(0.001, timeline.endCard - SLOW));
  const big = bigHits.some((b) => Math.abs(b - t) < 0.02);
  return {
    name,
    from,
    dur: Math.round(CUTS[i + 1] * FPS) - from,
    ink: PROJECT.ink?.[name] ?? MANIFEST[name]?.ink ?? 'light',
    energy: i < 3 ? 0.25 : Math.min(1, 0.55 + 0.6 * progress + (big ? 0.35 : 0)),
    rise: riseTimes.has(t),
    flash: big,
  };
});

export const FIRST_CUT = SEGMENTS[1]?.from ?? 31;
export const SLOW_END = Math.round(SLOW * FPS);
/** First segment of the last phrase: from here the word grows on every cut. */
export const GROW_FROM = SEGMENTS.findIndex((s) => s.from >= (PHRASES[P - 1]?.from ?? END_CARD));

export const segmentAt = (frame: number) => {
  for (let i = SEGMENTS.length - 1; i >= 0; i--) if (frame >= SEGMENTS[i].from) return i;
  return 0;
};
