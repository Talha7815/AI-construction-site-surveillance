const apiBase = location.port === '4173' ? 'http://127.0.0.1:8000' : '';
const nativeFetch = window.fetch.bind(window);
window.fetch = (input, init) => {
  if (typeof input === 'string' && input.startsWith('/api/')) input = `${apiBase}${input}`;
  return nativeFetch(input, init);
};

document.addEventListener('DOMContentLoaded', async () => {
  const status = document.querySelector('.system-pill strong');
  const dot = document.querySelector('.system-pill i');
  const notice = document.querySelector('.notice');
  try {
    const response = await fetch(`${apiBase}/api/health`);
    const health = await response.json();
    if (!health.pipeline_configured) throw new Error('Pipeline unavailable');
    if (status) status.textContent = 'Connected';
    if (dot) dot.style.background = 'var(--good)';
    if (notice) notice.remove();
  } catch {
    if (status) status.textContent = 'Unavailable';
  }
});
