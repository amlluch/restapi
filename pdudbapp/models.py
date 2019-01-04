# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Users(models.Model):
    indice = models.IntegerField(db_column='indice', primary_key=True)
    user = models.TextField(db_column='user', blank=False, null=False, unique=True)
    password = models.TextField(db_column='password', blank=False, null=True)
    challenge = models.TextField(db_column='challenge', blank=True, null=True)
    email = models.EmailField(db_column='email', blank=True, null=True, unique=True)
    
#     outlets = property(_get_outlets)


    class Meta:
        managed = False
        db_table = 'users'

    @property
    def username(self):
        return self.user


class Idata(models.Model):
    indice = models.IntegerField(db_column='indice', primary_key=True)  # Field name made lowercase.
    posicion = models.IntegerField(db_column='posicion', blank=True, null=True)
    nombre = models.TextField(db_column='Nombre', blank=True, null=True)  # Field name made lowercase.
    fres = models.TextField(db_column='Fres', blank=True, null=True)  # Field name made lowercase.
    forden = models.IntegerField(db_column='Forden', blank=True, null=True)  # Field name made lowercase.
    entrada = models.IntegerField(db_column='Entrada', blank=True, null=True)  # Field name made lowercase.
    device = models.IntegerField(db_column='Device', blank=True, null=True)  # Field name made lowercase.
    salida = models.IntegerField(db_column='Salida', blank=True, null=True)  # Field name made lowercase.
    oid_set = models.TextField(db_column='Oid_set', blank=True, null=True)  # Field name made lowercase.
    oid_get = models.TextField(db_column='Oid_get', blank=True, null=True)  # Field name made lowercase.
    walk = models.TextField(blank=True, null=True)
    walk3 = models.TextField(blank=True, null=True)
    estado = models.TextField(db_column='estado', blank=True, null=True)
    user = models.TextField(db_column='user', blank=True, null=True)
    password = models.TextField(db_column='password', blank=True, null=True)
    userkey = models.ForeignKey(Users, blank=True , null=True, db_column='userkey', on_delete=models.SET_NULL) 

    class Meta:
        managed = False
        db_table = 'idata'

    @property
    def position(self):
        return self.posicion

    def name(self):
        return self.nombre

    def status(self):
        if (self.estado.strip() == "0"):
            return "OFF"
        else:
            return "ON"
        
    def username(self):
        return self.user

NINGUNA = 25
SSL = 465
TLS = 587
NOSEC = None
SSL_SEC = 'use_ssl'
TLS_SEC = 'use_tls'
SEGURIDAD_CHOICES =(
    (NOSEC, 'ninguna'),
    (SSL_SEC, 'ssl'),
    (TLS_SEC, 'tls'),
    )

class Smtp(models.Model):
    
    indice = models.IntegerField(db_column='indice', primary_key=True)
    host = models.CharField(db_column = 'host', blank=False, null=False, max_length=35)
    port = models.IntegerField(db_column = 'port', blank=True, null=True, default=25)
    security =models.CharField(db_column= 'security', blank=True, null=True, choices=SEGURIDAD_CHOICES, default = NOSEC, max_length=8)
    username = models.CharField(db_column='username', blank=True, null=True, max_length=35)
    password = models.CharField(db_column='password', blank=True, null=True, max_length=35)
    returnaddress = models.EmailField(db_column='returnaddress', blank=True, null=True, max_length=35)
    
    class Meta:
        managed = False
        db_table = 'smtp'
