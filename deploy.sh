#!/bin/bash

# Script de deploy para VPS da Hostinger
echo "🚀 Iniciando deploy do LessonHub API..."

# Parar o servidor atual se estiver rodando
echo "📋 Parando servidor atual..."
pkill -f "uvicorn" || true
pkill -f "start_server.py" || true

# Atualizar dependências
echo "📦 Atualizando dependências..."
pip install -r requirements.txt

# Executar migrações do banco
echo "🗄️ Executando migrações..."
alembic upgrade head

# Configurar variáveis de ambiente (se necessário)
if [ ! -f .env ]; then
    echo "⚠️ Arquivo .env não encontrado. Certifique-se de configurar as variáveis de ambiente."
fi

# Iniciar servidor com configurações otimizadas
echo "🔄 Iniciando servidor com múltiplos workers..."
nohup python start_server.py > app.log 2>&1 &

# Aguardar um pouco para o servidor inicializar
sleep 5

# Verificar se o servidor está rodando
if pgrep -f "start_server.py" > /dev/null; then
    echo "✅ Servidor iniciado com sucesso!"
    echo "📊 Logs disponíveis em: app.log"
    echo "🔍 Para verificar status: curl http://localhost:8000/health"
else
    echo "❌ Erro ao iniciar servidor. Verifique os logs em app.log"
    exit 1
fi

echo "�� Deploy concluído!" 