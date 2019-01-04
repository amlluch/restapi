from rest_framework.permissions import BasePermission

class IsGet(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return False
    
class IsPost(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return False
    
class IsPut(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'PUT':
            return True
        return False
      
class IsDelete(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return True
        return False
