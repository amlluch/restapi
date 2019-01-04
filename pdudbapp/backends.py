from django.conf import settings
from django.contrib.auth.models import User

from pdudbapp.models import Users as Userpdu
from pdudbapp.models import Smtp

from django.conf import settings
from django.contrib.auth.hashers import BasePasswordHasher


import os
import requests

from Crypto import Random
from Crypto.Cipher import AES
import base64
from hashlib import md5
import string
import random

from django.contrib.auth.hashers import PBKDF2PasswordHasher
from collections import OrderedDict 
from django.core.mail.backends.smtp import EmailBackend

BLOCK_SIZE = 16

def pad(datos):
    length = BLOCK_SIZE - (len(datos) % BLOCK_SIZE)
    return datos + (chr(length)*length).encode()

def unpad(datos):
    return datos[:-(datos[-1] if type(datos[-1]) == int else ord(datos[-1]))]

def bytes_to_key(datos, salt, output=48):
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    datos = datos + salt
    key = md5(datos).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + datos).digest()
        final_key = final_key + key
    return final_key[:output]

def encrypt(message, passphrase):
    salt = Random.new().read(8)
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message)))

def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:]))

def makepassword(password, challenge):
    clave = (password).encode()
    return encrypt(str(challenge), clave)

class PduAuthBackend(object):
    def authenticate(self, username=None, password=None):
        uri = 'http://127.0.0.1:8089/auth'
        try:  # Comprueba si existe en la base de datos para obtener el challenge. Los super users no tienen challenge
            usuario = Userpdu.objects.using('pdudb').get(user=username)
            clave = (password).encode()
            passfinal = encrypt(str(usuario.challenge), clave)
        except:   # Podria ser un super usuario
            passfinal = password
        payload = {"username":username,"password":passfinal,"topic":"","acc":""}
        res = requests.post(uri, data=payload)
        if (res.status_code != 200) : 
            #Limpiamos el ficher de usuarios de django
            try:
                user = User.object.get(username=username)
                User.object.filter(username=username).delete()
            except:
                pass
            return None
        uri_super = 'http://127.0.0.1:8089/superuser'
        payload = {'username': username}
        super_resp = requests.post(uri_super, payload)
        is_superuser = super_resp.status_code == 200

        try:
            user = User.objects.get(username=username)
            if not is_superuser:
                user.set_password = password
                user.email = usuario.email
                user.save()
        except User.DoesNotExist:
            
            user = User(username=username)
            if is_superuser :
                user.is_staff = True
                user.is_superuser = True
            else:
                user.email = usuario.email
                
            user.set_password(password)
            user.save()


        return user
    
    def get_user(self, username):
        try:
            return User.objects.get(pk=username)
        except User.DoesNotExist:
            return None
        
class PduHasher(BasePasswordHasher):
    algorithm = "plain"
      
    def check_password(self, password, encoded, setter=None, preferred='default'):
        hasher_changed = False
        must_update = True
        if password is None or password == "" :
            return False
        return True
        
    def make_password(self, password, salt=None, hasher='default'):
        if password is None:
            return ""
        return password;
    def is_password_usable (self, encoded):
        if encoded is None or encoded=="":
            return False
        return True
    
    def verify(self, password, encoded):
        return password == encoded
    
    def encode(self, password, salt, iterations=None):
        assert salt == ''
        return password
    def salt(self):
        return ""
    def safe_summary(self, encoded):
        return OrderedDict([
            (_('algorithm'), self.algorithm),
            (_('hash'), encoded),
        ])
        
      
class PduEmailBackend(EmailBackend):
    
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None, **kwargs):
        super(PduEmailBackend, self).__init__(fail_silently=False)
        smtp = Smtp.objects.using('pdudb').first()
        if smtp:
            self.host = self.host if smtp.host is None else smtp.host
            self.port = self.port if smtp.port is None else smtp.port
            self.username = self.username if smtp.username is None else smtp.username
            self.password = self.password if smtp.password is None else smtp.password
            if smtp.security == 'use_tls':
                self.use_tls = True
            else: 
                self.use_tls = False
            if smtp.security == 'use_ssl':
                self.use_ssl = True
            else: 
                self.use_ssl = False
        