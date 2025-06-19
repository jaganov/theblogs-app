from django.db import models
from django.conf import settings
from django.utils.text import slugify
import math
import uuid
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models.functions import ExtractDay
from django.db.models import Q
from django.utils import timezone

import markdown
import re



class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True, max_length=500)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    featured_image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    image_caption = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
        ],
        default='draft'
    )
    views = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate base slug from title
            base_slug = slugify(self.title)
            # Add a unique suffix using first 8 characters of UUID
            unique_suffix = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_suffix}"
        
        # Calculate reading time (assuming average reading speed of 200 words per minute)
        word_count = len(re.findall(r'\w+', self.content))
        self.reading_time = max(1, round(word_count / 200))
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/blog/{self.slug}/'

    @property
    def is_draft(self):
        return self.status == 'draft'

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    @classmethod
    def get_days_with_posts(cls, year, month):
        """
        Returns a set of days in the given month that have published posts.
        """
        # Get all days in the month that have published posts
        days_with_posts = cls.objects.filter(
            status='published',
            created_at__year=year,
            created_at__month=month
        ).annotate(
            day=ExtractDay('created_at')
        ).values_list('day', flat=True).distinct()
        
        return set(days_with_posts)

    @classmethod
    def search(cls, query):
        """
        Search posts using PostgreSQL full-text search.
        Searches in title and excerpt fields.
        """

        search_vector = SearchVector('title', weight='A') + \
                       SearchVector('excerpt', weight='B')
        search_query = SearchQuery(query)

        return cls.objects.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(
            rank__gt=0
        ).order_by('-rank')