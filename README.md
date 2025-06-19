# The Blogs - Web Application for Blogs

## Project Description

**The Blogs** is a modern web application for creating and managing blogs, developed as part of an educational project. The platform allows users to create, edit, and share their articles in a shared blog space.

## Functional Requirements

According to the technical specification, the application implements the following capabilities:

1. **Display all blog posts** sorted by date (the latest post is displayed first)
2. **List of authors** with the ability to view all platform authors
3. **Filter by author** - view posts by a specific author
4. **Calendar search** - display posts for a selected date
5. **User registration and authentication** with unique usernames
6. **Create own blog posts** by authenticated users
7. **Search through posts** using PostgreSQL Full-Text Search (FTS)

## Technology Stack

### Backend
- **Django 5.2.3** - main web framework
- **Python 3.x** - programming language
- **PostgreSQL 16.2** - main database
- **psycopg2** - driver for working with PostgreSQL

### Frontend
- **HTML5/CSS3** - markup and styling
- **JavaScript (Vanilla)** - interactivity
- **HTMX** - modern approach to AJAX without writing JavaScript
- **Font Awesome** - icons
- **Google Fonts** - typography

### DevOps & Deployment
- **Docker** - containerization
- **Docker Compose** - container orchestration
- **PostgreSQL** - database in container

### Additional Technologies
- **Markdown** - markup support in posts
- **Django Admin** - administrative panel
- **Django Management Commands** - commands for generating test data

## Project Architecture

### Application Separation (Apps)

The project is divided into two main applications, which is a popular practice in Django:

#### 1. **account** - User Management
- **CustomUser Model** - extended user model with `bio` and `avatar` fields
- **Authentication System** - registration, login, logout
- **User Profiles** - profile editing, post management
- **HTMX Integration** - modern approach to authentication forms

#### 2. **blog** - Main Blog Functionality
- **Post Model** - posts with extended fields
- **Search System** - PostgreSQL FTS instead of LIKE queries
- **Calendar Functionality** - API for getting days with posts
- **Pagination** - limiting posts per page

### Database

#### PostgreSQL Full-Text Search (FTS)
Instead of traditional LIKE queries, a powerful PostgreSQL full-text search system is used:

```python
# Example of FTS usage in models.py
@classmethod
def search(cls, query):
    search_vector = SearchVector('title', weight='A') + \
                   SearchVector('excerpt', weight='B')
    search_query = SearchQuery(query)
    
    return cls.objects.annotate(
        rank=SearchRank(search_vector, search_query)
    ).filter(rank__gt=0).order_by('-rank')
```

#### Database Schema
- **CustomUser** - extended user model
- **Post** - post model with automatic reading time calculation
- **Indexes** for performance optimization

## Key Features

### 1. HTMX in Authentication
Using HTMX to create a modern user experience without writing JavaScript:

```html
<!-- Example from login.html -->
<form method="post" 
      class="auth-form"
      hx-post="{% url 'account:login' %}"
      hx-target="#login-message"
      hx-swap="innerHTML"
      hx-indicator="#login-indicator">
```

### 2. Data Generation Commands
Special Django management commands created for populating the database with test data:

- **`generate_users`** - creates 10 test users with unique profiles
- **`generate_posts`** - generates 40 posts for each user with thematic content

### 3. Extended Admin Panel
Detailed administrative panel configured with:

#### For Users (CustomUserAdmin):
- Filters by status, groups, activity
- Search by name, email, username
- Extended fields: bio, avatar

#### For Posts (PostAdmin):
- Image display in list
- Filters by status, date, author
- View statistics and reading time
- Field grouping in sections

### 4. Automatic Reading Time Calculation
```python
def save(self, *args, **kwargs):
    # Reading time calculation (200 words per minute)
    word_count = len(re.findall(r'\w+', self.content))
    self.reading_time = max(1, round(word_count / 200))
    super().save(*args, **kwargs)
```

### 5. Post Status System
- **Draft** - drafts (visible only to author)
- **Published** - published posts (visible to everyone)

## Project Structure

```
theblogs_app/
├── app/                    # Main Django application
│   ├── account/           # User application
│   │   ├── models.py      # CustomUser model
│   │   ├── views.py       # Authentication and profiles
│   │   ├── admin.py       # User admin panel
│   │   └── management/    # Generation commands
│   ├── blog/              # Blog application
│   │   ├── models.py      # Post model with FTS
│   │   ├── views.py       # Main views
│   │   ├── admin.py       # Post admin panel
│   │   └── management/    # Generation commands
│   ├── templates/         # HTML templates
│   ├── static/           # CSS, JS, images
│   └── app/              # Django settings
├── docker-compose.yml    # Docker configuration
├── requirements.txt      # Python dependencies
└── README.md            # Documentation
```

## Installation and Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.8+

### Quick Start

1. **Clone Repository**
```bash
git clone <repository-url>
cd theblogs_app
```

2. **Start with Docker**
```bash
docker-compose up -d
```

3. **Apply Migrations**
```bash
docker-compose exec web python manage.py migrate
```

4. **Create Superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Generate Test Data**
```bash
docker-compose exec web python manage.py generate_users
docker-compose exec web python manage.py generate_posts
```

### Local Development

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Database Setup**
```bash
# Create .env file with PostgreSQL settings
```

3. **Run Development Server**
```bash
python manage.py runserver
```

## API Endpoints

### Main URLs
- `/blog/` - main page with posts
- `/blog/authors/` - list of all authors
- `/blog/search/` - search through posts
- `/blog/create/` - create new post
- `/account/login/` - login page
- `/account/register/` - registration
- `/account/profile/` - user profile
- `/admin/` - administrative panel

### Calendar API
- `GET /blog/api/days-with-posts/?year=2024&month=3` - get days with posts

## Implementation Features

### 1. Security
- CSRF protection for all forms
- Password validation
- Draft access rights verification

### 2. Performance
- Database indexes for fast search
- Optimized queries with select_related
- Pagination for large lists

### 3. UX/UI
- Responsive design
- Modern interface
- Interactive elements with HTMX
- Calendar post search

### 4. Scalability
- Modular architecture
- Application separation
- Ability to transfer account application between projects

## Technical Details

### PostgreSQL Configuration
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': '-c search_path=%s' % os.environ.get("DB_SCHEME", "django")
        },
        # ... other settings
    },
}
```

### HTMX Settings
```html
<!-- Automatic CSRF token addition -->
<script>
document.body.addEventListener('htmx:configRequest', function(evt) {
    evt.detail.headers['X-CSRFToken'] = '{{ csrf_token }}';
});
</script>
```

## Conclusion

The **The Blogs** project demonstrates a modern approach to web application development using Django and PostgreSQL. Key features:

- **Application separation** for better code organization
- **PostgreSQL FTS** for efficient search
- **HTMX** for modern user interface
- **Docker** for easy deployment
- **Extended admin panel** for content management
- **Automatic test data generation**

The project is production-ready and can be easily extended with additional functionality.
