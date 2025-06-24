FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Criar diretório para logs
RUN mkdir -p /app/logs

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando padrão (pode ser sobrescrito pelo docker-compose)
CMD ["python", "start_server.py"]