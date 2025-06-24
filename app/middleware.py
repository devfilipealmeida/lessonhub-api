from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import asyncio
from collections import defaultdict
import threading

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        
        with self.lock:
            # Limpar requisições antigas
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if now - req_time < self.window_seconds
            ]
            
            # Verificar se ainda há espaço
            if len(self.requests[client_id]) >= self.max_requests:
                return False
            
            # Adicionar nova requisição
            self.requests[client_id].append(now)
            return True

# Instância global do rate limiter
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

async def rate_limit_middleware(request: Request, call_next):
    # Identificar cliente (IP ou user_id se autenticado)
    client_id = request.client.host
    
    # Para endpoints de autenticação, usar IP
    if request.url.path.startswith("/login") or request.url.path.startswith("/register"):
        client_id = f"auth_{request.client.host}"
    
    # Para endpoints protegidos, usar user_id se disponível
    if hasattr(request.state, "user"):
        client_id = f"user_{request.state.user.id}"
    
    # Verificar rate limit
    if not rate_limiter.is_allowed(client_id):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )
    
    # Adicionar headers de rate limit
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(
        rate_limiter.max_requests - len(rate_limiter.requests[client_id])
    )
    
    return response 