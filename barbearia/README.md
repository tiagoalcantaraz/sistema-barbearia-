# Studio Barbearia — App de Agendamento

App simples em **Flask + SQLite** para agendar clientes de uma barbearia.

## Como rodar
```
python -m venv venv
venv\Scripts\activate        # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
Acesse http://127.0.0.1:5000 (cliente) e http://127.0.0.1:5000/admin (painel).

## Estrutura
- Telas: início, agendar, cadastro (clientes) e painel, com menu lateral e logo no topo
- `app.py` — rotas, regras e banco de dados
- `templates/` — páginas HTML (Jinja2)
- `static/style.css` — visual (azul marinho + botões amarelo #ffb700; logo em `static/logo.png`, fundo em `static/fundo.png`)
- `docs/` — documentação
- `barbearia.db` — criado automaticamente

## Design
Azul marinho `#0b1f3a` (predominante), amarelo `#ffb700` (botões), fundo `#eef2f7`, dourado da logo `#f5b50a`.
