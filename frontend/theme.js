/* ========================================
   NewsHub — Theme Manager
   Toggle claro/escuro com persistência
   ======================================== */

(function () {
  // Aplicar tema guardado antes de renderizar (evita flash)
  const saved = localStorage.getItem('nh-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (saved === 'dark' || (!saved && prefersDark)) {
    document.documentElement.classList.add('dark');
  }
})();

function initThemeToggle() {
  const btn = document.getElementById('themeToggleBtn');
  if (!btn) return;

  function updateIcon() {
    const isDark = document.documentElement.classList.contains('dark');
    btn.innerHTML = isDark ? getSunIcon() : getMoonIcon();
    btn.setAttribute('aria-label', isDark ? 'Mudar para tema claro' : 'Mudar para tema escuro');
    btn.title = isDark ? 'Tema claro' : 'Tema escuro';
  }

  btn.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    localStorage.setItem('nh-theme', isDark ? 'dark' : 'light');
    updateIcon();
  });

  updateIcon();
}

function getSunIcon() {
  return `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <circle cx="12" cy="12" r="4"/>
    <path stroke-linecap="round" d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
  </svg>`;
}

function getMoonIcon() {
  return `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
  </svg>`;
}

document.addEventListener('DOMContentLoaded', initThemeToggle);
