FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# アプリケーションの起動コマンド (必要に応じて)
CMD ["python", "app.py"]