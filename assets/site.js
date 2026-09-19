const copyButton = document.querySelector('[data-copy-citation]');
if (copyButton) {
  copyButton.addEventListener('click', async () => {
    const citation = document.getElementById('citation');
    const status = document.getElementById('copy-status');
    try {
      await navigator.clipboard.writeText(citation.textContent);
      status.textContent = 'Citation copied.';
      copyButton.textContent = 'Copied';
      setTimeout(() => { copyButton.textContent = 'Copy BibTeX'; }, 2500);
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(citation);
      selection.removeAllRanges();
      selection.addRange(range);
      status.textContent = 'Citation selected. Press Command+C or Ctrl+C to copy.';
    }
  });
}

const projectMenu = document.querySelector('.project-menu');
document.addEventListener('click', (event) => {
  if (projectMenu && !projectMenu.contains(event.target)) projectMenu.open = false;
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && projectMenu?.open) {
    projectMenu.open = false;
    projectMenu.querySelector('summary').focus();
  }
});
document.querySelectorAll('[data-scroll]').forEach((button) => {
  button.addEventListener('click', () => {
    const track = document.querySelector('.video-track');
    track.scrollBy({left: Number(button.dataset.scroll) * 260,
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  });
});

const showcase = document.getElementById('showcase-video');
const clips = document.querySelectorAll('[data-video]');
if (showcase) {
  clips.forEach((clip) => {
    if (clip.href === showcase.querySelector('source')?.src) clip.setAttribute('aria-current', 'true');
  });
  clips.forEach((clip) => clip.addEventListener('click', (event) => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    showcase.pause();
    showcase.poster = clip.dataset.poster;
    showcase.src = clip.dataset.video;
    showcase.setAttribute('aria-label', clip.dataset.title);
    document.getElementById('video-title').textContent = clip.dataset.title;
    document.getElementById('video-direct').href = clip.dataset.video;
    clips.forEach((item) => item.removeAttribute('aria-current'));
    clip.setAttribute('aria-current', 'true');
    showcase.load();
    showcase.play().catch(() => {});
  }));
}
