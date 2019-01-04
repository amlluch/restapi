# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from pdudbapp.models import Users, Idata
from django.contrib.auth.models import User
import django.contrib.auth.password_validation as validators
from django.core import exceptions
import sys
from pdudbapp.backends import makepassword
import paho.mqtt.client as mqtt
from random import randint
from rest_framework.authtoken.models import Token
from rest_framework.fields import SkipField
from collections import OrderedDict
from rest_framework.validators import UniqueValidator

from django.conf import settings

class OutletUser(serializers.ModelSerializer):
       
    class Meta:
        model = Idata
        fields = ('position', 'name', 'status',)
        

class UserSerializer(serializers.ModelSerializer):
    
    outlets = OutletUser(read_only=True, source='idata_set', many=True)
      
    class Meta:
        model = Users
        fields = ('username', 'email', 'outlets')
        
        
    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if not field.write_only]
 
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue
 
            if (attribute is not None):
                represenation = field.to_representation(attribute)
                if represenation is None or represenation == '':
                    # No serializa objetos vacios
                    continue
                if isinstance(represenation, list) and not represenation:
                   # No serializa listas vacias
                   continue
                ret[field.field_name] = represenation
 
        return ret
    def validate_username(self, value):
        try:
            Users.objects.using('pdudb').get(user = value)
        except:
            raise serializers.ValidationError('User doesn\'t exist')
        return super(UserSerializer, self).validate(value)
    
class GetOutletSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Idata
        fields = ('position', 'name', 'status', 'username')
        
class OutletSerializer(serializers.ModelSerializer):
    
    position = serializers.IntegerField(required=False, max_value=23, min_value=1, read_only=True)
    name = serializers.CharField(required= False, max_length= 35, write_only=True)
    status = serializers.CharField(required= False, max_length= 3, write_only=True)
    username = serializers.CharField(required= False, max_length= 35, read_only=True)
    
    class Meta:
        model = Idata
        fields = ('position', 'name', 'status', 'username')
     
    def validate_status(self, value):
        valores = ['on', 'ON', 'On', 'off', 'Off', 'OFF']
        if not (value in valores):
            raise serializers.ValidationError('Status should be \'on\' or \'off\'')
        return super(OutletSerializer, self).validate(value)
        
    def update(self, instance, validated_data):
        
        if 'name' in validated_data:
            instance.nombre = validated_data['name']
            Idata.objects.using('pdudb').filter(posicion = instance.posicion).update(nombre=validated_data['name'])
#            instance.save()
        if 'status' in validated_data:
            if validated_data['status'] in ['on', 'ON', 'On']: 
                payload = "1"
            else: 
                payload = "2"
            topic = "device/set/" + str(instance.posicion)
            client = mqtt.Client(client_id="django" + str(randint(0,99)))
            usrmqtt = settings.IOT_USER
            finalpass = settings.IOT_PWD
            client.username_pw_set(usrmqtt, finalpass)
            client.connect(settings.IOT_HOST, settings.IOT_PORT, 10)
            client.publish(topic, payload, qos=0, retain=False)
            client.disconnect()
        return instance
        

class EntryPoint(serializers.Serializer):
    message = serializers.CharField(required= True, max_length =35)
    
    
class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """

    class Meta:
        model = Token
        fields = ('key',)
    

class ModifyUser(serializers.ModelSerializer):
    username = serializers.CharField(required= False, max_length =35, default = '', initial = '', read_only=True)
    email = serializers.EmailField(required = False, max_length = 55, read_only=True, default = '', initial = '', validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(required= False, max_length = 35, write_only=True, default = '', initial = '', style={'input_type': 'password'})
    position = serializers.IntegerField(required = False, max_value=23, min_value=1, write_only=True)
    name = serializers.CharField(required = False, max_length = 35)
    status = serializers.CharField(required = False, max_length = 5)
    rempos = serializers.BooleanField(required = False)
    
    class Meta: 
        model = Idata
        fields = ('username', 'email', 'password', 'position', 'name', 'status', 'rempos', )
        
        
    def __init__(self, *args, **kwargs):
        super(ModifyUser,self).__init__(*args, **kwargs)
        request = self.context['request']

        if request.method=='POST':
            self.fields['username'].required = True
            self.fields['username'].read_only = False
            self.fields['email'].read_only = False
            self.fields['email'].required = True
            self.fields['password'].required = True
            self.fields.pop('position')
            self.fields.pop('name')
            self.fields.pop('status')
            self.fields.pop('rempos')
            

        if request.user.is_superuser == False:
            self.fields.pop('rempos')
            

        try:

            if self.initial_data['name']!='':
                self.fields['position'].required = True
            if self.initial_data['status']!='':
                self.fields['position'].required = True
            if self.initial_data['rempos']!=False:
                self.fields['position'].required = True
          
        except:
            pass
        

    def validate_name(self, value):
        return super(ModifyUser, self).validate(value)
    
    def validate_rempos(self, value):
        request = self.context['request']
        if not request.user.is_superuser:
            raise serializers.ValidationError('Not authorized')
        return super(ModifyUser, self).validate(value)
    
    def validate_password(self, data):
        if data=='' : 
            return super(ModifyUser, self).validate(data)
        errors = dict() 
        try:
            validators.validate_password(password=data)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        return super(ModifyUser, self).validate(data)
    
    def validate_position(self, value):
        request = self.context['request']
        if not request.user.is_superuser:
            try:
                idata = Idata.objects.using('pdudb').get(posicion=value)
                if idata.user!=request.user.username:
                    raise serializers.ValidationError('Not authorized')
            except:
                raise serializers.ValidationError('Outlet doesn\'t exist')
        return super(ModifyUser, self).validate(value)
    
    def validate_status(self, value):
        valores = ['on', 'ON', 'On', 'off', 'Off', 'OFF']
        if not (value in valores):
            raise serializers.ValidationError('Status should be \'on\' or \'off\'')
        return super(ModifyUser, self).validate(value)
    
    def update(self, instance, validated_data):
        request = self.context['request']
        if 'password' in validated_data:
            if validated_data['password']!='':
                instance.set_password(validated_data['password'])
                # Changes token with new password
                try:
                    instance.auth_token.delete()
                except:
                    pass
            instance.save()
        if 'position' in validated_data:
            if 'rempos' in validated_data:
                remove = validated_data['rempos']
            else:
                remove = False
            if remove:
                Idata.objects.using('pdudb').filter(posicion = validated_data['position']).update(user='', userkey=None)
            else:
                usuario = Users.objects.using('pdudb').get(user = instance.username)
                Idata.objects.using('pdudb').filter(posicion = validated_data['position']).update(user=instance.username, userkey=usuario.pk)
        if 'name' in validated_data:
            Idata.objects.using('pdudb').filter(posicion = validated_data['position']).update(nombre=validated_data['name'])
        if 'status' in validated_data:
            if validated_data['status'] in ['on', 'ON', 'On']:
                payload = "1"
            else: 
                payload = "2"
            topic = "device/set/" + str(validated_data['position'])    
            client = mqtt.Client(client_id="django" + str(randint(0,99)))
            usrmqtt = instance.username
            if request.user.is_superuser: 
                usrmqtt = settings.IOT_USER
                finalpass = settings.IOT_PWD
            else:
                usuario = Users.objects.using('pdudb').get(user=instance.username)
                finalpass = makepassword(usuario.password, usuario.challenge)   #Encrypts password with AES
            client.username_pw_set(usrmqtt, finalpass)
            client.connect(settings.IOT_HOST, settings.IOT_PORT, 10)
            client.publish(topic, payload, qos=0, retain=False)
            client.disconnect()

        return instance
    
    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password = validated_data['password']
        return User.objects.create(**validated_data)
    