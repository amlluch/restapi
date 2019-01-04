# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication

from pdudbapp.models import Users as Userpdu
from pdudbapp.models import Idata
from documentation import CustomUserRestSchema, CustomAdminRestSchema, CustomOutletRestSchema
from restapi.serializers import UserSerializer, ModifyUser, OutletSerializer, EntryPoint, TokenSerializer, GetOutletSerializer
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from permissions import IsGet, IsPost, IsPut, IsDelete
from rest_condition import ConditionalPermission, C, And, Or, Not


from rest_framework.generics import GenericAPIView

from django.contrib.auth.views import logout

from django.http import HttpResponseRedirect

# Create your views here.


# El orden importa para que se desloguee correctamente
@authentication_classes(( SessionAuthentication, BasicAuthentication, TokenAuthentication))
class usersRest(APIView):
    
    schema = CustomUserRestSchema()
    permission_classes = [Or(And(IsGet, IsAuthenticated),   #Any authenticated user
                             And(IsPut, IsAuthenticated),   #Any authenticated user
                             And(IsDelete, IsAdminUser))]   #Only Admin can delete
    serializer_class = ModifyUser

    def get(self, request, usr=None, format=None):
        
        """
        
        It shows a user with its features (no password shown)
        """
        if (request.user.username!=usr and not(request.user.is_superuser)):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            usuarios = Userpdu.objects.using('pdudb').get(user=usr)
            serializers = UserSerializer(usuarios)
        except:
            return Response('User dosen\'t exist', status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def put(self, request, usr=None, format=None):
        """
        Change user paswword, outlet name, status or remove user from outlet position.
        For changing outlet name or outlet status (on or off) or for removing a user from outlet position 
        is mandatory a position.
        """
        try:
            usuario = Userpdu.objects.using('pdudb').get(user=usr)
            try: 
                user = User.objects.get(username=usr)
            except:
                user = User(username=usr)
                user.set_password = usuario.password
                user.email = usuario.email
                user.save()
        except:
            content = {'Please move along': 'User ' + usr + ' doesn\'t exist'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        if (request.user.username!=usr and not(request.user.is_superuser)):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        context = {'request':request}

        serializer = self.serializer_class(user, data=request.data, context=context)
        if serializer.is_valid():

            dato = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    def delete(self, request, usr=None, format=None):
        """
        Delete user. Only for admins.
        
        """
        try:
            usuario = Userpdu.objects.using('pdudb').get(user=usr)
            try:
                user = User.objects.get(username=usr.strip())
            except:
                user = User(username=usr)
                user.set_password(usuario.password)
                user.save()
            User.objects.filter(username = usr).delete()
            return Response('User deleted', status=status.HTTP_200_OK)
            
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)



@authentication_classes(( SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAdminUser,))
class adminRest(APIView):
    schema = CustomAdminRestSchema()
    serializer_class = ModifyUser
    def get(self, request, format=None):
        """
        Complete list of users and its features.
        """
        usuarios = Userpdu.objects.using('pdudb').all()
        serializer = UserSerializer(usuarios, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request, format=None):
        """
        It creates a new user.
        """

        context = { 'request':request}
        serializer = ModifyUser(data=request.data, context = context)
        if serializer.is_valid():
            
            try:
                usuario = Userpdu.objects.using('pdudb').get(user=request.data['username'])
                content = {'Please move along': 'User ' + request.data['username'] + ' already exists'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            except:
                datos = serializer.validated_data
                dato = serializer.save()
                return Response('User created', status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes(( SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAdminUser,))
class outletsRest(APIView):

    def get(self, request, format=None):
        """
        
        Complete list of outlets and its features. No parameters required. For admins only.
        """
        outlets = Idata.objects.using('pdudb').all()
        serializer = GetOutletSerializer(outlets, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
    
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAdminUser,))    
class outletRest(APIView):
    schema = CustomOutletRestSchema()
    serializer_class = OutletSerializer
    def get(self, request, position=None, format=None):
        
        """
        Outlet features. For admins only. Use user rest for changing data related to users.
        """
        context = {'request':request}
        try:
            outlet = Idata.objects.using('pdudb').get(posicion=position)
            serializer = GetOutletSerializer(outlet, context=context)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, position=None, format=None):
        
        """
        Outlet features. For admins only. Use user rest for changing data related to users.
        """
        context = {'request':request}
        try:
            outlet = Idata.objects.using('pdudb').get(posicion=position)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializers = self.serializer_class(outlet, data=request.data, context = context)
        if serializers.is_valid():
            dato = serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication)) 
class restEntryPoint(GenericAPIView):
    """
    Restful API Entry point. 
    
    Login for options
    """

    def get(self, request):
        data = {'message': 'Welcome to Restful API',}
        serializer = EntryPoint(instance=data)
        return Response(serializer.data)

@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication)) 
@permission_classes((IsAuthenticated,))    
class logOutView(APIView):
    """
    Renew auth Token and logout
    """
    def get(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except:
            pass
    
        logout(request)
        return HttpResponseRedirect(redirect_to='/pdu/restapi')


@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication)) 
@permission_classes((IsAuthenticated,)) 
class getToken(APIView):
    """
    View actual Token. Add header for auth:\n
    
    -H "Authorization: Token ------- YOUR TOKEN HERE ---------"
    """
    def get(self, request):
        tk, _ = Token.objects.get_or_create(user=request.user)
        serializer = TokenSerializer(instance = tk)
        return Response(serializer.data)

