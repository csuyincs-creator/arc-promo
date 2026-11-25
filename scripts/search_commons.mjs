// Search Wikimedia Commons; prints only CC0 / public-domain bitmaps.
//   node search.mjs [--min=W] [--wide] "query" ...
const UA = 'Mozilla/5.0 (Macintosh) media-fetch/1.0';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const args = process.argv.slice(2);
const min = Number((args.find((a) => a.startsWith('--min=')) || '--min=2000').slice(6));
const wide = args.includes('--wide');
for (const q of args.filter((a) => !a.startsWith('--'))) {
  const p = new URLSearchParams({
    action: 'query', format: 'json', generator: 'search', gsrnamespace: '6', gsrlimit: '25',
    gsrsearch: `${q} filetype:bitmap fileres:>${min}`,
    prop: 'imageinfo', iiprop: 'size|extmetadata', iiextmetadatafilter: 'LicenseShortName|Artist',
  });
  let txt = '';
  for (let i = 0; i < 5; i++) {
    const r = await fetch('https://commons.wikimedia.org/w/api.php?' + p, {headers: {'User-Agent': UA}});
    txt = await r.text();
    if (txt.startsWith('{')) break;
    await sleep(7000);
  }
  console.log('## ' + q);
  try {
    const pages = Object.values(JSON.parse(txt).query?.pages || {}).sort((a, b) => a.index - b.index);
    let n = 0;
    for (const x of pages) {
      const i = x.imageinfo?.[0] || {};
      const lic = i.extmetadata?.LicenseShortName?.value || '';
      if (!/^(CC0|Public domain|PD)/i.test(lic)) continue;
      if (wide && i.width < i.height * 1.25) continue;
      if (n++ >= 10) break;
      console.log(`  ${x.title.slice(5)} | ${i.width}x${i.height} | ${lic} | ${(i.extmetadata?.Artist?.value || '').replace(/<[^>]+>/g, '').trim().slice(0, 30)}`);
    }
  } catch (e) { console.log('  ERR ' + txt.slice(0, 100)); }
  await sleep(2500);
}
