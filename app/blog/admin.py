from django.contrib import admin
from django.utils.html import format_html
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'views', 'reading_time', 'display_image')
    list_filter = ('status', 'created_at', 'author')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'views', 'reading_time')
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('Content', {
            'fields': ('content', 'excerpt')
        }),
        ('Image', {
            'fields': ('featured_image', 'image_caption'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views', 'reading_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_image(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.featured_image.url)
        return "No Image"
    display_image.short_description = 'Image'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
