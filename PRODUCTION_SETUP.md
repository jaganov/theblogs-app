# Production Setup Instructions

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Database Configuration
POSTGRES_DB=theblogs
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here

# Django Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,web
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

# Database Schema
DB_SCHEME=app

# Optional: Database URL (alternative to individual variables)
# DATABASE_URL=postgresql://postgres:your_secure_password_here@postgres:5432/theblogs
```

## Quick Start

1. **Create .env file** with the variables above

2. **Setup permissions** (optional, for Linux systems):
   ```bash
   chmod +x setup_permissions.sh
   ./setup_permissions.sh
   ```

3. **Run the entire stack**:
   ```bash
   docker compose up -d
   ```

4. **Apply migrations**:
   ```bash
   docker compose exec web uv run python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   docker compose exec web uv run python manage.py createsuperuser
   ```

6. **Generate test data** (optional):
   ```bash
   docker compose exec web uv run python manage.py generate_users
   docker compose exec web uv run python manage.py generate_posts
   ```

## Access the Application

- **Main application**: http://localhost
- **Admin panel**: http://localhost/admin
- **Health check**: http://localhost/health

## Architecture

- **Nginx**: Reverse proxy on port 80, serves static files
- **Django**: ASGI application with uvicorn, 4 workers
- **PostgreSQL**: Database with custom schema

## Production Features

- ✅ Static file serving via Nginx
- ✅ Media file serving via Nginx
- ✅ Gzip compression
- ✅ Rate limiting (login: 5r/m, API: 10r/s)
- ✅ Security headers
- ✅ Health checks
- ✅ Logging configuration
- ✅ Environment-based configuration
- ✅ Database URL support
- ✅ Non-root user in containers (UID 1000)
- ✅ Proper file permissions for uploads

## File Permissions

The application uses a non-root user (UID 1000) for security. All media uploads and static files are handled with proper permissions:

- **Media files**: `/app/app/media/` (writable by app user)
- **Static files**: `/app/app/staticfiles/` (writable by app user)
- **Logs**: `/app/app/logs/` (writable by app user)

## Monitoring

Check container health:
```bash
docker compose ps
```

View logs:
```bash
docker compose logs -f
```

## Scaling

To scale the web service:
```bash
docker compose up -d --scale web=3
```

## Backup

Backup database:
```bash
docker compose exec postgres pg_dump -U postgres theblogs > backup.sql
```

Restore database:
```bash
docker compose exec -T postgres psql -U postgres theblogs < backup.sql
```

## Troubleshooting

### Permission Issues
If you encounter permission issues with file uploads:

1. **Check container logs**:
   ```bash
   docker compose logs web
   ```

2. **Verify user permissions**:
   ```bash
   docker compose exec web ls -la /app/app/media
   ```

3. **Reset permissions** (if needed):
   ```bash
   docker compose down
   docker compose up -d
   ```

### Database Connection Issues
If database connection fails:

1. **Check database status**:
   ```bash
   docker compose exec postgres pg_isready -U postgres
   ```

2. **Test connection manually**:
   ```bash
   docker compose exec web uv run python check_db.py
   ``` 