// Runs in the Google Flow project page (javascript_tool). IDS = [[id, prompt prefix]] from
// `batch.py ids`. Downloads each generated image (full size, =s0) as nhp_<id>.webp into
// ~/Downloads, matching the chat image's alt text (the prompt) to the prefix; returns what it found.
async function nhFetch(IDS) {
  // the chat shows only the first four images of each answer until "See all" is clicked
  for (const b of [...document.querySelectorAll('button')].filter(b => b.innerText.trim() === 'See all')) b.click();
  await new Promise(r => setTimeout(r, 1500));
  const imgs = [...document.querySelectorAll('img[alt]')].filter(i => i.src.includes('/asb/'));
  const norm = s => s.replace(/\s+/g, ' ').trim().toLowerCase();
  const done = [], missing = [];
  for (const [id, prefix] of IDS) {
    const im = imgs.find(i => norm(i.alt).startsWith(norm(prefix)));
    if (!im) { missing.push(id); continue; }
    const url = im.src.replace(/=s\d+(-rw)?/, '=s0');
    const blob = await (await fetch(url)).blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `nhp_${id}.${blob.type.includes('png') ? 'png' : blob.type.includes('webp') ? 'webp' : 'jpg'}`;
    document.body.appendChild(a); a.click(); a.remove();
    await new Promise(r => setTimeout(r, 300));
    done.push(id);
  }
  return { done: done.length, missing };
}
