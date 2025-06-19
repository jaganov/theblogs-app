from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from account.models import CustomUser
import requests
import os
import hashlib
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate 10 test users with different usernames, bios, and avatars'

    def add_arguments(self, parser):
        parser.add_argument(
            '--avatar-chance',
            type=float,
            default=0.8,
            help='Probability of generating avatar for each user (0.0 to 1.0, default: 0.8)'
        )

    def get_avatar_image(self, username, width=200, height=200):
        """Get random avatar image from Picsum Photos based on username"""
        try:
            # Create a hash from username to get consistent image for each user
            username_hash = hashlib.md5(username.lower().encode()).hexdigest()
            # Convert first 8 characters of hash to integer for image ID
            image_id = int(username_hash[:8], 16) % 1000 + 1  # IDs from 1 to 1000
            
            url = f"https://picsum.photos/id/{image_id}/{width}/{height}"
            
            self.stdout.write(f'    Requesting avatar from: {url}')
            
            # Test if the image exists
            response = requests.head(url, timeout=10)
            
            if response.status_code == 200:
                self.stdout.write(f'    Avatar URL resolved: {url}')
                return url
            else:
                # If specific ID doesn't exist, use random image
                random_url = f"https://picsum.photos/{width}/{height}"
                self.stdout.write(f'    Using random avatar: {random_url}')
                return random_url
                
        except requests.exceptions.Timeout:
            self.stdout.write(
                self.style.WARNING(f'Timeout getting avatar image for {username}')
            )
            return None
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.WARNING(f'Request failed for avatar image {username}: {e}')
            )
            return None
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Unexpected error getting avatar image for {username}: {e}')
            )
            return None

    def download_and_save_avatar(self, image_url, username, user_id):
        """Download avatar image and save to media directory"""
        try:
            if not image_url:
                self.stdout.write(
                    self.style.WARNING(f'No avatar URL provided for {username}')
                )
                return None
            
            # Create media directory if it doesn't exist
            from django.conf import settings
            media_dir = os.path.join(settings.MEDIA_ROOT, f'user_{user_id}', 'avatar')
            
            # Ensure the directory exists
            try:
                os.makedirs(media_dir, exist_ok=True)
                self.stdout.write(f'    Directory created/verified: {media_dir}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create directory {media_dir}: {e}')
                )
                return None
            
            # Download image with better error handling
            try:
                response = requests.get(image_url, timeout=15, stream=True)
                response.raise_for_status()  # Raise exception for bad status codes
                
                # Check content type to ensure it's an image
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    self.stdout.write(
                        self.style.WARNING(f'URL does not point to an image: {content_type}')
                    )
                    return None
                
            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to download avatar from {image_url}: {e}')
                )
                return None
            
            # Generate filename
            filename = f"avatar_{username}.jpg"
            filepath = os.path.join(media_dir, filename)
            
            # Save image
            try:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Verify file was created and has content
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    self.stdout.write(f'    Avatar saved: {filename} ({os.path.getsize(filepath)} bytes)')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Avatar file was not created or is empty: {filepath}')
                    )
                    return None
                
            except IOError as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to save avatar to {filepath}: {e}')
                )
                return None
            
            # Return relative path for Django model
            return f"user_{user_id}/avatar/{filename}"
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error downloading avatar for {username}: {e}')
            )
            return None

    def handle(self, *args, **options):
        avatar_chance = options['avatar_chance']
        
        # Validate avatar_chance parameter
        if not 0.0 <= avatar_chance <= 1.0:
            self.stdout.write(
                self.style.ERROR('Avatar chance must be between 0.0 and 1.0')
            )
            return

        users_data = [
            {
                'username': 'alex_writer',
                'bio': 'Passionate tech writer and software developer. Love exploring new technologies and sharing knowledge through writing.'
            },
            {
                'username': 'maria_blogger',
                'bio': 'Lifestyle blogger with a focus on productivity and personal development. Always learning and growing.'
            },
            {
                'username': 'john_developer',
                'bio': 'Full-stack developer with 5+ years of experience. Specialized in Python, Django, and React. Open source contributor.'
            },
            {
                'username': 'sarah_designer',
                'bio': 'UI/UX designer passionate about creating beautiful and functional user experiences. Coffee addict and design enthusiast.'
            },
            {
                'username': 'mike_entrepreneur',
                'bio': 'Startup founder and business consultant. Helping others build successful companies and achieve their goals.'
            },
            {
                'username': 'lisa_teacher',
                'bio': 'High school teacher and educational content creator. Dedicated to making learning fun and accessible for everyone.'
            },
            {
                'username': 'david_photographer',
                'bio': 'Professional photographer capturing life\'s beautiful moments. Travel enthusiast and nature lover.'
            },
            {
                'username': 'anna_chef',
                'bio': 'Home chef and food blogger. Sharing delicious recipes and cooking tips for everyday meals.'
            },
            {
                'username': 'tom_fitness',
                'bio': 'Personal trainer and fitness coach. Helping people achieve their health and fitness goals through sustainable practices.'
            },
            {
                'username': 'emma_artist',
                'bio': 'Digital artist and illustrator. Creating colorful and imaginative artwork that brings joy to people\'s lives.'
            }
        ]

        created_count = 0
        for user_data in users_data:
            username = user_data['username']
            bio = user_data['bio']
            
            # Check if user already exists
            if CustomUser.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User {username} already exists, skipping...')
                )
                continue
            
            # Create user first to get the ID
            user = CustomUser.objects.create_user(
                username=username,
                password='test',
                bio=bio
            )
            
            # Generate and download avatar based on avatar_chance parameter
            if random.random() < avatar_chance:
                self.stdout.write(f'  Generating avatar for user: {username}...')
                avatar_path = self.download_and_save_avatar(
                    self.get_avatar_image(username), 
                    username, 
                    user.id
                )
                
                if avatar_path:
                    user.avatar = avatar_path
                    user.save()
                    self.stdout.write(f'    ✓ Avatar added: {avatar_path}')
                else:
                    self.stdout.write(f'    ⚠ No avatar generated')
            else:
                self.stdout.write(f'  Skipping avatar generation for user: {username} (chance: {avatar_chance})')
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created user: {username}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal users created: {created_count}')
        )
        self.stdout.write(
            self.style.SUCCESS('All users have password: test')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Avatar generation chance: {avatar_chance * 100:.0f}%')
        ) 