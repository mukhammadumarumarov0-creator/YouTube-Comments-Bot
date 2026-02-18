from django.contrib import admin
from .models import User, Video, Comment
from django.contrib.auth.hashers import make_password
# -------------------------------
# User Admin
# -------------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'full_name',
        'telegram_id', 'email',
        'is_staff', 'is_active'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'full_name', 'telegram_id', 'email', 'phone')
    ordering = ('id',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password',
                'full_name',
                'email',
                'phone',
                'telegram_id'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Agar parol oddiy text bo‘lsa → avtomatik HASH qilamiz
        """
        if obj.password and not obj.password.startswith('pbkdf2_'):
            obj.password = make_password(obj.password)

        super().save_model(request, obj, form, change)

# -------------------------------
# Video Admin
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    # Admin list view – ko'rinadigan ustunlar
    list_display = ('id', 'title', 'url', 'user', 'youtube_id', 'length', 'keywords', 'created_at')
    list_filter = ('created_at', 'user')
    
    # Qidiruv
    search_fields = ('title', 'youtube_id', 'url', 'user__username', 'user__full_name')
    
    # Tartib
    ordering = ('-created_at',)
    
    # Readonly fields
    readonly_fields = ('created_at',)
    
    # Form layout
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'url', 'youtube_id', 'length', 'keywords')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'user_name', 'youtube_id', 'comment_id', 'sent_to_telegram', 'created_at')
    list_filter = ('sent_to_telegram', 'created_at', 'video')
    search_fields = ('user_name', 'youtube_id', 'comment_id', 'video__title', 'video__user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('video', 'user_name', 'youtube_id', 'comment_id', 'text', 'sent_to_telegram')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
