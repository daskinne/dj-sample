from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from guardian.shortcuts import *
from django.core.mail import send_mail

class Deal(models.Model):
    owner = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200)
    start_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        permissions = (
                ('buyer', 'Buyer'),
                ('seller', 'Seller'),
            )
    #future, add tasks, sub-permissions

    @property
    def participants(self):
        assigned_users = get_users_with_perms(self, attach_perms=True)
        buyers = []
        sellers = []
        users = []
        for user, perms in assigned_users.iteritems():
            print user, perms
            if 'buyer' in perms:
                buyers.append(user)
            else:
                sellers.append(user)
            users.append(user)
        return {'users': users, 'buyers': buyers, 'sellers':sellers}

    def is_buyer(self, user):
        return user.has_perm('buyer', self)

    def add_user(self, email, message, is_buyer):
        #Check if user exists
        user = None
        if User.objects.filter(email=email).count() > 0:
            user = User.objects.get(email=email)
            assign_perm('buyer' if is_buyer else 'seller', user, self)
            send_mail('A deal has been shared with you on Roshee', message +
                      '\n\n The deal can be viewed at:\n'
                      'http://localhost:8000/deal/'+str(self.id)+'\n\n Thanks, Roshee', 'support@roshee.com',
                      [email], fail_silently=False)
            print 'sending invite'
        else:
            #send invite email here
            send_mail('A deal has been shared with you on Roshee', form.cleaned_data['message'] +
                      '\n\n\n Please signup to view the deal at:\nhttp://localhost:8000/accounts/signup'
                      '\n\n The deal can be viewed at:\n'
                      'http://localhost:8000/deal/'+str(self.id)+'\n\n Thanks, Roshee', 'support@roshee.com',
                      [email], fail_silently=False)
            PendingPermissions(deal=self,
                               email=email,
                               is_buyer=is_buyer).save()
            print 'sending registration'


def permission_filter(user_is_buyer):
    return Q(is_private=False)|Q(is_buyer=user_is_buyer)


class DealMessage(models.Model):
    user = models.ForeignKey(User)
    deal = models.ForeignKey(Deal)
    message = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=True)
    #bool if party or counterparty to allow filtering
    is_buyer = models.BooleanField(default=True)


class Attachment(models.Model):
    deal = models.ForeignKey(Deal)
    data = models.FileField(upload_to='attachments')
    is_private = models.BooleanField(default=True)
    #bool if party or counterparty to allow filtering
    is_buyer = models.BooleanField(default=True)


def handle_uploaded_file(user, deal, file):
    with open('deal/%s/%s/%s' % deal.id, is_buyer, file.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
class PendingPermissions(models.Model):
    deal = models.ForeignKey(Deal)
    email = models.EmailField()
    is_buyer = models.BooleanField(default=True)

from userena.signals import activation_complete


def user_activated(user, **kwargs):
    perms = PendingPermissions.objects.filter(email=user.email)
    for perm in perms:
        assign_perm('buyer' if perm.is_buyer else 'seller', user, perm.deal)
    print 'Permissions assigned'


