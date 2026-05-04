# NewsHub — Guia Completo de Execução e Testes

Este documento explica passo a passo como configurar, executar e testar o projeto `newshub`.

---

## 1. Visão Geral do Projeto

O projeto `newshub` é um agregador de notícias em Python/Flask com frontend estático em HTML/CSS/JavaScript.

Componentes principais:
- `backend/` — servidor Flask com rotas de autenticação, notícias, preferências, favoritos e IA.
- `frontend/` — páginas web estáticas para login, registo, dashboard, favoritos e preferências.
- `database/` — arquivo SQLite, manager de BD e schema SQL.
- `utils/` — utilitários de validação, tratamento de erros e IA.
- `tests/` — testes de rotas do backend.

---

## 2. Pré-requisitos

Antes de começar, instale:

- Python 3.9 ou superior
- `pip`
- Navegador moderno (Chrome, Firefox, Edge etc.)

---

## 3. Preparar o ambiente

### 3.1. Abrir terminal

Abra o terminal e navegue até a pasta do projeto:

```bash
cd e:\3ANO\ES2\Lab3_part2\newshub
```

### 3.2. Criar ambiente virtual

No Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

No macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.3. Instalar dependências

Com o ambiente virtual ativo, execute:

```bash
pip install -r requirements.txt
```

---

## 4. Configurar variáveis de ambiente

Copie o ficheiro de exemplo e configure as chaves:

No Windows PowerShell:

```powershell
copy .env.example .env
```

No macOS/Linux:

```bash
cp .env.example .env
```

Abra o arquivo `.env` e defina pelo menos:

```env
NEWS_API_KEY=YOUR_NEWSAPI_KEY
SECRET_KEY=uma_chave_secreta_aleatoria
```

> Se não tiver `NEWS_API_KEY`, pode usar a aplicação apenas com funcionalidades locais ou de teste, mas a consulta real ao NewsAPI não funcionará.

---

## 5. Inicializar a base de dados

O projeto usa `database/newshub.db` em SQLite. Crie as tabelas com:

```bash
python database/db_manager.py init
```

### 5.1. Popular dados de teste (opcional)

Se quiser dados de utilizador e favoritos já prontos:

```bash
python database/db_manager.py seed
```

Usuário de teste criado:
- email: `joao@example.com`
- password: `password123`

### 5.2. Comandos adicionais do DB Manager

- `python database/db_manager.py reset` — reinicia a base de dados
- `python database/db_manager.py backup` — cria backup do arquivo SQLite
- `python database/db_manager.py stats` — mostra estatísticas da base de dados

---

## 6. Executar o backend

No terminal com o ambiente virtual ativo, inicie o servidor Flask:

```bash
python backend/app.py
```

O servidor ficará disponível em:

- `http://localhost:5000`

### Endpoints importantes

- `/api/health`
- `/api/auth/login`
- `/api/auth/register`
- `/api/auth/me`
- `/api/news`
- `/api/news/personalized`
- `/api/preferences`
- `/api/favorites`
- `/api/ai/summary`

---

## 7. Executar o frontend

O frontend é estático e pode ser servido com um servidor simples.

### Opção 1: Usar `python -m http.server`

No terminal, vá para a pasta `frontend`:

```bash
cd frontend
python -m http.server 5500
```

Abra no navegador:

- `http://localhost:5500/index.html`

### Opção 2: Usar Live Server do VS Code

Se tiver extensão Live Server instalada, abra `frontend/index.html` e clique em "Open with Live Server".

---

## 8. Como testar a aplicação

### 8.1. Testar o servidor Flask

Execute os testes de rotas no terminal:

```bash
python tests/test_routes.py
```

Verifique se os testes passam e se não existem erros de importação.

### 8.2. Testar manualmente

No navegador:
1. Abra `http://localhost:5500/index.html`
2. Faça registo ou login
3. Verifique as preferências de categoria
4. Adicione/visualize favoritos
5. Teste o carregamento de notícias e busca

### 8.3. Verificar Health Check

No navegador ou `curl`:

```bash
curl http://localhost:5000/api/health
```

Deve retornar JSON com `status: ok`.

---

## 9. Estrutura de ficheiros

```
newshub/
├── backend/
│   ├── app.py
│   ├── auth.py
│   ├── categories.py
│   ├── db.py
│   ├── favorites.py
│   └── news.py
├── database/
│   ├── db_manager.py
│   └── schema.sql
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── favorites.html
│   ├── preferences.html
│   ├── styles.css
│   └── app.js
├── tests/
│   └── test_routes.py
├── utils/
│   ├── ai_features.py
│   ├── error_handlers.py
│   └── validators.py
├── requirements.txt
├── .env.example
├── README.md
└── GUIDE.md
```

---

## 10. Dicas rápidas

- Sempre ative o `venv` antes de executar comandos Python.
- Se o backend não iniciar, verifique se a variável `SECRET_KEY` está definida.
- Se o frontend não conseguir contactar o backend, confirme a origem `http://localhost:5500` no servidor Flask.
- Para reiniciar a base de dados, use `python database/db_manager.py reset`.

---

## 11. Executar em dois terminais

Terminal A:

```bash
cd e:\3ANO\ES2\Lab3_part2\newshub
venv\Scripts\activate
python backend/app.py
```

Terminal B:

```bash
cd e:\3ANO\ES2\Lab3_part2\newshub\frontend
python -m http.server 5500
```

Abra no navegador:

- `http://localhost:5500/index.html`

---

## 12. Problemas comuns

- `ModuleNotFoundError`:
  - Ative o ambiente virtual
  - Instale dependências com `pip install -r requirements.txt`
- `NEWS_API_KEY` inválida:
  - Verifique a chave em `.env`
  - Use uma chave válida do NewsAPI.org
- Erro de CORS:
  - Confirme que o frontend usa `http://localhost:5500`
  - O backend já permite essa origem

---

## 13. Comandos úteis resumidos

```bash
# Preparar ambiente
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Inicializar DB
python database/db_manager.py init
python database/db_manager.py seed

# Executar backend
python backend/app.py

# Executar frontend
cd frontend
python -m http.server 5500

# Testes
python tests/test_routes.py
```

---

## 14. Nota final

Este guia cobre a configuração completa para executar e testar o projeto `newshub` localmente. Se precisar de ajuda adicional, pode usar os conteúdos do arquivo `README.md` do projeto como referência complementar.
