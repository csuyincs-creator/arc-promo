import React from 'react';
import {Composition} from 'remotion';
import {Arc} from './Arc';
import {FPS, TOTAL} from './timeline';

// Laid out at 1920x1080; render with --scale=2 for 4K (all shots are drawn at 4K).
export const Root: React.FC = () => <Composition id="Arc" component={Arc} durationInFrames={TOTAL} fps={FPS} width={1920} height={1080} />;
