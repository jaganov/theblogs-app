#!/usr/bin/env python3
"""
Script for complete cleanup and setup of TheBlogs project
Performs: database cleanup, media files cleanup, migrations, user and post generation
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def run_command(command, description, check=True):
    """Execute command with description output"""
    print(f"\n🔄 {description}")
    print(f"Executing: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print("✅ Successfully completed")
            if result.stdout.strip():
                print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        if check:
            sys.exit(1)
        return e

def wait_for_database():
    """Wait for database readiness"""
    print("\n⏳ Waiting for database to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                "docker exec theblogs_db pg_isready -U postgres",
                shell=True, check=True, capture_output=True
            )
            print("✅ Database is ready!")
            return True
        except subprocess.CalledProcessError:
            if attempt < max_attempts - 1:
                print(f"   Attempt {attempt + 1}/{max_attempts}...")
                time.sleep(2)
            else:
                print("❌ Database not ready after all attempts")
                return False

def main():
    print("🚀 Starting complete cleanup and setup of TheBlogs project")
    print("=" * 60)
    
    # 1. Stop containers and remove volumes
    run_command("docker-compose down -v", "Stopping containers and removing volumes")
    
    # 2. Remove media files
    media_path = Path("app/media")
    if media_path.exists():
        print(f"\n🗑️ Removing media files from {media_path}")
        import shutil
        shutil.rmtree(media_path)
        print("✅ Media files removed")
    else:
        print("\nℹ️ Media folder not found, skipping")
    
    # 3. Start containers
    run_command("docker-compose up -d", "Starting containers")
    
    # 4. Wait for database readiness
    if not wait_for_database():
        print("❌ Failed to wait for database readiness")
        sys.exit(1)
    
    # 5. Execute migrations
    run_command("docker exec theblogs_db psql -U postgres -d theblogs -c 'DROP SCHEMA IF EXISTS django CASCADE;'", "Cleaning django schema")
    run_command("docker exec theblogs_db psql -U postgres -d theblogs -c 'CREATE SCHEMA django;'", "Creating django schema")
    
    # 6. Django migrations
    run_command("cd app && python manage.py migrate", "Executing Django migrations")
    
    # 7. Create superuser (if needed)
    print("\n👤 Creating superuser")
    print("Enter superuser data (or press Enter to skip):")
    username = input("Username (admin): ").strip() or "admin"
    email = input("Email (admin@example.com): ").strip() or "admin@example.com"
    password = input("Password (admin123): ").strip() or "admin123"
    
    create_superuser_cmd = f"cd app && python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('{username}', '{email}', '{password}')\""
    run_command(create_superuser_cmd, "Creating superuser")
    
    # 8. Generate users
    print("\n👥 Generating test users")
    num_users = input("Number of users to generate (10): ").strip() or "10"
    run_command(f"cd app && python manage.py generate_users --count {num_users}", "Generating users")
    
    # 9. Generate posts
    print("\n📝 Generating test posts")
    num_posts = input("Number of posts to generate (20): ").strip() or "20"
    run_command(f"cd app && python manage.py generate_posts --count {num_posts}", "Generating posts")
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print(f"📊 Users created: {num_users}")
    print(f"📝 Posts created: {num_posts}")
    print(f"👤 Superuser: {username} / {password}")
    print("\n🌐 Application available at: http://localhost:8000")
    print("🔧 Admin panel: http://localhost:8000/admin/")

if __name__ == "__main__":
    main() 