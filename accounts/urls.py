"""
The web addresses for accounts. Each line connects an address to the
view (in views.py) that builds that page.

All of these start with /accounts/ (see config/urls.py), so
'login/' here is the page at /accounts/login/.
"""

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

# Lets other files refer to these pages by name, e.g. 'accounts:login'.
app_name = 'accounts'

urlpatterns = [
    # /accounts/register/  → sign-up page
    path('register/', views.register_view, name='register'),

    # /accounts/login/  → login page
    path('login/', views.login_view, name='login'),

    # /accounts/dashboard/  → customer or worker dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # /accounts/profile/edit/  → edit phone, location and email
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    # /accounts/logout/  → logs the user out (Django's built-in view)
    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),
]
