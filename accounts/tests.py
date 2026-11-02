"""
Automatic checks for the accounts part of HelpHub.

Each test pretends to be a visitor (signing up, logging in, opening
pages) and checks the site responds correctly. They run on a temporary
copy of the database, so real accounts are never touched.

Run them with:   python manage.py test accounts
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


# A password that passes all the password rules, used by every test.
PASSWORD = 'Str0ng-Passw0rd!'


def make_user(username, role):
    """Create a test user with a customer or worker profile."""
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password=PASSWORD
    )
    Profile.objects.create(user=user, role=role)
    return user


class PublicPageTests(TestCase):
    """Pages anyone can open without an account."""

    def test_public_pages_load_without_login(self):
        for name in ['home', 'about', 'contact', 'privacy', 'terms',
                     'accounts:login', 'accounts:register']:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)


class RegistrationTests(TestCase):
    """Signing up as a customer or a worker."""

    def register(self, **overrides):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'role': 'customer',
            'password1': PASSWORD,
            'password2': PASSWORD,
        }
        data.update(overrides)
        return self.client.post(reverse('accounts:register'), data)

    def test_register_creates_user_with_chosen_role(self):
        for role in ['customer', 'worker']:
            with self.subTest(role=role):
                response = self.register(username=f'new_{role}', role=role)

                self.assertRedirects(response, reverse('accounts:login'))
                profile = Profile.objects.get(user__username=f'new_{role}')
                self.assertEqual(profile.role, role)

    def test_duplicate_username_shows_error(self):
        make_user('taken', 'customer')

        response = self.register(username='taken')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')

    def test_unknown_role_is_rejected(self):
        response = self.register(role='admin')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_email_is_required(self):
        response = self.register(email='')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())


class LoginLogoutTests(TestCase):
    """Logging in and out."""

    def setUp(self):
        make_user('cust', 'customer')

    def test_valid_login_goes_to_dashboard(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'cust', 'password': PASSWORD}
        )
        self.assertRedirects(response, reverse('accounts:dashboard'))

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'cust', 'password': 'wrong'}
        )
        self.assertContains(response, 'Invalid username or password.')

    def test_login_follows_safe_next_url(self):
        target = reverse('accounts:profile_edit')
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'cust', 'password': PASSWORD, 'next': target}
        )
        self.assertRedirects(response, target)

    def test_login_ignores_external_next_url(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'cust', 'password': PASSWORD,
             'next': 'https://evil.example.com/'}
        )
        self.assertRedirects(response, reverse('accounts:dashboard'))

    def test_logout_ends_session(self):
        self.client.login(username='cust', password=PASSWORD)

        self.client.post(reverse('accounts:logout'))

        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)


class DashboardTests(TestCase):
    """Each role reaches the right dashboard."""

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('accounts:dashboard'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:dashboard')}"
        )

    def test_customer_sees_customer_dashboard(self):
        self.client.force_login(make_user('cust', 'customer'))

        response = self.client.get(reverse('accounts:dashboard'))

        self.assertTemplateUsed(response, 'accounts/customer_dashboard.html')

    def test_worker_sees_worker_dashboard(self):
        self.client.force_login(make_user('work', 'worker'))

        response = self.client.get(reverse('accounts:dashboard'))

        self.assertTemplateUsed(response, 'accounts/worker_dashboard.html')

    def test_staff_without_profile_goes_to_admin(self):
        admin = User.objects.create_superuser('boss', 'boss@example.com', PASSWORD)
        self.client.force_login(admin)

        response = self.client.get(reverse('accounts:dashboard'))

        self.assertRedirects(response, reverse('admin:index'))

    def test_user_without_profile_sees_setup_message(self):
        user = User.objects.create_user('norole', password=PASSWORD)
        self.client.force_login(user)

        response = self.client.get(reverse('accounts:dashboard'))

        self.assertTemplateUsed(response, 'accounts/no_role.html')


class ProfileEditTests(TestCase):
    """Editing phone, location and email (but never the role)."""

    def setUp(self):
        self.user = make_user('cust', 'customer')
        self.client.force_login(self.user)

    def test_updates_contact_details(self):
        response = self.client.post(reverse('accounts:profile_edit'), {
            'email': 'updated@example.com',
            'phone': '+1 (555) 123-4567',
            'location': 'Downtown',
        })

        self.assertRedirects(response, reverse('accounts:dashboard'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.profile.phone, '+15551234567')
        self.assertEqual(self.user.profile.location, 'Downtown')

    def test_rejects_invalid_phone(self):
        response = self.client.post(reverse('accounts:profile_edit'), {
            'email': 'cust@example.com',
            'phone': 'call me',
            'location': '',
        })

        self.assertContains(response, 'Enter a valid phone number.')

    def test_role_cannot_be_changed(self):
        self.client.post(reverse('accounts:profile_edit'), {
            'email': 'cust@example.com',
            'phone': '',
            'location': '',
            'role': 'worker',
        })

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.role, 'customer')


class AdminTests(TestCase):
    """What staff see in the admin site."""

    def setUp(self):
        make_user('cust', 'customer')
        make_user('work', 'worker')
        admin = User.objects.create_superuser('boss', 'boss@example.com', PASSWORD)
        self.client.force_login(admin)

    def test_user_list_shows_roles(self):
        response = self.client.get(reverse('admin:auth_user_changelist'))

        self.assertContains(response, 'HelpHub Role')
        self.assertContains(response, 'Customer')
        self.assertContains(response, 'Worker')

    def test_profiles_can_be_filtered_by_role(self):
        response = self.client.get(
            reverse('admin:accounts_profile_changelist'),
            {'role__exact': 'worker'}
        )

        results = response.context['cl'].result_list
        self.assertEqual([p.user.username for p in results], ['work'])
