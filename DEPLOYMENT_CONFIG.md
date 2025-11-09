# 🚀 Deployment Configuration - Port Setup

## Server Architecture

```
Internet → mail.fayvad.com (Nginx) → Django App (port 8005)
                                      ↓ (internal)
                             Modoboa Server (port 8000)
```

## Port Configuration

| Service | External Port | Internal Port | Purpose |
|---------|---------------|---------------|---------|
| **Modoboa** | 8000 | 8000 | Email server API + IMAP/SMTP |
| **Django App** | 8005 | 8000 | Web interface + business logic |
| **Nginx** | 80/443 | - | Reverse proxy for mail.fayvad.com |

## Environment Variables

### Production (.env)
```bash
MODOBOA_API_URL=http://localhost:8000/api/v1
```

### Docker Development (docker-compose.yml)
```bash
MODOBOA_API_URL=http://host.docker.internal:8000/api/v1
```

## Nginx Configuration Example

```nginx
server {
    listen 443 ssl;
    server_name mail.fayvad.com;
    
    # SSL certificates
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Modoboa API (internal only - not exposed externally)
server {
    listen 8000;
    server_name localhost;
    
    location /api/v1/ {
        # Modoboa API endpoints
        proxy_pass http://localhost:8000;
    }
}
```

## Deployment Steps

1. **Install Modoboa** on port 8000
2. **Deploy Django app** on port 8005
3. **Configure Nginx** to proxy mail.fayvad.com → port 8005
4. **Test internal communication** Django → Modoboa API

## Verification Commands

```bash
# Test Django app
curl -I https://mail.fayvad.com/

# Test Modoboa API (internal)
curl -I http://localhost:8000/api/v1/

# Test internal communication
curl http://localhost:8005/fayvad_api/email/folders/
```
