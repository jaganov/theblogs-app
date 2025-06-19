# The Blogs - Modern Blog Platform

## Quick Start

### Local Development (with Docker)
1. **Clone the repository:**
   ```bash
git clone <repository-url>
cd theblogs_app
```git
2. **Create a `.env` file** in the root directory (see [Production Setup](./PRODUCTION_SETUP.md) for required variables).
3. **Start the stack:**
   ```bash
docker compose up -d
```
4. **Apply migrations:**
   ```bash
docker compose exec web uv run python manage.py migrate
```
5. **Create a superuser:**
   ```bash
docker compose exec web uv run python manage.py createsuperuser
```
6. **(Optional) Generate test data:**
   ```bash
docker compose exec web uv run python manage.py generate_users
   docker compose exec web uv run python manage.py generate_posts
```

For full production setup, see [PRODUCTION_SETUP.md](./PRODUCTION_SETUP.md).

---

## Reset & Cleanup

To fully reset the project (database, media, etc.), see [RESET_INSTRUCTIONS.md](./RESET_INSTRUCTIONS.md). This guide covers:
- Automated and manual cleanup scripts for Windows/Linux/Mac
- How to remove Docker volumes and media files
- How to re-initialize the database and superuser
- Useful Docker and database commands

---

## Project Overview

**The Blogs** is a modern web application for creating and managing blogs. It features:
- User registration, authentication, and profile management
- Blog post creation, editing, and search (with PostgreSQL Full-Text Search)
- Calendar-based post filtering
- Extended Django admin panel
- Test data generation commands
- Dockerized deployment

### Architecture
- **Backend:** Django 5, Python 3, PostgreSQL 16
- **Frontend:** HTML5, CSS3, Vanilla JS, HTMX
- **DevOps:** Docker, Docker Compose, Nginx (production)
- **Apps:**
  - `account`: user management, authentication, profiles
  - `blog`: posts, search, calendar, authors

---

## Features
- List and search all blog posts (sorted by date)
- Author directory and filtering
- Calendar search for posts by date
- User registration and authentication (with HTMX forms)
- Profile editing and avatar upload
- Post creation, editing, and status (draft/published)
- Extended admin panel (user and post management)
- Automatic reading time calculation
- Test data generation (users, posts, images)

---

## Current Limitations
- **No adaptive (responsive) layout**: The UI is not mobile-friendly.
- **No asset compression/PageSpeed optimization**: Static files are not minified or optimized.
- **No dynamic loading/infinite scroll**: All content loads at once; no lazy loading or infinite scroll.
- **No social network integration**: No sharing, login, or preview for social platforms.
- **Potential for further dynamic mechanics**: More interactive features can be added.

---

## Screenshots Gallery
Below are screenshots demonstrating the main features and UI of the application:

![Admin Blog Detail](screenshots/admin_blog_detail.png)  
*Admin panel: blog detail view.*

![Admin Blogs](screenshots/admin_blogs.png)  
*Admin panel: list of blogs.*

![Admin Users](screenshots/admin_users.png)  
*Admin panel: list of users.*

![Admin Login](screenshots/admin_login.png)  
*Admin panel: login page.*

![Authors List](screenshots/authors_list.png)  
*Public: authors directory.*

![Contact](screenshots/contact.png)  
*Public: contact page.*

![Create Post](screenshots/create_post.png)  
*User: create new post.*

![Delete Post](screenshots/delete_post.png)  
*User: delete post confirmation.*

![Edit Post](screenshots/edit_post.png)  
*User: edit post form.*

![Edit Profile](screenshots/edit_profile.png)  
*User: edit profile form.*

![Index](screenshots/index.png)  
*Public: main blog feed.*

![Login](screenshots/login.png)  
*User: login form.*

![Post Detail](screenshots/post_detail.png)  
*Public: post detail view.*

![Privacy Policy](screenshots/privacy_policy.png)  
*Public: privacy policy.*

![Profile](screenshots/profile.png)  
*User: profile page.*

![Register](screenshots/register.png)  
*User: registration form.*

![Search](screenshots/search.png)  
*Public: search results.*

![Terms of Service](screenshots/terms_of_service.png)  
*Public: terms of service.*

---

## Main Endpoints

### Blog App
- `/` — Main blog feed
- `/create/` — Create a new post
- `/search/` — Search posts
- `/authors/` — List of authors
- `/@<username>/` — Author profile
- `/api/days-with-posts/` — Calendar API (days with posts)
- `/privacy-policy/` — Privacy policy
- `/terms-of-service/` — Terms of service
- `/contact/` — Contact page
- `/<post_slug>/` — Post detail

### Account App
- `/account/register/` — Register
- `/account/login/` — Login
- `/account/logout/` — Logout
- `/account/profile/` — User profile
- `/account/profile/edit/` — Edit profile
- `/account/profile/posts/<post_slug>/edit/` — Edit post
- `/account/profile/posts/<post_slug>/delete/` — Delete post

### Admin & Health
- `/admin/` — Django admin panel
- `/health/` — Health check endpoint

---

## Test Data Generation

The project includes management commands for generating test users and posts with avatars and images:
- `python manage.py generate_users [--avatar-chance 0.8]` — Create test users (see [README_text_generation.md](./app/blog/management/commands/README_text_generation.md) for details)
- `python manage.py generate_posts [--image-chance 1.0]` — Create test posts

See [README_text_generation.md](./app/blog/management/commands/README_text_generation.md) for full usage, parameters, and features.

---

## Assignment Requirements Checklist

This project fully implements all requirements from the assignment:

- **Display all blog posts sorted by date:**
  - Implemented on the main page (`/`), newest posts first.
- **Display the list of authors:**
  - Implemented at `/authors/`.
- **Show only the blog posts by a selected author:**
  - Implemented via author profile pages (`/@username/`).
- **Calendar date selection to filter posts:**
  - Implemented with a calendar and `/api/days-with-posts/`.
- **User registration and post creation:**
  - Implemented at `/account/register/` and `/create/`.
- **Search for blog posts by query:**
  - Implemented at `/search/` using PostgreSQL Full-Text Search.
- **Each post has an author, title, content, and date:**
  - Enforced by the data model.
- **Initial data: authors and posts:**
  - Provided by test data generation commands.
- **Pagination with "Next" and "Previous" links:**
  - Implemented in all post lists and search results.

---

## Documentation
- [Production Setup](./PRODUCTION_SETUP.md): Full production deployment guide
- [Reset Instructions](./RESET_INSTRUCTIONS.md): Full cleanup/reset guide
- [Test Data Generation](./app/blog/management/commands/README_text_generation.md): Details on test data commands

---

## License
MIT License (see LICENSE file if present)
