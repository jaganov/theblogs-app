# Production Deployment Guide for theblogs_app

## Overview
This guide provides step-by-step instructions for deploying your Django blog platform (theblogs_app) to a production Ubuntu VPS using Docker Compose, Nginx, and GitHub Actions for CI/CD. The guide is tailored for the domain `theblogs.app` and the current project structure.

---

## Prerequisites
- Ubuntu 20.04+ VPS (2GB+ RAM recommended)
- Domain name: `theblogs.app` pointed to your server's IP
- Project repository on GitHub
- SSH access to your server

---

## 1. Initial Server Setup

**Run as root or with sudo:**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw fail2ban

# Configure firewall
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Create a deploy user
sudo adduser deploy
sudo usermod -aG sudo deploy
sudo usermod -aG docker deploy
```

---

## 2. Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

---

## 3. Clone the Project

**Switch to the deploy user:**

```bash
sudo su - deploy
git clone https://github.com/yourusername/theblogs_app.git
cd theblogs_app
```

---

## 4. Environment Variables

Create a `.env` file in the project root (next to `manage.py`):

```env
DEBUG=False
SECRET_KEY=your-super-secret-production-key
ALLOWED_HOSTS=theblogs.app,www.theblogs.app

POSTGRES_DB=theblogs_prod
POSTGRES_USER=theblogs_user
POSTGRES_PASSWORD=super-secure-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

MEDIA_URL=/media/
STATIC_URL=/static/
```

---

## 5. Production Docker Compose

Create a dedicated `docker-compose.prod.yml` in the project root:

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: theblogs_web
    restart: unless-stopped
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env
    depends_on:
      - db
    networks:
      - theblogs_network

  db:
    image: postgres:16
    container_name: theblogs_db
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    env_file:
      - .env
    networks:
      - theblogs_network

  nginx:
    image: nginx:alpine
    container_name: theblogs_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/sites-available:/etc/nginx/sites-available
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - web
    networks:
      - theblogs_network

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  theblogs_network:
    driver: bridge
```

---

## 6. Nginx Configuration

- Ensure the `nginx/` directory exists in your project root.
- Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout  65;
    types_hash_max_size 2048;
    client_max_body_size 50M;
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
    include /etc/nginx/sites-available/*;
}
```

- Create `nginx/sites-available/theblogs.conf`:

```nginx
server {
    listen 80;
    server_name theblogs.app www.theblogs.app;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name theblogs.app www.theblogs.app;

    ssl_certificate /etc/letsencrypt/live/theblogs.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/theblogs.app/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

---

## 7. SSL Certificate with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d theblogs.app -d www.theblogs.app
```

---

## 8. Launch the Application

```bash
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

## 9. CI/CD with GitHub Actions

### 9.1. GitHub Secrets
Add these secrets in your GitHub repository (Settings → Secrets and variables → Actions):
- `VPS_HOST`: your server IP
- `VPS_USER`: deploy
- `VPS_SSH_KEY`: your private SSH key

### 9.2. GitHub Actions Workflow
Create `.github/workflows/deploy.yml` in your repo:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        SECRET_KEY: test-secret-key
        DEBUG: True
      run: |
        python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to server
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.VPS_HOST }}
        username: ${{ secrets.VPS_USER }}
        key: ${{ secrets.VPS_SSH_KEY }}
        script: |
          cd /home/deploy/theblogs_app
          git pull origin main
          docker-compose -f docker-compose.prod.yml down
          docker-compose -f docker-compose.prod.yml up -d --build
          docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate
          docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput
          docker system prune -f
```

---

## 10. Useful Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Check service status
docker-compose -f docker-compose.prod.yml ps

# Execute Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Database backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U theblogs_user theblogs_prod > backup.sql

# Database restore
docker-compose -f docker-compose.prod.yml exec -T db psql -U theblogs_user theblogs_prod < backup.sql
```

---

## 11. Security Checklist

- [ ] SSH key authentication enabled
- [ ] Password authentication disabled
- [ ] Firewall configured
- [ ] SSL certificates installed
- [ ] Strong database passwords
- [ ] Regular backups scheduled
- [ ] Log monitoring in place
- [ ] Fail2ban configured
- [ ] Regular security updates

---

## 12. Performance Optimization

- [ ] Static files served by Nginx
- [ ] Database queries optimized
- [ ] Caching implemented (e.g., Redis)
- [ ] Image optimization
- [ ] CDN for static assets (optional)
- [ ] Database connection pooling
- [ ] Monitoring tools (optional)

---

This deployment guide is tailored for theblogs_app and provides a secure, production-ready setup with monitoring and automated deployment. Adjust secrets, passwords, and paths as needed for your environment.