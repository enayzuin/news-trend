# Dockerfile para o projeto TrendNews
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Cria diretório para os arquivos de saída
RUN mkdir -p output

# Expõe a porta para o servidor Flask
EXPOSE 8000

# Define variáveis de ambiente (podem ser substituídas durante a execução)
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Comando para iniciar o servidor Flask
CMD ["python", "app.py"]
