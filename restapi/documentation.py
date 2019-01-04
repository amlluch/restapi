# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.schemas import  AutoSchema
import coreapi
import coreschema



@authentication_classes(( SessionAuthentication, BasicAuthentication, TokenAuthentication))
class CustomUserRestSchema(AutoSchema):

    def get_serializer_fields(self, path, method):
        
        extra_fields = []

        if method=='PUT':
            extra_fields = [

                coreapi.Field(
                    name='password',
                    required=False,
                    location='form',
                    schema=coreschema.String(
                    description="New password",
                    title= 'password',
                   )
                ),
                coreapi.Field(
                    name='position',
                    required=False,
                    location='form',
                    type = coreschema.Integer,
                    schema=coreschema.Integer(
                    description="Device outlet position. Mandatory for changing outlet name, remove user or outlet status. Must be an integer. Only admins can remove user from outlet",
                    title = "position"
                   )
                ),
                coreapi.Field(
                    name='name',
                    required=False,
                    location='form',
                    schema=coreschema.String(
                    description="Change the outlet name in the position provided",
                    title = 'name'
                   )
                ),
                coreapi.Field(
                    name='status',
                    required=False,
                    location='form',
                    type = coreschema.String,
                    schema=coreschema.String(
                    description="Turn on or off the remote server connected to the outlet position provided. Values accepted: \'on\' or \'off\'",
                    title = 'status'
                   )
                ),
                coreapi.Field(
                    name='rempos',
                    required=False,
                    location='form',
                    schema=coreschema.Boolean(
                    description="Remove user from position. Only for admins. Values accepted: True or False (False by default)",
                    title = 'rempos',
                   )
                ),
            ]

        manual_fields = super(CustomUserRestSchema, self).get_serializer_fields(path, method)
        return manual_fields + extra_fields
    
@authentication_classes(( SessionAuthentication, BasicAuthentication, TokenAuthentication))
class CustomAdminRestSchema(AutoSchema):
    
    def get_serializer_fields(self, path, method):
        
        extra_fields = []
        if method == 'POST':
            extra_fields=[
                coreapi.Field(
                    name='username',
                    required=True,
                    location='form',
                    schema=coreschema.String(
                    description="New user name"
                   )
                ),
                coreapi.Field(
                    name='email',
                    required=True,
                    location='form',
                    schema=coreschema.String(
                    description="User email. Must be unique"
                   )
                ),
                coreapi.Field(
                    name='password',
                    required=True,
                    location='form',

                    schema=coreschema.String(
                    description="New password"
                   )
                )
            ]
        manual_fields = super(CustomAdminRestSchema, self).get_serializer_fields(path, method)
        return manual_fields + extra_fields
    
@authentication_classes(( SessionAuthentication, BasicAuthentication, TokenAuthentication)) 
class CustomOutletRestSchema(AutoSchema):
    
    def get_link(self, path, method, base_url):
        link = super(CustomOutletRestSchema, self).get_link( path, method, base_url)
   
        path_field = [coreapi.Field(
                name=link.fields[0].name,
                required = True,
                location = 'path',
                schema = coreschema.Integer(description="Outlet number. Must be an integer"),
                ),]

        extra_fields = []
        
        if method=='PUT':
            extra_fields=[
                    coreapi.Field(
                        name='name',
                        required=False,
                        location='form',
                        type = coreschema.String,
                        schema=coreschema.String(
                        description="Change the outlet name in the position provided",
                        title="name"
                       )
                    ),
                    coreapi.Field(
                        name='status',
                        required=False,
                        location='form',
                        type = coreschema.String,
                        schema=coreschema.String(
                        description="Turn on or off the remote server connected to the outlet position provided. Values accepted: \'on\' or \'off\'",
                        title = 'status'
                       )
                    )
                ]
                
        campos = path_field + extra_fields
        
        newlink = coreapi.Link(
        url = link.url,
        action = link.action,
        description = link.description,
        encoding = 'application/json',
        fields = campos
        )
  
        return newlink
    
    
    