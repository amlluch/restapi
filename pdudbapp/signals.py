from __future__ import unicode_literals
from django.dispatch import receiver
from django.contrib.auth.models import User
from models import Users as Userpdu
from models import Idata
from django.db.models.signals import post_save, post_delete
import random
import string

 
def randomHash():
    cadena=''
    for i in range(25):
        cadena = cadena + random.choice(string.letters)
    return cadena
     
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            Userpdu.objects.using('pdudb').get(user=instance)
        except:
            nuevousuario = Userpdu.objects.using('pdudb').create(user=instance)
             
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_superuser:
        Userpdu.objects.using('pdudb').filter(user=instance.username).delete()
        return 
    pduUser = Userpdu.objects.using('pdudb').get(user=instance.username)
    pduUser.password = instance.password
    if pduUser.challenge == None or pduUser.challenge == '':
        pduUser.challenge = randomHash()
    pduUser.email = instance.email
    pduUser.save()
    
@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    Userpdu.objects.using('pdudb').filter(user=instance.username).delete()
    Idata.objects.using('pdudb').filter(user=instance.username).update(user="", userkey = None)
            