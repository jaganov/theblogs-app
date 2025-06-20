# The Blogs - Modern Blog Platform

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

## Live Demo

🌐 **Live Application:** [https://theblogs.app/](https://theblogs.app/)

The project is successfully deployed and running in production with:
- SSL certificate (HTTPS)
- Nginx reverse proxy
- PostgreSQL database
- Automated deployment via GitHub Actions
- Regular backups and monitoring

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

## Quick Start

> **Note:** Creating a `.env` file is optional for local development. The project uses default parameters. See [Production Setup](./PRODUCTION_SETUP.md) to override defaults for production.

### Local Development (with Docker)
1. **Clone the repository:**

```bash
git clone <repository-url>
cd theblogs_app
```

2. **(Optional) Create a `.env` file** in the root directory (see [Production Setup](./PRODUCTION_SETUP.md) for required variables).

3. **Start the stack:**

```bash
docker compose up -d
```

4. **Apply migrations:**

```bash
docker compose exec web uv run python manage.py migrate
```

```bash
docker compose exec web uv run python manage.py collectstatic
```
5. **Create a superuser:**

```bash
docker compose exec web uv run python manage.py createsuperuser
```

6. **Generate test data:**

```bash
docker compose exec web uv run python manage.py generate_users --avatar-chance 1.0   # 100% users with avatars
docker compose exec web uv run python manage.py generate_posts --image-chance 0.5    # 50% posts with images
```

See [README_text_generation.md](./app/blog/management/commands/README_text_generation.md) for details on test data generation mechanics and parameters.

For full production setup, see [PRODUCTION_SETUP.md](./PRODUCTION_SETUP.md).

---

## Deployment

### Production Deployment

The project is designed for easy deployment to production environments. The current live deployment at [https://theblogs.app/](https://theblogs.app/) demonstrates the production setup.

#### Deployment Options:

1. **Simple Production Setup** - [PRODUCTION_SETUP.md](./PRODUCTION_SETUP.md)
   - Basic production configuration with Docker Compose
   - Nginx reverse proxy
   - SSL certificate setup
   - Environment variable configuration

2. **Full Production Deployment** - [DEPLOY_SETUP.md](./DEPLOY_SETUP.md)
   - Complete VPS deployment guide
   - Ubuntu server setup
   - Automated deployment via GitHub Actions
   - Backup and monitoring systems
   - Security hardening

#### Key Production Features:
- ✅ SSL/HTTPS encryption
- ✅ Nginx reverse proxy with caching
- ✅ PostgreSQL database with connection pooling
- ✅ Static and media file serving
- ✅ Rate limiting and security headers
- ✅ Health checks and monitoring
- ✅ Automated backups
- ✅ Docker containerization
- ✅ Environment-based configuration

#### Deployment Steps (General):
1. **Server Setup**: Configure Ubuntu VPS with Docker and Nginx
2. **Domain Configuration**: Point domain to server IP
3. **SSL Certificate**: Obtain Let's Encrypt certificate
4. **Application Deployment**: Deploy using Docker Compose
5. **Database Setup**: Run migrations and create superuser
6. **Monitoring**: Configure logs and health checks

For detailed deployment instructions, see [DEPLOY_SETUP.md](./DEPLOY_SETUP.md).

---

## Test Data Generation

The project includes management commands for generating test users and posts with avatars and images. Example usage:

```bash
python manage.py generate_users --avatar-chance 0.8   # 80% users with avatars
python manage.py generate_posts --image-chance 1.0    # 100% posts with images
```

See [README_text_generation.md](./app/blog/management/commands/README_text_generation.md) for full usage, parameters, and features.

---

## Reset & Cleanup

To fully reset the project (database, media, etc.), see [RESET_INSTRUCTIONS.md](./RESET_INSTRUCTIONS.md). This guide covers:

- Automated and manual cleanup scripts for Windows/Linux/Mac
- How to remove Docker volumes and media files
- How to re-initialize the database and superuser
- Useful Docker and database commands

---

## Main Endpoints

### Blog App

- `/` — Main blog feed
- `/search/` — Search posts
- `/authors/` — List of authors
- `/@<username>/` — Author profile
- `/create/` — Create a new post
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

## Documentation

- [Production Setup](./PRODUCTION_SETUP.md): Basic production deployment guide
- [Deploy Setup](./DEPLOY_SETUP.md): Complete VPS deployment guide with automation
- [Reset Instructions](./RESET_INSTRUCTIONS.md): Full cleanup/reset guide
- [Test Data Generation](./app/blog/management/commands/README_text_generation.md): Details on test data commands

---

## Screenshots Gallery

Below are screenshots demonstrating the main features and UI of the application (in logical user flow order):

![Index](screenshots/index.png)
*Main blog feed.*

![Search](screenshots/search.png)
*Search results.*

![Authors List](screenshots/authors_list.png)
*Authors directory.*

![Post Detail](screenshots/post_detail.png)
*Post detail view.*

![Register](screenshots/register.png)
*User registration form.*

![Login](screenshots/login.png)
*User login form.*

![Profile](screenshots/profile.png)
*User profile page.*

![Edit Profile](screenshots/edit_profile.png)
*Edit profile form.*

![Create Post](screenshots/create_post.png)
*Create new post.*

![Edit Post](screenshots/edit_post.png)
*Edit post form.*

![Delete Post](screenshots/delete_post.png)
*Delete post confirmation.*

![Contact](screenshots/contact.png)
*Contact page.*

![Privacy Policy](screenshots/privacy_policy.png)
*Privacy policy.*

![Terms of Service](screenshots/terms_of_service.png)
*Terms of service.*

![Admin Blogs](screenshots/admin_blogs.png)
*Admin panel: main blogs list.*

![Admin Users](screenshots/admin_users.png)
*Admin panel: users list.*

![Admin Blog Detail](screenshots/admin_blog_detail.png)
*Admin panel: blog detail view.*

---

## License

MIT License (see LICENSE file if present)
