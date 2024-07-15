from rest_framework import permissions
from .models import *

# class IsOwnerOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         if request.method == 'GET':
#             return True
#         else:
#             if user.is_superuser:
#                 return True
#         return False



class IsAssistant(permissions.BasePermission):
    def has_permission(self, request, view):
        assistant = CustomUser.objects.filter(role = 'Assitant')
        if request.user in assistant:
            return True
        else:
            if request.method == 'GET':
                return True
        return False    
       

class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        doctor = CustomUser.objects.filter(role = 'Doctor')
        if request.user in doctor:
            return True
        else:
            if request.method == 'GET':
                return True            
        return False


class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        patient = CustomUser.objects.filter(role = 'Patient')
        if request.user in patient:
            return True
        else:
            if request.method == 'GET':
                return True
        return True

class RegisterViewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == 'GET':
            return CustomUser.objects.filter(username=  request.user.username)
        
        if not request.user.is_authenticated and request.method == 'POST':
            return True
        return False

class CommentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        patient = CustomUser.objects.filter(role = 'Patient')
        assistant = CustomUser.objects.filter(role = 'Assitant')
        doctor = CustomUser.objects.filter(role = 'Doctor')

        if request.user in patient:
            if request.method == "POST":
                return True
        if request.user in assistant or not request.user.is_authenticated:
            if request.method == "GET":
                return True
            return False
        if request.user in doctor:
            return False
        return True
    
    # def has_object_permission(self, request, view, obj):
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
        
    #     return obj.user == request.user
    


