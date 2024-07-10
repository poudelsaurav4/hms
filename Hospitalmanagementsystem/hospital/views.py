import os
from django.shortcuts import render, redirect
from rest_framework import viewsets, mixins,generics
from .models import *
from .serializers import *
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib import messages 
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from xhtml2pdf import pisa
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from .router import ConditionalRouter
from rest_framework.decorators import api_view, permission_classes

# from custom_renderer import JPEGRenderer, PNGRenderer
# Create your views here.
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
    



class Register(viewsets.ModelViewSet):
    # queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    # permission_classes = [IsAssistant]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CustomUser.objects.none()
            
        else:
            if user.role == 'Assitant':
                return CustomUser.objects.all()
        

        return CustomUser.objects.filter(username=user.username)
    def get_serializer_context(self):

        context = super().get_serializer_context()
        # import ipdb; ipdb.set_trace()

        if not self.request.user.is_authenticated:
            context['welcome'] = "Hello, welcome to our API!"
        return context


class DocAppointment(viewsets.ModelViewSet):
    queryset= Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsPatient | IsDoctor, IsAuthenticated]
    # authentication_classes = [BasicAuthentication,SessionAuthentication]

    def get_queryset(self):

        status_check = Appointment.objects.filter(status = 'completed')
        user = self.request.user
        # if status_check:
        #     return Appointment.objects.exclude(status= 'completed')
        if user.role == 'Assitant':
            return Appointment.objects.all()
        return Appointment.objects.filter(Q(patient = self.request.user) | Q(doctor = self.request.user)).exclude(status= 'Completed')


class PatientMedicalRecord(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsDoctor,IsAuthenticated]
    # authentication_classes = [BasicAuthentication, SessionAuthentication]


    # def get_serializer_context(self):
    #     context=  super(PatientMedicalRecord).get_serializer_context()
    #     context.update({
    #         'doctor': CustomUser.objects.get(role = "doctor").username
    #     })
        # return context
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'Assitant':
            return MedicalRecord.objects.all()
        return MedicalRecord.objects.filter(Q(patient = self.request.user) | Q(doctor = self.request.user))
    

class DocPrescription(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctor, IsAuthenticated]
    # authentication_classes = [BasicAuthentication, SessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Assitant':
            return Prescription.objects.all()
        return Prescription.objects.filter(Q(patient = self.request.user) | Q(doctor = self.request.user))


class OnlyDocAppointment(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    http_method_names = ['get']

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CustomUser.objects.none()
        if self.request.user.role == 'Doctor':
            return Appointment.objects.filter(doctor = self.request.user).exclude(status= 'Completed')

        
        

class CommentList(viewsets.ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer
    permission_classes= [CommentPermission]
    http_method_names = ['get', 'post']


def new_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')
        username = request.POST.get('username')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'newpassword.html', {'username': username})
        
        elif len(new_password) < 8 or new_password.isdigit():
            messages.error(request, "Password should not be less than 8 digits and password shouldnot contain only words")
            return render(request, 'newpassword.html', {'username': username})
        
        else:
            if CustomUser.objects.filter(username=username).exists():
                user = CustomUser.objects.get(username=username)
                user.password = make_password(new_password)
                user.save()
                messages.success(request, "Password has been reset successfully")
                return redirect('/api-auth/login/?next=/')
            else:
                messages.error(request, "Invalid username")
                return render(request, 'newpassword.html', {username:username})

    return render(request, 'newpassword.html')


from django.template.loader import render_to_string

class MedRecPdf(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'report.html'
    
    def get(self, request):
        queryset = MedicalRecord.objects.filter(patient = self.request.user)
        return Response({'records': queryset})
    
class PresciptionDownload(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'presciption.html'
    
    def get(self, request):
        queryset = Prescription.objects.filter(patient = self.request.user)
        return Response({'records': queryset})
    

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_media/

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri

    # Make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def html_to_pdf(request):
    queryset = MedicalRecord.objects.filter(patient=request.user)
    template_name = 'report.html'
    html = render_to_string(template_name, {
        'records': queryset,
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    if pisa_status.err:
        return HttpResponse(f'We had some errors <pre>{html}</pre>')

    return response

def presciptiondownload(request):
    queryset = Prescription.objects.filter(patient=request.user)
    template_name = 'presciption.html'
    html = render_to_string(template_name, {
        'records': queryset,
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    if pisa_status.err:
        return HttpResponse(f'We had some errors <pre>{html}</pre>')

    return response