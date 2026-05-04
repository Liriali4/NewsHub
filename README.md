# NewsHub — Agregador de Notícias Inteligente

Uma aplicação web moderna de agregação de notícias com funcionalidades inteligentes de IA, autenticação de utilizadores, e personalização de preferências.

## 🎯 Características

- ✅ Autenticação segura com hash bcrypt
- ✅ Agregação de notícias em tempo real via NewsAPI.org
- ✅ Filtro por 6 categorias (Tecnologia, Desporto, Saúde, Ciência, Negócios, Entretenimento)
- ✅ Sistema de favoritos persistente
- ✅ Notícias personalizadas baseadas em preferências
- ✅ Resumos inteligentes com IA (OpenAI)
- ✅ Interface responsiva (desktop, tablet, mobile)
- ✅ Busca de notícias por palavra-chave
- ✅ Modo escuro automático

## 📋 Pré-requisitos

- **Python 3.9+**
- **pip** (gestor de pacotes Python)
- **Navegador web moderno** (Chrome, Firefox, Safari, Edge)
- **Chave API NewsAPI.org** (gratuita com limite de 100 pedidos/dia)

## 🚀 Instalação

### 1. Clonar/Preparar o Projecto

```bash
# Navegar para a pasta do projeto
cd newshub
```

### 2. Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar ficheiro de exemplo
cp .env.example .env

# Editar .env e preencher:
# - NEWS_API_KEY=sua_chave_aqui
# - SECRET_KEY=gera_uma_chave_aleatoria
```

### 5. Inicializar a Base de Dados

```bash
# Criar tabelas
python database/db_manager.py init

# (Opcional) Inserir dados de teste
python database/db_manager.py seed
```

## 🔑 Como Obter a Chave de API de Notícias

1. Aceder a [news api.org](https://newsapi.org)
2. Clicar em "Get API Key"
3. Registar-se gratuitamente
4. Copiar a chave e colocar em `.env` como `NEWS_API_KEY=...`

**Limite Gratuito:** 100 pedidos/dia

## ▶️ Executar a Aplicação

### Terminal 1 — Backend (Flask)

```bash
python backend/app.py
```

O servidor estará disponível em `http://localhost:5000`

### Terminal 2 — Frontend (Servidor Web)

```bash
# Opção 1: Usar o Live Server do VS Code
# Clicar direito em frontend/index.html → "Open with Live Server"

# Opção 2: Usar Python SimpleHTTPServer
cd frontend
python -m http.server 5500
```

A aplicação estará disponível em `http://localhost:5500/index.html`

## 📁 Estrutura do Projecto

```
newshub/
├── frontend/               # Aplicação web (HTML/CSS/JavaScript)
│   ├── index.html         # Dashboard principal
│   ├── login.html         # Página de login
│   ├── register.html      # Página de registo
│   ├── favorites.html     # Página de favoritos
│   ├── preferences.html   # Página de preferências
│   ├── styles.css         # Estilos CSS (sistema de design)
│   └── app.js             # Lógica JavaScript e API calls
│
├── backend/               # Servidor Flask (Python)
│   ├── app.py            # Aplicação principal
│   ├── auth.py           # Blueprint de autenticação
│   ├── news.py           # Blueprint de notícias
│   ├── categories.py     # Blueprint de preferências
│   ├── favorites.py      # Blueprint de favoritos
│   └── db.py             # Gestão de base de dados
│
├── database/              # Dados e schema
│   ├── schema.sql        # Definição das tabelas
│   ├── newshub.db        # Ficheiro da BD (SQLite)
│   └── db_manager.py     # Script de gestão da BD
│
├── utils/                 # Utilitários compartilhados
│   ├── validators.py     # Validação de inputs
│   ├── error_handlers.py # Tratamento de erros
│   └── ai_features.py    # Funcionalidades de IA
│
├── tests/                 # Testes
│   └── test_routes.py    # Testes de rotas (manual)
│
├── requirements.txt       # Dependências Python
├── .env.example          # Variáveis de ambiente (exemplo)
└── README.md             # Este ficheiro
```

## 🧪 Testes

### Testar Rotas do Backend

```bash
# Certifique-se que o servidor Flask está em execução
python tests/test_routes.py
```

Resultado esperado: **14/14 testes passam ✅**

### Testar Diagnostico do Sistema

```bash
python utils/health_check.py
```

## 📊 API Endpoints

### Autenticação
- `POST /api/auth/register` — Registar novo utilizador
- `POST /api/auth/login` — Fazer login
- `POST /api/auth/logout` — Fazer logout
- `GET /api/auth/me` — Dados do utilizador autenticado

### Notícias
- `GET /api/news?category=X&page=Y` — Listar notícias
- `GET /api/news/personalized` — Notícias personalizadas

### Preferências
- `GET /api/preferences` — Obter preferências
- `PUT /api/preferences` — Guardar preferências

### Favoritos
- `GET /api/favorites` — Listar favoritos
- `POST /api/favorites` — Adicionar favorito
- `DELETE /api/favorites/<id>` — Remover favorito

### IA
- `POST /api/ai/summary` — Gerar resumo inteligente

## 🔐 Segurança

- Passwords armazenadas com hash **bcrypt** (nunca em texto simples)
- Sessões HTTP-only e SameSite=Lax
- CORS configurado para localhost apenas
- Validação de inputs em todos os endpoints
- Proteção contra duplicação de favoritos/preferências

## 🎨 Sistema de Design

- **Paleta de cores:** Azul (#1a3557) + Branco + Cinzento claro
- **Grid responsivo:** 3 colunas (desktop), 2 (tablet), 1 (mobile)
- **Tipografia:** System fonts (Inter, Roboto, etc.)
- **Modo escuro:** Automático via `prefers-color-scheme`
- **Animações:** Suave com transições CSS

## 📝 Conta de Teste

Se inicializou com `python database/db_manager.py seed`:

- **Email:** `joao@example.com`
- **Password:** `password123`

## 🐛 Troubleshooting

### Erro: "Cannot GET /api/news"
- Certifique-se que o servidor Flask está em execução (`python backend/app.py`)

### Erro: "API Key inválida"
- Verifique que tem `NEWS_API_KEY` em `.env`
- Confirme que a chave foi copiada correctamente do newsapi.org

### Erro: "Nenhuma notícia encontrada (429)"
- Excedeu o limite diário de 100 pedidos
- O limite repõe-se às 00:00 UTC

### Base de Dados Corrompida
```bash
# Repor base de dados (apaga todos os dados)
python database/db_manager.py reset
```

## 📈 Roadmap Futuro

- [ ] Integração com múltiplas APIs de notícias
- [ ] Exportação de favoritos para PDF
- [ ] Partilha em redes sociais
- [ ] App mobile nativa
- [ ] Notificações push
- [ ] Análise de sentimento avançada
- [ ] Sistema de comentários

## 👥 Membros do Grupo

| Nome | Responsabilidade | Prompts |
|------|------------------|---------|
| [Membro 1] | Frontend | F-1, F-2, F-3, F-4 |
| [Membro 2] | Backend | B-1, B-2, B-3, B-4 |
| [Membro 3] | API + IA | A-1, A-2, A-3, A-4 |
| [Membro 4] | Database + QA | D-1, D-2, D-3, D-4 |

## 📄 Licença

Este projecto foi desenvolvido como trabalho académico e é fornecido "tal como está".

## 📞 Contacto

Para dúvidas ou problemas, consulte o(a) orientador(a) ou crie uma issue no repositório.

---

**Última actualização:** Maio de 2025  
**Versão:** 1.0.0
