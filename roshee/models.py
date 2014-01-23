from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db import models

class Deal(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200)
    start_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField()
    
    def blah(self):
        
    
class DealMessage(models.Model):
    user = models.ForeignKey(User)
    deal = models.ForeignKey(Deal)
    description = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)