from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

def user_avatar_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/avatar/<filename>
    return f'user_{instance.id}/avatar/{filename}'

class CustomUser(AbstractUser):
    bio = models.TextField(_('bio'), max_length=500, blank=True)
    avatar = models.ImageField(_('avatar'), upload_to=user_avatar_path, null=True, blank=True)

    # Add related_name to resolve reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_set',
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_set',
        help_text=_('Specific permissions for this user.'),
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username
