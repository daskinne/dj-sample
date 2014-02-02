from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.conf import settings
from guardian.shortcuts import *
from django.core.mail import send_mail
import os
from uuid import uuid4
import hmac
import time
import base64
import urllib
import hashlib

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

    def is_seller(self, user):
        return user.has_perm('seller', self)

    def add_user(self, email, message, is_buyer):
        #Check if user exists
        user = None
        if User.objects.filter(email=email).count() > 0:
            user = User.objects.get(email=email)
            assign_perm('buyer' if is_buyer else 'seller', user, self)
            send_mail('A deal has been shared with you on Roshee', message +
                      '\n\n The deal can be viewed at:\n'
                      'http://my.roshee.com/deal/'+str(self.id)+'\n\n Thanks, Roshee', 'support@roshee.com',
                      [email], fail_silently=False)
            print 'sending invite'
        else:
            #send invite email here
            send_mail('A deal has been shared with you on Roshee', message +
                      '\n\n\n Please signup to view the deal at:\nhttp://my.roshee.com/accounts/signup'
                      '\n\n The deal can be viewed at:\n'
                      'http://my.roshee.com/deal/'+str(self.id)+'\n\n Thanks, Roshee', 'support@roshee.com',
                      [email], fail_silently=False)
            PendingPermissions(deal=self,
                               email=email,
                               is_buyer=is_buyer).save()
            print 'sending registration'

    @property
    def pending_users(self):
        return PendingPermissions.objects.filter(deal=self).values('email')


def permission_filter(user_is_buyer):
    return Q(is_private=False)| Q(is_buyer=user_is_buyer,is_shared=True)


class DealMessage(models.Model):
    user = models.ForeignKey(User)
    deal = models.ForeignKey(Deal)
    message = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    is_buyer = models.BooleanField(default=True)
    is_private = models.BooleanField(default=True)#if only shown for user
    is_shared = models.BooleanField(default=False)#if shared with counterparty
    #bool if party or counterparty to allow filtering
    g = models.BooleanField(default=True)


def get_upload_path(instance, filename):
    return os.path.join(
      "deal","%d" % instance.deal.id, "%s-%s" % (str(uuid4()), filename))

class Attachment(models.Model):
    deal = models.ForeignKey(Deal)
    data = models.FileField(upload_to=get_upload_path)
    is_private = models.BooleanField(default=True)#if only shown for user
    is_shared = models.BooleanField(default=False)#if shared with counterparty
    file_name = models.CharField(max_length='200')
    #bool if party or counterparty to allow filtering
    is_buyer = models.BooleanField(default=True)

    def gen_signature(self, string_to_sign):
        return base64.encodestring(
            hmac.new(
                settings.AWS_SECRET_ACCESS_KEY,
                string_to_sign,
                hashlib.sha1
            ).digest()
        ).strip()

    @property
    def download_link(self):
        #permission logic here
        return str(self.get_auth_link())

    def get_auth_link(self, expires=300, timestamp=None):
        ''' Return a secure S3 link with an expiration on the download.
            expires: Seconds from NOW the link expires
            timestamp: Epoch timestamp. If present, "expires" will not be used.
        '''
        filename = urllib.quote_plus(str(self.data))
        filename = filename.replace('%2F', '/')
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        path = '/%s/%s' % (bucket, filename)

        if timestamp is not None:
            expire_time = float(timestamp)
        else:
            expire_time = time.time() + expires
        expire_str = '%.0f' % (expire_time)
        string_to_sign = u'GET\n\n\n%s\n%s' % (expire_str, path)
        params = {
            'AWSAccessKeyId': settings.AWS_ACCESS_KEY_ID,
            'Expires': expire_str,
            'Signature': self.gen_signature(string_to_sign.encode('utf-8')),
        }

        return 'http://%s.s3.amazonaws.com/%s?%s' % (
                                    bucket, filename, urllib.urlencode(params))




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
        perm.delete()
    print 'Permissions assigned'


