# Test Data Generation Commands

This document describes Django commands for generating test users and posts with automatic image loading.

## User Generation

### Command: `generate_users`

Generates 10 test users with unique names, biographies, and avatars.

#### Usage:
```bash
python manage.py generate_users
```

#### Parameters:
- `--avatar-chance` (float, default: 0.8): Probability of generating an avatar for each user (0.0 to 1.0)

#### Examples:
```bash
# Generate users with avatars (80% probability by default)
python manage.py generate_users

# Generate users with avatars (100% probability)
python manage.py generate_users --avatar-chance 1.0

# Generate users without avatars
python manage.py generate_users --avatar-chance 0.0

# Generate users with avatars (50% probability)
python manage.py generate_users --avatar-chance 0.5
```

#### Created Users:
- `alex_writer` - Technical writer
- `maria_blogger` - Lifestyle blogger
- `john_developer` - Full-stack developer
- `sarah_designer` - UI/UX designer
- `mike_entrepreneur` - Entrepreneur
- `lisa_teacher` - Teacher
- `david_photographer` - Photographer
- `anna_chef` - Chef
- `tom_fitness` - Fitness trainer
- `emma_artist` - Artist

## Post Generation

### Command: `generate_posts`

Generates 20 posts for each user with thematic content, Markdown formatting, and images.

#### Usage:
```bash
python manage.py generate_posts
```

#### Parameters:
- `--image-chance` (float, default: 1.0): Probability of generating an image for each post (0.0 to 1.0)

#### Examples:
```bash
# Generate posts with images (100% probability by default)
python manage.py generate_posts

# Generate posts with images (80% probability)
python manage.py generate_posts --image-chance 0.8

# Generate posts without images
python manage.py generate_posts --image-chance 0.0

# Generate posts with images (50% probability)
python manage.py generate_posts --image-chance 0.5
```

## Features

### User Avatars
- Downloaded from Picsum Photos service
- Size: 200x200 pixels
- Saved in `MEDIA_ROOT/user_<id>/avatar/`
- Each user is assigned a unique image based on username hash

### Post Images
- Downloaded from Picsum Photos service
- Size: 800x600 pixels
- Saved in `MEDIA_ROOT/blog_images/`
- Each post is assigned an image based on topic hash
- Image captions are automatically generated

### Post Content
- Uses Markdown formatting
- Generated using Faker with multiple locales
- Includes headers, paragraphs, lists, and code
- Creates thematic content for each user type

## Requirements

- Installed `requests` package for image downloading
- Installed `faker` package for content generation
- Configured `MEDIA_ROOT` folder in Django settings
- Internet access for image downloading

## Notes

- All users are created with password `test`
- All posts are created with status `published`
- Post dates are randomly distributed over the last 6 months
- If image download errors occur, commands continue working and display warnings 