import re

from django import forms

from .models import UserAccount


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter your password"}
        ),
        label="Password",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm your password"}
        ),
        label="Confirm Password",
    )

    class Meta:
        model = UserAccount
        fields = ["username", "email", "password", "confirm_password"]
        widgets = {
            "username": forms.TextInput(
                attrs={"placeholder": "Enter your username"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Enter your email"}
            ),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if UserAccount.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if UserAccount.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        # Password strength validation
        if len(password) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters long"
            )
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter"
            )
        if not re.search(r"[a-z]", password):
            raise forms.ValidationError(
                "Password must contain at least one lowercase letter"
            )
        if not re.search(r"[0-9]", password):
            raise forms.ValidationError(
                "Password must contain at least one digit"
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError(
                "Password must contain at least one special character"
            )
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password != confirm:
            raise forms.ValidationError("Passwords do not match")


class ImageUploadForm(forms.Form):
    image = forms.ImageField(required=False)
