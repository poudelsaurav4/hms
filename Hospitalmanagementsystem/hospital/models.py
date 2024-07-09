from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError


# Create your models here.
# def username_validators(value):
#     if not "@"in value:
        # return ValidationError("username must have @ in it")
class CustomUser(AbstractUser):
    # username = models.CharField(max_length=50, validators=username_validators)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'other'),
    )
    ROLES_CHOICES = {
        ('Doctor', 'Doctor'),
        ('Patient', 'Patient'),
        ('Assitant', 'Assistant'),
    }
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    role = models.CharField(max_length=50,choices=ROLES_CHOICES, default='Patient')
    address = models.CharField(max_length=255)
    groups = models.ManyToManyField(Group, default="", blank=True)
    contact_number = models.CharField(max_length=20)
    profile_pic = models.ImageField(upload_to='media/', blank=True)
    
        
    @property
    def is_doctor(self):
        return self.role == 'Doctor'

    @property
    def is_patient(self):
        return self.role == 'Patient'
    
    def __str__(self) -> str:
        return self.username

class Doctor(models.Model):
    DOC_AVAILABLE = (
        ('is_available', 'is_available'),
        ('not_available', 'not_available'),
        ('sun-fri', 'sun-fri'),
        ('wed-thurs', 'wed-thrus'),
        ('sat', 'sat')
    )

    SPECIALITY = (
        ('Cardiologist', 'Cardiologist'),
        ('Physist', 'Physist'),
        ('ENT','ENT'),
        ('Surgen','Surgen')
    )
    user = models.OneToOneField(CustomUser, related_name='doc',on_delete=models.CASCADE)
    speciality = models.CharField(max_length=100, choices=SPECIALITY)
    availability = models.CharField(max_length=50,choices=DOC_AVAILABLE)


    def __str__(self):
        return self.user.username

# class Patient(models.Model):
#     user = models.OneToOneField(CustomUser, related_name='pat', on_delete=models.CASCADE)
#     medicalhistory = models.TextField()
#     def __str__(self):
#         return self.user.username

# class Assistant(models.Model):
#     user = models.OneToOneField(CustomUser, related_name='assistant', on_delete= models.CASCADE)


class Appointment(models.Model):
    APPOINTMENT_CHOICES = (
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    appointment_date=models.DateField()
    appointment_time=models.TimeField()
    whatfor = models.TextField(max_length=255, blank=True, null=True)
    status=models.CharField(max_length=50,choices=APPOINTMENT_CHOICES)
    doctor=models.ForeignKey(CustomUser,related_name='doctor_appointments', on_delete=models.CASCADE)
    patient = models.ForeignKey(CustomUser, related_name='patient_appointments',on_delete=models.CASCADE)

    def __str__(self):
        return self.doctor.username
    
class MedicalRecord(models.Model):
    patient = models.ForeignKey(CustomUser, related_name='medical_records_patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey(CustomUser, related_name='medical_records_doctor', on_delete=models.CASCADE)
    diagnosis = models.TextField()
    treatment = models.TextField()
    test_results = models.TextField(blank=True, null=True)
    progress_notes = models.TextField(blank=True, null=True)
    date_created = models.DateField(auto_now_add=False)
    report_img = models.ImageField(upload_to='media/', blank=True)
    
class Prescription(models.Model):
    patient = models.ForeignKey(CustomUser, related_name='prescription_for', on_delete=models.CASCADE)
    doctor = models.ForeignKey(CustomUser, related_name='prescribed_by', on_delete=models.CASCADE)
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    instructions = models.TextField(blank=True, null=True)

class Comments(models.Model):
    doctor = models.ForeignKey(CustomUser, related_name='Doctor_comment', on_delete=models.CASCADE)
    comment = models.TextField(null=True)
    created_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_on','comment')
