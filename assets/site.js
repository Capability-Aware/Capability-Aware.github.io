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

// Muting before play also supports browsers that inspect the runtime property.
document.querySelectorAll('.video-track video').forEach((video) => {
  video.muted = true;
  video.play().catch(() => { /* Native controls remain available. */ });
});
