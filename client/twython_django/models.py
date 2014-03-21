from django.contrib.auth.models import User
from django.db import models

class TwitterProfile(models.Model):
    user = models.OneToOneField(User)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)
