// Dev helper: render a few frames for review.   SCALE=0.5 node stills.mjs 0 40 120
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition, openBrowser} from '@remotion/renderer';
import path from 'node:path';

const frames = process.argv.slice(2).map(Number);
const scale = Number(process.env.SCALE ?? 0.5);
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const browser = await openBrowser('chrome');
const composition = await selectComposition({serveUrl, id: 'Arc', puppeteerInstance: browser});
for (const frame of frames) {
  const output = path.resolve(`out/stills/f${String(frame).padStart(3, '0')}.jpg`);
  await renderStill({composition, serveUrl, frame, output, imageFormat: 'jpeg', jpegQuality: 88, scale, puppeteerInstance: browser});
  process.stdout.write(frame + ' ');
}
await browser.close({silent: true});
