@echo off
chcp 65001 >nul
echo 🚀 Starting complete cleanup and setup of TheBlogs project
echo ============================================================

echo.
echo 🔄 Stopping containers and removing volumes...
docker-compose down -v

echo.
echo 🗑️ Removing media files...
if exist "app\media" (
    rmdir /s /q "app\media"
    echo ✅ Media files removed
) else (
    echo ℹ️ Media folder not found, skipping
)

echo.
echo 🔄 Starting containers...
docker-compose up -d

echo.
echo ⏳ Waiting for database to be ready...
:wait_loop
docker exec theblogs_db pg_isready -U postgres >nul 2>&1
if errorlevel 1 (
    echo    Attempting to connect to database...
    timeout /t 2 /nobreak >nul
    goto wait_loop
)
echo ✅ Database is ready!

echo.
echo 🔄 Cleaning django schema...
docker exec theblogs_db psql -U postgres -d theblogs -c "DROP SCHEMA IF EXISTS django CASCADE;"

echo.
echo 🔄 Creating django schema...
docker exec theblogs_db psql -U postgres -d theblogs -c "CREATE SCHEMA django;"

echo.
echo 🔄 Executing Django migrations...
cd app
python manage.py migrate
cd ..

echo.
echo 👤 Creating superuser...
set /p username="Username (admin): "
if "%username%"=="" set username=admin

set /p email="Email (admin@example.com): "
if "%email%"=="" set email=admin@example.com

set /p password="Password (admin123): "
if "%password%"=="" set password=admin123

cd app
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('%username%', '%email%', '%password%')"
cd ..

echo.
echo 👥 Generating test users...
set /p num_users="Number of users to generate (10): "
if "%num_users%"=="" set num_users=10

cd app
python manage.py generate_users --count %num_users%
cd ..

echo.
echo 📝 Generating test posts...
set /p num_posts="Number of posts to generate (20): "
if "%num_posts%"=="" set num_posts=20

cd app
python manage.py generate_posts --count %num_posts%
cd ..

echo.
echo ============================================================
echo 🎉 Setup completed successfully!
echo 📊 Users created: %num_users%
echo 📝 Posts created: %num_posts%
echo 👤 Superuser: %username% / %password%
echo.
echo 🌐 Application available at: http://localhost:8000
echo 🔧 Admin panel: http://localhost:8000/admin/
echo.
pause 