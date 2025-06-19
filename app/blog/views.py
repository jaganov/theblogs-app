from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from .models import Post

User = get_user_model()

def health_check(request):
    """
    Health check endpoint for monitoring
    """
    return HttpResponse("healthy", content_type="text/plain")

# Create your views here.
def index(request):
    """
    Blog main page
    """
    # Get published posts
    posts = Post.objects.filter(status='published').order_by('-created_at')

    # Pagination
    paginator = Paginator(posts, 3)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'blog/index.html', context)

def authors_list(request):
    """
    View for displaying all authors with their post counts
    """
    # Get all users who have published posts
    authors = User.objects.annotate(
        post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
    ).filter(post_count__gt=0).order_by('-post_count')

    # Pagination
    paginator = Paginator(authors, 12)  # Show 12 authors per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'blog/authors_list.html', context)

def days_with_posts(request):
    """
    API endpoint to get days with posts for a given month
    """
    try:
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
        days = Post.get_days_with_posts(year, month)
        return JsonResponse({'days': list(days)})
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid year or month'}, status=400)

@login_required
def create_post(request):
    """
    View for creating a new blog post
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        featured_image = request.FILES.get('featured_image')
        status = request.POST.get('status', 'draft')
        excerpt = request.POST.get('excerpt', '')
        image_caption = request.POST.get('image_caption', '')

        post = Post(
            title=title,
            content=content,
            author=request.user,
            featured_image=featured_image,
            status=status,
            excerpt=excerpt,
            image_caption=image_caption
        )
        post.save()

        messages.success(request, 'Post created successfully!')
        return redirect('blog:post_detail', post_slug=post.slug)

    context = {}
    return render(request, 'blog/create_post.html', context)

def post_detail(request, post_slug):
    """
    View for displaying a single blog post
    Shows draft posts only to their authors, published posts to everyone
    """
    post = get_object_or_404(Post, slug=post_slug)

    if post.status == 'draft' and (not request.user.is_authenticated or post.author != request.user):
        messages.error(request, 'This post is not available.')
        return redirect('blog:index')

    if post.status == 'published':
        post.views += 1
        post.save(update_fields=['views'])

    related_posts = Post.objects.filter(
        status='published'
    ).exclude(
        id=post.id
    ).distinct()[:3]

    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)

def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user_profile, status='published').order_by('-created_at')
    published_posts_count = posts.count()

    # Pagination - 5 posts per page
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user_profile': user_profile,
        'page_obj': page_obj,
        'published_posts_count': published_posts_count,
    }
    return render(request, 'blog/profile.html', context)

def search(request):
    query = request.GET.get('q', '')
    date = request.GET.get('date', '')
    
    if date:
        try:
            # Parse the date string (format: YYYY-MM-DD)
            from datetime import datetime
            search_date = datetime.strptime(date, '%Y-%m-%d').date()
            posts = Post.objects.filter(
                created_at__date=search_date,
                status='published'
            ).order_by('-created_at')
            query = f"Posts from {search_date.strftime('%B %d, %Y')}"
        except ValueError:
            posts = Post.objects.none()
    elif query:
        posts = Post.search(query)
    else:
        # Show all published posts when no search parameters
        posts = Post.objects.filter(status='published').order_by('-created_at')
        query = 'All Latest Articles'
    
    # Pagination - 7 posts per page
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/search.html', {
        'page_obj': page_obj,
        'posts': page_obj,
        'query': query,
        'date': date
    })

def privacy_policy(request):
    return render(request, 'blog/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'blog/terms_of_service.html')

def contact(request):
    return render(request, 'blog/contact.html')
