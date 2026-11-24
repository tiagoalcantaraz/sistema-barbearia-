# Setup do Ambiente
1. Instale Python 3.10+.
2. Crie e ative o ambiente virtual (`python -m venv venv`).
3. `pip install -r requirements.txt`
4. `python app.py` — o banco `barbearia.db` é criado sozinho.
5. Abra http://127.0.0.1:5000.
Para produção: troque `secret_key`, desative `debug` e use gunicorn/waitress.
