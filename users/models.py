from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager
from .utils import avatar_upload_path

NAME_MAX_LENGTH = 100
USER_PHONE_MAX_LENGTH = 30


class Skill(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    surname = models.CharField(max_length=NAME_MAX_LENGTH)
    email = models.EmailField(unique=True)
    about = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=USER_PHONE_MAX_LENGTH, blank=True, default="")
    github_url = models.URLField(blank=True, default="")
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name="users")
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} {self.surname}"
