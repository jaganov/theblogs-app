from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('blog.urls'), name="blog"),
    path('account/', include('account.urls'), name="account"),

    path("health/", lambda r: HttpResponse("ok")),
    # While it is still under construction, we have to make it invisible for search robots. After we will update it.
    path("robots.txt", lambda r: HttpResponse(
        """User-agent: *
        Disallow: /
        """, content_type="text/plain")),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = """
The Blogs Dashboard
"""
admin.site.site_title = "The Blogs Dashboard"
admin.site.index_title = "Welcome to The Blogs Dashboard"

handler404 = 'app.views.custom_404_view'
