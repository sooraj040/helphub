"""
The main list of web addresses on HelpHub.

Each line connects an address to the code that builds that page.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from accounts.views import home_view

urlpatterns = [
    # /  → the homepage
    path('', home_view, name='home'),

    # /accounts/...  → sign up, log in, dashboard and so on.
    # The full list is in accounts/urls.py.
    path('accounts/', include('accounts.urls')),

    # /admin/  → Django's admin site for staff
    path('admin/', admin.site.urls),

    # The simple information pages linked from the footer.
    # TemplateView just shows a page, with no extra logic.
    path(
        'about/',
        TemplateView.as_view(template_name='pages/about.html'),
        name='about'
    ),
    path(
        'contact/',
        TemplateView.as_view(template_name='pages/contact.html'),
        name='contact'
    ),
    path(
        'privacy/',
        TemplateView.as_view(template_name='pages/privacy.html'),
        name='privacy'
    ),
    path(
        'terms/',
        TemplateView.as_view(template_name='pages/terms.html'),
        name='terms'
    ),
]
