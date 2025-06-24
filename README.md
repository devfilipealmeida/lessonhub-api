# LessonHub API

API para geração de cursos online usando IA.

## 🚀 Deploy com Docker

### Produção
```bash
# Deploy completo
chmod +x deploy-docker.sh
./deploy-docker.sh

# Ou manualmente:
docker-compose up -d --build
```

### Desenvolvimento
```bash
# Usar configuração de desenvolvimento
docker-compose -f docker-compose.dev.yml up -d --build
```

## 📋 Comandos Úteis

```bash
# Ver logs
docker-compose logs -f app

# Parar serviços
docker-compose down

# Reiniciar apenas a aplicação
docker-compose restart app

# Ver status dos containers
docker-compose ps

# Executar migrações
docker-compose run --rm app alembic upgrade head

# Acessar shell do container
docker-compose exec app bash
```

## 🔧 Configurações de Performance

### Banco de Dados
- Pool de conexões: 20 + 30 overflow
- Configurações otimizadas do PostgreSQL
- Health checks automáticos

### Aplicação
- Múltiplos workers baseados no número de CPUs
- Rate limiting: 100 requests/minuto por usuário
- Timeout de 5 minutos para geração de cursos
- Middleware de performance

### Nginx (Opcional)
- Balanceamento de carga
- Compressão Gzip
- Timeouts otimizados para operações longas

## 📊 Monitoramento

- Health check: `GET /health`
- Logs em volume Docker
- Headers de performance nas respostas

## 🛠️ Estrutura do Projeto

```
lessonhub-api/
├── app/
│   ├── main.py              # Configuração principal
│   ├── database.py          # Configuração do banco
│   ├── middleware.py        # Rate limiting
│   └── routes/              # Endpoints da API
├── docker-compose.yml       # Produção
├── docker-compose.dev.yml   # Desenvolvimento
├── Dockerfile              # Imagem da aplicação
├── nginx.conf              # Configuração do Nginx
├── start_server.py         # Script otimizado
└── deploy-docker.sh        # Script de deploy
```

## 🔍 Troubleshooting

### Problemas de Concorrência
- Verificar logs: `docker-compose logs app`
- Monitorar uso de memória: `docker stats`
- Verificar health checks: `curl http://localhost:8000/health`

### Banco de Dados
- Verificar conexões: `docker-compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT count(*) FROM pg_stat_activity;"`
- Logs do banco: `docker-compose logs db` 
