/* ========================================
   NewsHub — Theme Manager
   Toggle claro/escuro com persistência
   ======================================== */

// Aplicar tema ANTES de renderizar (evita flash branco/preto)
// Padrão: CLARO. Só aplica escuro se o utilizador escolheu explicitamente.
(function () {
  const saved = localStorage.getItem('nh-theme');
  if (saved === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
})();

function getSunIcon(size) {
  return `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="${size}" height="${size}">
    <circle cx="12" cy="12" r="4"/>
    <path stroke-linecap="round" d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
  </svg>`;
}

function getMoonIcon(size) {
  return `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="${size}" height="${size}">
    <path stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
  </svg>`;
}

function applyTheme(isDark) {
  if (isDark) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  localStorage.setItem('nh-theme', isDark ? 'dark' : 'light');
}

function updateToggleBtn(btn) {
  if (!btn) return;
  const isDark = document.documentElement.classList.contains('dark');
  // Navbar usa ícone branco (18px), auth usa ícone colorido (20px)
  const isAuthPage = btn.closest('.auth-page') !== null || btn.style.color === 'var(--color-primary)';
  const size = isAuthPage ? 20 : 18;
  btn.innerHTML = isDark ? getSunIcon(size) : getMoonIcon(size);
  btn.setAttribute('aria-label', isDark ? 'Mudar para tema claro' : 'Mudar para tema escuro');
  btn.title = isDark ? 'Tema claro' : 'Tema escuro';
}

function initThemeToggle() {
  const btn = document.getElementById('themeToggleBtn');
  if (!btn) return;

  updateToggleBtn(btn);

  btn.addEventListener('click', () => {
    const isDark = !document.documentElement.classList.contains('dark');
    applyTheme(isDark);
    updateToggleBtn(btn);
  });
}

document.addEventListener('DOMContentLoaded', initThemeToggle);
