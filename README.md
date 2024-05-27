# Rate Limiting Service

Implemented the token bucket algorithm. Worked with Redis as the primary database.
Features
- Lua Scripting: to avoid race condition
- Docker / Kubernetes / Azure cache for redis: to allow efficient scaling up and down of services 
