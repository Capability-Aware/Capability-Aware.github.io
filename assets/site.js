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
