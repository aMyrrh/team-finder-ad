from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .models import User

ABOUT_TEXTAREA_ROWS = 4


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Неверный email или пароль.")
            if not user.is_active:
                raise forms.ValidationError("Аккаунт заблокирован.")
            cleaned["user"] = user
        return cleaned


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "about", "phone", "github_url", "avatar"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
            "avatar": "Аватар",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": ABOUT_TEXTAREA_ROWS}),
        }
