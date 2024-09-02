from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Incident

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'pin_code']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Firstname'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lastname'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pin Code'}),
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'pin_code']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Firstname'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lastname'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pin Code'}),
        }

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=None, from_email=None,
             request=None, html_email_template_name=None, extra_email_context=None):
        email = self.cleaned_data["email"]
        user = CustomUser.objects.filter(email=email).first()
        if user:
            # Generate a password reset token and send the email
            super().save(
                domain_override=domain_override,
                subject_template_name=subject_template_name,
                email_template_name=email_template_name,
                use_https=use_https,
                token_generator=token_generator,
                from_email=from_email,
                request=request,
                html_email_template_name=html_email_template_name,
                extra_email_context=extra_email_context
            )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}))

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 != new_password2:
            raise ValidationError("Passwords do not match")

        return cleaned_data




class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['incident_id', 'reporter', 'details', 'priority', 'status', 'entity_type']
        widgets = {
            'incident_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'reporter': forms.Select(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'entity_type': forms.Select(attrs={'class': 'form-control'}),
        }

