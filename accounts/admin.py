"""
Settings for the admin site at /admin/, where staff manage HelpHub.
This file controls what staff see on the user and profile pages.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    """
    Shows the profile (role, phone, location) inside each user's
    admin page, so staff can see and edit everything in one place.
    """
    model = Profile
    can_delete = False   # the profile can't be deleted on its own
    extra = 0            # don't show an extra empty profile form


class HelpHubUserAdmin(UserAdmin):
    """
    Django's normal admin page for users, with HelpHub additions.
    """

    # Show the profile on each user's page.
    inlines = (ProfileInline,)

    # Columns on the list of users: Django's usual ones,
    # plus the HelpHub role and whether the account is active.
    list_display = UserAdmin.list_display + ('get_helphub_role', 'is_active')

    # Filters on the right-hand side: Django's usual ones, plus role.
    list_filter = UserAdmin.list_filter + ('profile__role',)

    # Load each user's profile in the same database query (faster).
    list_select_related = ('profile',)

    @admin.display(description='HelpHub Role')
    def get_helphub_role(self, obj):
        # The text for the "HelpHub Role" column.
        try:
            return obj.profile.get_role_display()
        except Profile.DoesNotExist:
            return 'No profile'


# Swap Django's normal user admin page for our improved one.
admin.site.unregister(User)
admin.site.register(User, HelpHubUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    A separate admin page listing every profile.
    """

    # Columns on the list.
    list_display = ('user', 'role', 'phone', 'location')

    # Filter by Customer or Worker.
    list_filter = ('role',)

    # What the search box looks through.
    search_fields = ('user__username', 'user__email', 'phone')

    # Load each profile's user in the same database query (faster).
    list_select_related = ('user',)
