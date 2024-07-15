from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from django.conf.urls.static import static

from .views import *


router = DefaultRouter()
router.register(r'registeruser', Register, basename='register')
# router.register(r'assistantonly', AssistnantAppointment, basename='assistantonly')
router.register(r'appointment', DocAppointment, basename='appointment')
router.register(r'medrecord', PatientMedicalRecord, basename='medrecord')
router.register(r'prescription', DocPrescription, basename='prescription')
router.register(r'comments', CommentList, basename='comments')
router.register(r'viewappointment', OnlyDocAppointment, basename='viewappointment')



urlpatterns = [
    path('', include(router.urls)),
    # path('doctors/', DoctorCreateView.as_view(), name='doctor-create'),
    # path('comments/', CommentListCreateView.as_view(), name= 'assistantcreate' ),
    # path('userappointment/', DocAppointmentList.as_view(), name='userappointment'),
    path('report/', MedRecPdf.as_view(), name='report'),
    path('prescriptionreport/', PresciptionDownload.as_view(), name='prescriptionreport'),
    path('pdf', html_to_pdf, name = 'pdf'),
    path('prescription',presciptiondownload, name = 'prescription'),
    path('resetpassword/', new_password, name='resetpassword'),
    path('update/<int:pk>/', DocAppointmentUpdate.as_view({'get':'retrieve',
                                                           'patch':'partial_update'}), name= 'update')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
