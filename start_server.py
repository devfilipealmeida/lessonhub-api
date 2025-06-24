import uvicorn
import multiprocessing
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Configurações otimizadas para produção
    workers = multiprocessing.cpu_count() * 2 + 1  # Número recomendado de workers
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=workers,
        loop="uvloop",  # Loop mais eficiente (Linux/Mac)
        http="httptools",  # HTTP parser mais rápido
        access_log=True,
        log_level="info",
        timeout_keep_alive=30,
        timeout_graceful_shutdown=30,
        limit_concurrency=1000,  # Limite de conexões simultâneas
        limit_max_requests=1000,  # Reinicia workers após N requests
        backlog=2048,  # Tamanho da fila de conexões
    ) 