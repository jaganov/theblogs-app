from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import CustomUser
from blog.models import Post

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        bio = request.POST.get('bio', '')
        avatar = request.FILES.get('avatar')

        if password1 != password2:
            messages.error(request, "Passwords don't match")
            return redirect('account:register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('account:register')

        user = CustomUser.objects.create_user(
            username=username,
            password=password1,
            bio=bio
        )
        if avatar:
            user.avatar = avatar
            user.save()

        login(request, user)
        return redirect('account:profile')

    return render(request, 'account/register.html')

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    '<div class="alert alert-danger">Please enter both username and password</div>',
                    content_type='text/html',
                    status=400
                )
            messages.error(request, "Please enter both username and password")
            return redirect('account:login')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = '/account/profile/'
                return response
            return redirect('account:profile')
        else:
            error_message = '<div class="alert alert-danger">Invalid username or password</div>'
            if request.headers.get('HX-Request'):
                response = HttpResponse(
                    error_message,
                    content_type='text/html',
                    status=400
                )
                response['HX-Trigger'] = '{"showError": true}'
                return response
            messages.error(request, "Invalid username or password")
            return redirect('account:login')

    return render(request, 'account/login.html')

@login_required
def profile_view(request):
    user = request.user
    status_filter = request.GET.get('status', 'published')

    posts = Post.objects.filter(author=user)
    if status_filter == 'draft':
        posts = posts.filter(status='draft')
    else:
        posts = posts.filter(status='published')

    posts = posts.order_by('-created_at')

    paginator = Paginator(posts, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user': user,
        'posts': page_obj,
        'page_obj': page_obj,
        'published_count': Post.objects.filter(author=user, status='published').count(),
        'draft_count': Post.objects.filter(author=user, status='draft').count(),
        'current_filter': status_filter,
    }
    return render(request, 'account/profile.html', context)

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.bio = request.POST.get('bio', user.bio)

        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']

        user.save()
        messages.success(request, "Profile updated successfully")
        return redirect('account:profile')

    return render(request, 'account/edit_profile.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('account:login')

@login_required
def edit_post(request, post_slug):
    """View for editing an existing post"""
    post = get_object_or_404(Post, slug=post_slug, author=request.user)

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.excerpt = request.POST.get('excerpt')
        post.status = request.POST.get('status')

        if 'featured_image' in request.FILES:
            post.featured_image = request.FILES['featured_image']
        post.image_caption = request.POST.get('image_caption')

        post.save()
        messages.success(request, 'Post updated successfully!')
        return redirect('account:profile')

    return render(request, 'account/edit_post.html', {
        'post': post,
    })

@login_required
def delete_post(request, post_slug):
    """View for deleting a post"""
    post = get_object_or_404(Post, slug=post_slug, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('account:profile')

    return render(request, 'account/delete_post.html', {'post': post})
