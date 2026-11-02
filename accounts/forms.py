"""
Forms are the boxes people fill in on the website.
Each form lists its fields, checks what was typed, and saves it.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from .models import Profile


class RegisterForm(UserCreationForm):
    """
    The sign-up form.

    Django's ready-made UserCreationForm already handles the username,
    the password and the "type your password again" box. We add an
    email address and the customer/worker choice.
    """

    email = forms.EmailField(required=True)

    # Shown as two round buttons: Customer or Worker.
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        widget=forms.RadioSelect
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'role',
            'password1',
            'password2',
        ]

    def save(self, commit=True):
        # "commit=False" means "prepare the user but don't save yet".
        # In that case we just hand the unsaved user back.
        if not commit:
            return super().save(commit=False)

        # Save the new user and their profile together.
        # If either one fails, neither is saved, so we never end up
        # with a user who has no profile.
        with transaction.atomic():
            user = super().save(commit=True)
            Profile.objects.create(
                user=user,
                role=self.cleaned_data['role']
            )

        return user


class ProfileForm(forms.ModelForm):
    """
    The "Edit your profile" form, for updating contact details
    after signing up.

    The role (customer or worker) is deliberately NOT on this form,
    so nobody can change their own role.
    """

    email = forms.EmailField(required=True)

    # The database only keeps 15 characters, but we allow up to 25
    # here so people can type spaces and dashes. clean_phone() below
    # removes them before saving.
    phone = forms.CharField(
        required=False,
        max_length=25,
        help_text='Spaces and dashes are fine. Start with + for a country code.'
    )

    class Meta:
        model = Profile
        fields = ['phone', 'location']
        labels = {
            'location': 'Area / city',
        }

    # The order the boxes appear on the page.
    field_order = ['email', 'phone', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Email is stored on the User, not the Profile,
        # so fill in the current email by hand.
        self.fields['email'].initial = self.instance.user.email

    def clean_phone(self):
        """
        Tidy up and check the phone number.
        For example "+1 (555) 123-4567" is saved as "+15551234567".
        """
        phone = self.cleaned_data['phone']

        # Remove spaces, brackets and dashes.
        phone = ''.join(phone.split())
        phone = phone.replace('(', '').replace(')', '').replace('-', '')

        # An empty phone number is allowed.
        if phone == '':
            return phone

        # A "+" at the start (for a country code) is allowed.
        # Everything after it must be numbers, between 7 and 14 of them.
        numbers = phone.removeprefix('+')
        if not numbers.isdecimal() or not 7 <= len(numbers) <= 14:
            raise forms.ValidationError('Enter a valid phone number.')

        return phone

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Put the new email onto the user account.
        profile.user.email = self.cleaned_data['email']

        # Save the email and the profile together, or neither.
        if commit:
            with transaction.atomic():
                profile.user.save(update_fields=['email'])
                profile.save()

        return profile
