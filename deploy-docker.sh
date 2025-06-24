#!/bin/bash

# Script de deploy para Docker Compose
echo "🐳 Iniciando deploy do LessonHub API com Docker..."

# Parar containers existentes
echo "📋 Parando containers existentes..."
docker-compose down

# Remover imagens antigas (opcional, para forçar rebuild)
echo "🧹 Limpando imagens antigas..."
docker system prune -f

# Fazer build das imagens
echo "🔨 Fazendo build das imagens..."
docker-compose build --no-cache

# Executar migrações
echo "🗄️ Executando migrações do banco..."
docker-compose run --rm app alembic upgrade head

# Iniciar serviços
echo "🚀 Iniciando serviços..."
docker-compose up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status dos containers
echo "📊 Verificando status dos containers..."
docker-compose ps

# Verificar logs da aplicação
echo "📋 Logs da aplicação:"
docker-compose logs app --tail=20

# Testar health check
echo "🔍 Testando health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Health check passou!"
else
    echo "❌ Health check falhou. Verifique os logs:"
    docker-compose logs app
fi

echo "🎉 Deploy concluído!"
echo ""
echo "📋 Comandos úteis:"
echo "  - Ver logs: docker-compose logs -f app"
echo "  - Parar: docker-compose down"
echo "  - Reiniciar: docker-compose restart app"
echo "  - Status: docker-compose ps" 