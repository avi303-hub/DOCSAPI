from django.db import models
from django.contrib.auth.models import User

class UserGoogleAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_access_token = models.CharField(max_length=255)
    google_refresh_token = models.CharField(max_length=255)
    token_expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Google Auth"
