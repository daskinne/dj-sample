from django.contrib.auth.models import User
from django.db import models

class Deal(models.Model):
    owner = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200)
    start_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

class DealMessage(models.Model):
    user = models.ForeignKey(User)
    deal = models.ForeignKey(Deal)
    message = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)