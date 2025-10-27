from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email).strip()
        user = self.model(email=email, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_active", True)
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password, **extra):
        extra.setdefault("is_active", True)
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if not extra["is_staff"] or not extra["is_superuser"]:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True")
        return self._create_user(email, password, **extra)

class User(AbstractBaseUser, PermissionsMixin):
    # minimal + stable
    email       = models.EmailField(unique=True, db_index=True)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        indexes = [models.Index(fields=["email"])]

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=150, blank=True)
    last_name  = models.CharField(max_length=150, blank=True)
    
    # User roles - can be both at the same time
    is_buyer  = models.BooleanField(default=False, help_text="User can buy products for holders (free users)")
    is_holder = models.BooleanField(default=False, help_text="User can receive products from buyers")

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.user.email
    
    def delete(self, *args, **kwargs):
        """Delete the User instead, which will cascade delete this Profile"""
        user = self.user
        # Delete the user, which will cascade delete this profile
        # We don't call super().delete() to avoid recursion
        return user.delete(*args, **kwargs)
