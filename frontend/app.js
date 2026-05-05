/* ========================================
   NewsHub — Frontend Logic (app.js)
   Comunicação com Backend, Gestão de UI
   ======================================== */

// === CONFIGURAÇÃO E CONSTANTES ===
const BASE_URL = 'http://localhost:5000/api';

// Mapeamento de categorias para cores
const CATEGORY_COLORS = {
  'tecnologia': 'tech',
  'desporto': 'sport',
  'saude': 'health',
  'ciencia': 'science',
  'negocios': 'business',
  'entretenimento': 'entertainment',
  'geral': 'tech'
};

// Estado global
let currentCategory = 'geral';
let currentPage = 1;
let currentQuery = '';
let currentUser = null;

// === FUNÇÕES AUXILIARES ===

/**
 * Formata data ISO para texto relativo em português
 * Ex: "há 2 horas", "ontem", "3 Mai 2025"
 */
function formatDate(isoString) {
  if (!isoString) return '';

  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return 'agora mesmo';
  if (diffMins < 60) return `há ${diffMins} minuto${diffMins !== 1 ? 's' : ''}`;
  if (diffHours < 24) return `há ${diffHours} hora${diffHours !== 1 ? 's' : ''}`;
  if (diffDays === 1) return 'ontem';
  if (diffDays < 7) return `há ${diffDays} dias`;

  // Formato: "3 Mai 2025"
  const months_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
  return `${date.getDate()} ${months_pt[date.getMonth()]} ${date.getFullYear()}`;
}

/**
 * Mostra notificação toast
 */
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.getElementById('toast');
  if (!toast) return;

  toast.textContent = message;
  toast.className = `toast ${type} visible`;

  setTimeout(() => {
    toast.classList.remove('visible');
  }, duration);
}

/**
 * Define estado de loading em um botão
 */
function setButtonLoading(button, isLoading, originalText = null) {
  if (!button) return;
  
  if (!originalText) {
    originalText = button.dataset.originalText || button.textContent;
    button.dataset.originalText = originalText;
  }
  
  if (isLoading) {
    button.disabled = true;
    button.classList.add('loading');
    button.textContent = 'A processar...';
  } else {
    button.disabled = false;
    button.classList.remove('loading');
    button.textContent = originalText;
  }
}

/**
 * Tratamento centralizado de erros de fetch
 */
async function fetchAPI(endpoint, options = {}) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      credentials: 'include',
      ...options
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Erro em ${endpoint}:`, error);
    throw error;
  }
}

// === AUTENTICAÇÃO ===

/**
 * Verifica se o utilizador está autenticado
 * Retorna true se autenticado, false caso contrário
 */
async function checkAuth() {
  try {
    const response = await fetch(`${BASE_URL}/auth/me`, {
      credentials: 'include'
    });

    if (!response.ok) {
      currentUser = null;
      return false;
    }

    const data = await response.json();
    currentUser = data;
    if (document.getElementById('userNameDisplay')) {
      document.getElementById('userNameDisplay').textContent = data.name || 'Utilizador';
    }
    return true;
  } catch (error) {
    console.error('Erro na verificação de autenticação:', error);
    currentUser = null;
    return false;
  }
}

/**
 * Regista um novo utilizador
 */
async function handleRegister(name, email, password) {
  const button = document.querySelector('#registerForm button[type="submit"]');
  
  try {
    setButtonLoading(button, true);
    
    const data = await fetchAPI('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password })
    });

    showToast('✅ Conta criada com sucesso! Redirecionando...', 'success');
    setTimeout(() => {
      window.location.href = 'index.html';
    }, 1500);
  } catch (error) {
    setButtonLoading(button, false);
    
    // Decompor mensagem de erro
    const errorMsg = error.message;
    if (errorMsg.includes('email')) {
      document.getElementById('emailError').textContent = 'Email já está registado ou inválido';
      document.getElementById('emailError').classList.add('visible');
    } else if (errorMsg.includes('password')) {
      document.getElementById('passwordError').textContent = errorMsg.split(': ')[1] || 'Palavra-passe inválida';
      document.getElementById('passwordError').classList.add('visible');
    } else {
      document.getElementById('generalError').textContent = errorMsg;
      document.getElementById('generalError').classList.add('visible');
    }
    
    showToast(`❌ Erro: ${errorMsg}`, 'error');
  }
}

/**
 * Login de utilizador
 */
async function handleLogin(email, password) {
  const button = document.querySelector('#loginForm button[type="submit"]');
  
  try {
    setButtonLoading(button, true);
    
    const data = await fetchAPI('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    currentUser = data;
    showToast('✅ Login bem-sucedido! Redirecionando...', 'success');
    setTimeout(() => {
      window.location.href = 'index.html';
    }, 1500);
  } catch (error) {
    setButtonLoading(button, false);
    document.getElementById('generalError').textContent = 'Email ou palavra-passe incorretos';
    document.getElementById('generalError').classList.add('visible');
    showToast('❌ Falha no login', 'error');
  }
}

/**
 * Logout de utilizador
 */
async function handleLogout() {
  try {
    await fetchAPI('/auth/logout', { method: 'POST' });
    currentUser = null;
    showToast('✅ Sessão terminada', 'info');
    setTimeout(() => {
      window.location.href = 'login.html';
    }, 800);
  } catch (error) {
    console.error('Erro ao fazer logout:', error);
    window.location.href = 'login.html';
  }
}

// === CARREGAMENTO DE NOTÍCIAS ===

/**
 * Cria um card de notícia dinamicamente
 */
function createNewsCard(article) {
  const categoryColor = CATEGORY_COLORS[article.category?.toLowerCase()] || 'tech';
  const imageUrl = article.urlToImage || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23e0e0e0" width="400" height="300"/%3E%3Ctext x="50%" y="50%" font-size="24" fill="%23999" text-anchor="middle" dominant-baseline="middle"%3E📰%3C/text%3E%3C/svg%3E';

  const card = document.createElement('article');
  card.className = 'news-card';
  card.innerHTML = `
    <a href="${article.url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; color: inherit;">
      <img 
        src="${imageUrl}" 
        alt="${article.title}" 
        class="news-card-image"
        loading="lazy"
        onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect fill=%22%23e0e0e0%22 width=%22400%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 font-size=%2224%22 fill=%22%23999%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22%3E📰%3C/text%3E%3C/svg%3E'"
      >
    </a>
    
    <div class="news-card-content">
      <span class="news-card-category ${categoryColor}">${article.category || 'Geral'}</span>
      
      <h3 class="news-card-title">
        <a href="${article.url}" target="_blank" rel="noopener noreferrer">${article.title}</a>
      </h3>
      
      <p class="news-card-description">${article.description || 'Sem descrição disponível'}</p>
      
      <div class="news-card-footer">
        <div>
          <span class="news-card-source">${article.source?.name || 'Fonte desconhecida'}</span>
          <br>
          <span>${formatDate(article.publishedAt)}</span>
        </div>
        <div class="news-card-actions">
          <button 
            class="btn-icon btn-favorite ${article.isFavorite ? 'favorite' : ''}" 
            title="${article.isFavorite ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}"
            data-article='${JSON.stringify(article)}'
            onclick="toggleFavorite(this)"
            aria-label="${article.isFavorite ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}"
          >
            <span class="fav-icon-wrap">
              ${article.isFavorite
                ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>`
                : `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="17" height="17"><path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>`
              }
              <span class="fav-badge">${article.isFavorite ? '✓' : '+'}</span>
            </span>
          </button>
          <button 
            class="btn-icon" 
            title="Ver resumo com IA"
            data-title="${article.title}"
            data-description="${article.description}"
            data-url="${article.url}"
            onclick="handleShowSummary(this)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="18" height="18"><path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
          </button>
        </div>
      </div>
    </div>
  `;

  return card;
}

/**
 * Carrega notícias da API
 */
async function loadNews(category = 'geral', page = 1, query = '') {
  try {
    currentCategory = category;
    currentPage = page;
    currentQuery = query;

    // Mostrar spinner
    const spinner = document.getElementById('loadingSpinner');
    const grid = document.getElementById('newsGrid');
    const emptyState = document.getElementById('emptyState');
    const errorState = document.getElementById('errorState');

    if (page === 1) {
      spinner.classList.add('visible');
      grid.innerHTML = '';
      emptyState.style.display = 'none';
      errorState.style.display = 'none';
    }

    // Construir query string
    let endpoint;
    if (query) {
      // Pesquisa: usar apenas 'q', ignore category
      endpoint = `/news?q=${encodeURIComponent(query)}&page=${page}`;
    } else {
      // Categoria: usar 'category'
      endpoint = `/news?category=${category}&page=${page}`;
    }

    const data = await fetchAPI(endpoint);

    // Ocultar spinner
    spinner.classList.remove('visible');

    // Actualizar título
    const titleMap = {
      'geral': 'Notícias em Destaque',
      'tecnologia': '💻 Tecnologia',
      'desporto': '⚽ Desporto',
      'saude': '🏥 Saúde',
      'ciencia': '🔬 Ciência',
      'negocios': '💼 Negócios',
      'entretenimento': '🎭 Entretenimento'
    };
    document.getElementById('newsSectionTitle').textContent = titleMap[category] || 'Notícias';

    // Processar artigos
    if (data.articles && data.articles.length > 0) {
      data.articles.forEach(article => {
        const card = createNewsCard(article);
        grid.appendChild(card);
      });

      // Mostrar botão "Carregar mais"
      const loadMoreBtn = document.getElementById('loadMoreBtn');
      loadMoreBtn.style.display = data.hasMore ? 'block' : 'none';

      errorState.style.display = 'none';
      emptyState.style.display = 'none';
    } else {
      if (page === 1) {
        emptyState.style.display = 'block';
        const emptyMsg = query 
          ? `Nenhuma notícia encontrada para "${query}"` 
          : 'Nenhuma notícia disponível nesta categoria';
        document.getElementById('emptyState').innerHTML = `
          <div style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">📰</div>
            <h3>Sem notícias</h3>
            <p>${emptyMsg}</p>
          </div>
        `;
        document.getElementById('loadMoreBtn').style.display = 'none';
      }
    }
  } catch (error) {
    console.error('Erro ao carregar notícias:', error);
    document.getElementById('loadingSpinner').classList.remove('visible');
    
    let errorMsg = 'Não foi possível carregar as notícias';
    if (error.message.includes('API')) {
      errorMsg = 'Serviço de notícias indisponível. Tenta novamente em breve.';
    } else if (error.message.includes('rede')) {
      errorMsg = 'Problemas de conexão. Verifica a tua internet.';
    }
    
    document.getElementById('errorMessage').textContent = errorMsg;
    document.getElementById('errorState').style.display = 'block';
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('loadMoreBtn').style.display = 'none';
    
    showToast(`❌ ${errorMsg}`, 'error', 4000);
  }
}

/**
 * Carrega notícias personalizadas (secção "Para si")
 */
async function loadPersonalizedNews() {
  try {
    const preferences = await loadPreferences();
    
    if (!preferences || preferences.length === 0) {
      document.getElementById('personalizedSection').style.display = 'none';
      return;
    }

    const data = await fetchAPI(`/news/personalized`);

    if (data.articles && data.articles.length > 0) {
      const grid = document.getElementById('personalizedGrid');
      grid.innerHTML = '';

      // Mostrar apenas os primeiros 3
      data.articles.slice(0, 3).forEach(article => {
        const card = createNewsCard(article);
        grid.appendChild(card);
      });

      document.getElementById('personalizedSection').style.display = 'block';
    } else {
      document.getElementById('personalizedSection').style.display = 'none';
    }
  } catch (error) {
    console.error('Erro ao carregar notícias personalizadas:', error);
    document.getElementById('personalizedSection').style.display = 'none';
  }
}

const HEART_FILLED = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>`;
const HEART_OUTLINE = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="18" height="18"><path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>`;

// === FAVORITOS ===

/**
 * Alterna o estado de favorito de um artigo
 */
async function toggleFavorite(button) {
  try {
    const articleJson = button.dataset.article;
    const article = JSON.parse(articleJson);
    const isFavorite = button.classList.contains('favorite');

    // Optimistic update
    button.classList.toggle('favorite');
    const nowFav = button.classList.contains('favorite');
    button.innerHTML = `<span class="fav-icon-wrap">
      ${nowFav
        ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>`
        : `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="17" height="17"><path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>`
      }
      <span class="fav-badge">${nowFav ? '✓' : '+'}</span>
    </span>`;
    button.title = nowFav ? 'Remover dos favoritos' : 'Adicionar aos favoritos';

    if (isFavorite) {
      // Remover dos favoritos
      const response = await fetch(`${BASE_URL}/favorites/${article.id}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (!response.ok) {
        // Revert
        button.classList.toggle('favorite');
        button.innerHTML = `<span class="fav-icon-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg><span class="fav-badge">✓</span></span>`;
        throw new Error('Erro ao remover favorito');
      }

      showToast('✅ Removido dos favoritos', 'info');
    } else {
      // Adicionar aos favoritos
      const response = await fetch(`${BASE_URL}/favorites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: article.title,
          description: article.description,
          urlToImage: article.urlToImage,
          source_name: article.source?.name,
          url: article.url,
          category: article.category,
          published_at: article.publishedAt
        })
      });

      if (!response.ok) {
        // Revert
        button.classList.toggle('favorite');
        button.innerHTML = `<span class="fav-icon-wrap"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="17" height="17"><path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg><span class="fav-badge">+</span></span>`;
        throw new Error('Erro ao adicionar favorito');
      }

      showToast('✅ Adicionado aos favoritos', 'success');
    }
  } catch (error) {
    console.error('Erro ao alternar favorito:', error);
    showToast('❌ Não foi possível atualizar favorito', 'error');
  }
}

/**
 * Carrega resumo IA do backend
 */
async function loadSummary(url, title, description) {
  try {
    const modal = document.getElementById('summaryModal');
    const spinner = document.getElementById('summarySpinner');
    const content = document.getElementById('summaryContent');

    const data = await fetchAPI('/ai/summary', {
      method: 'POST',
      body: JSON.stringify({ url, title, description })
    });

    spinner.classList.remove('visible');
    content.textContent = data.summary || 'Resumo não disponível.';
    content.style.display = 'block';
  } catch (error) {
    spinner.classList.remove('visible');
    content.textContent = '❌ Erro ao gerar resumo. Tenta novamente em breve.';
    content.style.display = 'block';
  }
}
}

/**
 * Carrega todos os favoritos do utilizador
 */
async function loadFavorites() {
  try {
    const spinner = document.getElementById('loadingSpinner');
    const grid = document.getElementById('favoritesGrid');
    const emptyState = document.getElementById('emptyState');
    const errorState = document.getElementById('errorState');

    spinner.classList.add('visible');
    grid.innerHTML = '';

    const data = await fetchAPI('/favorites');

    spinner.classList.remove('visible');

    if (data.favorites && data.favorites.length > 0) {
      data.favorites.forEach(favorite => {
        const article = {
          id: favorite.id,
          title: favorite.title,
          description: favorite.description,
          urlToImage: favorite.url_to_image,
          source: { name: favorite.source_name },
          publishedAt: favorite.published_at,
          url: favorite.url,
          category: favorite.category,
          isFavorite: true
        };
        const card = createNewsCard(article);
        grid.appendChild(card);
      });

      emptyState.style.display = 'none';
      errorState.style.display = 'none';
    } else {
      emptyState.style.display = 'block';
      errorState.style.display = 'none';
    }
  } catch (error) {
    console.error('Erro ao carregar favoritos:', error);
    document.getElementById('loadingSpinner').classList.remove('visible');
    document.getElementById('errorMessage').textContent = error.message;
    document.getElementById('errorState').style.display = 'block';
    document.getElementById('emptyState').style.display = 'none';
  }
}

// === RESUMO IA ===

/**
 * Mostra modal com resumo IA
 */
async function handleShowSummary(button) {
  const title = button.dataset.title;
  const description = button.dataset.description;
  const url = button.dataset.url;

  const modal = document.getElementById('summaryModal');
  const spinner = document.getElementById('summarySpinner');
  const content = document.getElementById('summaryContent');

  modal.classList.add('visible');
  spinner.classList.add('visible');
  content.style.display = 'none';

  try {
    await loadSummary(url, title, description);
    showToast('✅ Resumo gerado com sucesso!', 'success', 2000);
  } catch (error) {
    console.error('Erro ao carregar resumo:', error);
    spinner.classList.remove('visible');
    content.textContent = '❌ Serviço de IA indisponível. Tenta novamente em breve.';
    content.style.display = 'block';
    showToast('❌ Não foi possível gerar o resumo', 'error', 3000);
  }
}

// === PREFERÊNCIAS ===

/**
 * Carrega preferências do utilizador
 */
async function loadPreferences() {
  try {
    const data = await fetchAPI('/preferences');
    return data.categories || [];
  } catch (error) {
    console.error('Erro ao carregar preferências:', error);
    return [];
  }
}

/**
 * Inicializa a navbar com categorias
 */
async function initNavbarCategories() {
  const categories = [
    { id: 'geral', label: 'Geral' },
    { id: 'tecnologia', label: 'Tecnologia' },
    { id: 'desporto', label: 'Desporto' },
    { id: 'saude', label: 'Saúde' },
    { id: 'ciencia', label: 'Ciência' },
    { id: 'negocios', label: 'Negócios' },
    { id: 'entretenimento', label: 'Entretenimento' }
  ];

  const categoryList = document.getElementById('navbarCategories');
  if (!categoryList) return;

  categoryList.innerHTML = '';

  categories.forEach(cat => {
    const li = document.createElement('li');
    const button = document.createElement('button');
    button.textContent = cat.label;
    button.className = cat.id === currentCategory ? 'active' : '';
    button.addEventListener('click', () => {
      currentPage = 1;
      currentQuery = '';
      document.getElementById('searchInput').value = '';
      
      // Remover classe active de todos os botões
      document.querySelectorAll('.navbar-categories button').forEach(b => {
        b.classList.remove('active');
      });
      button.classList.add('active');
      
      loadNews(cat.id, 1);
    });
    li.appendChild(button);
    categoryList.appendChild(li);
  });
}

// === HANDLERS DE EVENTOS ===

/**
 * Handler para tentar carregar notícias novamente
 */
function handleRetry() {
  loadNews(currentCategory, currentPage, currentQuery);
}

/**
 * Handler para processar busca
 */
function handleSearch(event) {
  event.preventDefault();
  const query = document.getElementById('searchInput').value.trim();
  
  if (!query) {
    showToast('⚠️ Escreve uma palavra-chave para pesquisar', 'warning');
    return;
  }
  
  if (!currentQuery || currentQuery !== query) {
    currentQuery = query;
    currentPage = 1;
    
    // Adicionar loading state
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
      searchForm.classList.add('loading');
      
      loadNews(currentCategory, 1, query).finally(() => {
        searchForm.classList.remove('loading');
      });
    }
  }
}

/**
 * Handler para carregar mais notícias
 */
function handleLoadMore() {
  const button = document.getElementById('loadMoreBtn');
  if (!button || button.dataset.loading) return;
  
  button.dataset.loading = 'true';
  currentPage++;
  
  loadNews(currentCategory, currentPage, currentQuery).finally(() => {
    delete button.dataset.loading;
  });
}

// === INICIALIZAÇÃO ===

/**
 * Executa ao carregar a página
 */
document.addEventListener('DOMContentLoaded', async () => {
  // Inicializar navbar categorias (funciona em todas as páginas)
  await initNavbarCategories();

  // Event listener para botão "Tentar Novamente"
  const retryButton = document.getElementById('retryButton');
  if (retryButton) {
    retryButton.addEventListener('click', () => {
      loadNews(currentCategory, currentPage, currentQuery);
    });
  }

  // Event listener para form de pesquisa (apenas em index.html)
  const searchForm = document.getElementById('searchForm');
  if (searchForm) {
    searchForm.addEventListener('submit', handleSearch);
  }

  // Event listener para botão "Carregar mais" (apenas em index.html)
  const loadMoreBtn = document.getElementById('loadMoreBtn');
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', handleLoadMore);
  }
});
