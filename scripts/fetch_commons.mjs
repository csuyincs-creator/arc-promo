// node fetch.mjs outDir "name|width|File title" ...   (Wikimedia Commons, JPEG or PNG)
import fs from 'node:fs';
const UA = 'Mozilla/5.0 (Macintosh) media-fetch/1.0';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const [outDir, ...items] = process.argv.slice(2);
for (const item of items) {
  const [name, width, title] = item.split('|');
  const url = `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(title)}` + (width === "0" ? "" : `?width=${width}`);
  let done = false;
  for (let i = 0; i < 5 && !done; i++) {
    try {
      const r = await fetch(url, {headers: {'User-Agent': UA}});
      const b = Buffer.from(await r.arrayBuffer());
      const ext = b[0] === 0xff && b[1] === 0xd8 ? 'jpg' : b[0] === 0x89 && b[1] === 0x50 ? 'png' : null;
      if (r.ok && ext) { fs.writeFileSync(`${outDir}/${name}.${ext}`, b); done = true; console.log(`${name}.${ext} ${(b.length / 1e6).toFixed(1)}MB`); }
      else { console.log(name, 'retry', r.status); await sleep(15000); }
    } catch (e) { console.log(name, 'error', e.message); await sleep(15000); }
  }
  if (!done) console.log('FAILED', name);
  await sleep(3000);
}
