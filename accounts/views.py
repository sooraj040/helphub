"""
Views decide what happens when someone opens a page.

Each view receives the visitor's request (which page they asked for,
what they typed into a form, who they are logged in as) and sends
back a page to show, or sends them to another page.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import ProfileForm, RegisterForm
from .models import Profile


# The service categories shown on the homepage.
# For now they are typed in here. In Phase 2 they will come from
# the database, so the admin can add or remove them.
POPULAR_CATEGORIES = [
    {'name': 'Plumbing', 'description': 'Leaks, blockages and fittings'},
    {'name': 'Electrical work', 'description': 'Wiring, switches and lights'},
    {'name': 'Home cleaning', 'description': 'Regular and deep cleaning'},
    {'name': 'Appliance repair', 'description': 'Washing machines, fridges and more'},
    {'name': 'Carpentry', 'description': 'Furniture, doors and shelves'},
    {'name': 'Painting', 'description': 'Interior and exterior walls'},
    {'name': 'AC repair', 'description': 'Servicing, repairs and installation'},
    {'name': 'Moving and delivery', 'description': 'Moving homes and goods'},
    {'name': 'Gardening', 'description': 'Lawns, plants and outdoor upkeep'},
    {'name': 'Other services', 'description': 'Anything else you need a hand with'},
]


def home_view(request):
    """The public homepage. Anyone can see it without logging in."""
    return render(
        request,
        'home.html',
        {'categories': POPULAR_CATEGORIES}
    )


def register_view(request):
    """The sign-up page."""

    # Someone who is already logged in doesn't need a new account,
    # so send them to their dashboard.
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        # The visitor pressed "Create Account". Check what they typed.
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Everything is fine: create the account and profile,
            # then send them to the login page with a success notice.
            form.save()
            messages.success(
                request,
                'Account created successfully. Please log in.'
            )
            return redirect('accounts:login')

        # If something was wrong, we fall through to the bottom and
        # show the form again, with the error messages next to the boxes.
    else:
        # The visitor has just opened the page. Show an empty form.
        form = RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


def login_view(request):
    """The login page."""

    # Already logged in? Go straight to the dashboard.
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    # If someone tried to open a members-only page first, Django sends
    # them here with "?next=" and that page's address, so we can take
    # them back there after they log in.
    next_url = request.POST.get('next') or request.GET.get('next', '')

    # Remembered so the username box stays filled in after a mistake.
    username = ''

    if request.method == 'POST':
        # The visitor pressed "Log In".
        username = request.POST.get('username', '')
        password = request.POST.get('password')

        # Check the username and password. This gives back the user
        # if they match, or None if they don't.
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            # Only follow "next" if it is a page on HelpHub itself.
            # This stops tricks that send people to other websites.
            next_is_safe = url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            )
            if next_is_safe:
                return redirect(next_url)

            return redirect('accounts:dashboard')

        # Wrong username or password.
        messages.error(request, 'Invalid username or password.')

    return render(
        request,
        'accounts/login.html',
        {'next': next_url, 'username': username}
    )


# "@login_required" means: if the visitor isn't logged in,
# send them to the login page instead of showing this page.
@login_required
def dashboard_view(request):
    """Shows the customer dashboard or the worker dashboard."""

    # Find this user's profile.
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # No profile means no customer/worker role. This happens for
        # admin accounts made with the "createsuperuser" command.
        # Staff members go to the admin site instead.
        if request.user.is_staff:
            return redirect('admin:index')

        # Anyone else sees a "your account isn't set up yet" page.
        return render(request, 'accounts/no_role.html')

    # Pick the right dashboard for their role.
    if profile.role == 'worker':
        template_name = 'accounts/worker_dashboard.html'
    else:
        template_name = 'accounts/customer_dashboard.html'

    return render(request, template_name, {'profile': profile})


@login_required
def profile_edit_view(request):
    """The "Edit your profile" page for phone, location and email."""

    # Users without a profile have nothing to edit.
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        # The user pressed "Save Changes". Check what they typed.
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:dashboard')
    else:
        # The user has just opened the page. Show their current details.
        form = ProfileForm(instance=profile)

    return render(
        request,
        'accounts/profile_edit.html',
        {'form': form}
    )
