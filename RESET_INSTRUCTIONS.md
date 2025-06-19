# Instructions for Complete Cleanup and Setup of TheBlogs Project

## Where Data is Stored

### PostgreSQL Database
- **Container**: `theblogs_db`
- **Volume**: `postgres_data` (Docker volume)
- **Physical location**: `/var/lib/postgresql/data` inside container
- **Schema**: `app` (configured in settings.py)

### Media Files
- **Path**: `app/media/`
- **Contents**:
  - User avatars: `user_<id>/avatar/`
  - Post images: `blog_images/`

## Quick Cleanup (Automatic Script)

### For Windows:
```bash
# Run batch file
reset_and_setup.bat
```

### For Linux/Mac:
```bash
# Run Python script
python reset_and_setup.py
```

## Manual Cleanup (Step by Step)

### 1. Stop and Clean Containers
```bash
# Stop containers and remove volumes
docker-compose down -v
```

### 2. Remove Media Files
```bash
# Windows
rmdir /s /q app\media

# Linux/Mac
rm -rf app/media
```

### 3. Start Containers
```bash
docker-compose up -d
```

### 4. Wait for Database Readiness
```bash
# Check readiness
docker exec theblogs_db pg_isready -U postgres
```

### 5. Clean and Create Schema
```bash
# Remove django schema
docker exec theblogs_db psql -U postgres -d theblogs -c "DROP SCHEMA IF EXISTS django CASCADE;"

# Create new schema
docker exec theblogs_db psql -U postgres -d theblogs -c "CREATE SCHEMA django;"
```

### 6. Django Migrations
```bash
cd app
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
```

### 8. Generate Test Data
```bash
# Generate users
python manage.py generate_users --count 10

# Generate posts
python manage.py generate_posts --count 20
```

## Useful Commands

### View Docker Volumes
```bash
docker volume ls
```

### Remove Specific Volume
```bash
docker volume rm theblogs_app_postgres_data
```

### View Container Logs
```bash
docker logs theblogs_db
```

### Connect to Database
```bash
docker exec -it theblogs_db psql -U postgres -d theblogs
```

### View Schemas in Database
```sql
\dn
```

### View Tables in django Schema
```sql
\dt django.*
```

## Project Structure After Cleanup

```
theblogs_app/
├── app/
│   ├── media/                    # Will be created automatically
│   │   ├── user_1/avatar/        # User avatars
│   │   └── blog_images/          # Post images
│   ├── migrations/               # Django migrations
│   └── manage.py
├── docker-compose.yml
├── reset_and_setup.py           # Python cleanup script
├── reset_and_setup.bat          # Batch file for Windows
└── RESET_INSTRUCTIONS.md        # This file
```

## Notes

1. **Volume `postgres_data`** - This is a Docker volume that persists data between container restarts
2. **Media files** are stored locally in the `app/media/` folder
3. **Schema `django`** is created automatically when migrations are executed
4. After cleanup, all data will be permanently deleted
5. It's recommended to backup before cleanup if there's important data

## Application Access

After successful setup:
- **Main application**: http://localhost:8000
- **Admin panel**: http://localhost:8000/admin/
- **Superuser**: admin / admin123 