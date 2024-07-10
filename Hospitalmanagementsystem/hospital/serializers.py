import datetime 
from rest_framework import serializers
from hospital.models import *
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils import timezone

import re

    
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username','first_name','last_name', 'password','email','address','gender','role', 'profile_pic']

    def validate(self, data):
        
        if data['username'] == data['first_name']:
            raise serializers.ValidationError({'username':'username cannnot be same as firstname'})
        return data
    
    def validate_first_name(self, first_name):
        if re.search(r'[ !@#$%^&*()_+=\[{\]};:<>|./?\\\-]', first_name):
            raise serializers.ValidationError("Firstname cannot contain special characters like @, #, _, -")
        return first_name
    
    def validate_last_name(self, last_name):
        if re.search(r'[ !@#$%^&*()_+=\[{\]};:<>|./?\\\-]', last_name):
            raise serializers.ValidationError("Firstname cannot contain special characters like @, #, _, -")
        return last_name
        
    # def validate_email(self, email):
    #     pattern = r'^(gmail|hotmail|yahoo)\.(com|org|edu|[a-z]{2})$'
    #     if not re.match(pattern, email):
    #         raise serializers.ValidationError("Invalid email format or domain suffix.")
    #     return email
    
    def validate_password(self, password):
        if len(password)<=8 and password.isdigit():
            raise serializers.ValidationError('Your password should contain letters!')
        if not re.search(r'[a-zA-Z0-9]', password):
            raise serializers.ValidationError('Your password should contain at least one non-alphanumeric character!')

        return password  
   
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        user = CustomUser.objects.create(**validated_data)
        
        return user
    
# class AssistantSerializer(serializers.ModelSerializer):
    # user = RegisterSerializer()

    # class Meta:
    #     model = Assistant
    #     fields = ['id', 'user']

    


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role = 'Doctor'))
    patient = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role ='Patient'))
    # doctor_name = serializers.CharField(source = 'doctor.first_name')

    # doctor = serializers.SerializerMethodField()
    # patient = serializers.SerializerMethodField()
    class Meta:
        model = Appointment
        fields = ['id','appointment_date','appointment_time','whatfor' ,'status', 'doctor','patient']
        # unique_together = ('appointment_date','appointment_time','doctor','patient')
        
    def validate(self, data):
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        patient = data.get('patient')
        doctor = data.get('doctor')


        existing_appointment = Appointment.objects.filter(appointment_date=appointment_date,appointment_time=appointment_time,doctor=doctor).exists()
        existing_appointment_date = Appointment.objects.filter(appointment_date=appointment_date,patient= patient)


        if existing_appointment_date:
            raise serializers.ValidationError({'appointment_date':'appointment already exist at this date'})
        

        if existing_appointment:
            raise serializers.ValidationError({'appointment_time':'appointment already exist at this time'})
        
        
        if appointment_date < datetime.date.today():
            raise serializers.ValidationError({'appointment_date':"Appointment date should be date from tommorow"})
        
        #  raise serializers.ValidationError({'appointment_time':"Current time cannot be selected"})

        if not (appointment_time.hour >= 6 and appointment_time.hour < 18):  
            raise serializers.ValidationError({'appointment_time':"Appointments can only be scheduled between 6 am and 6 pm."})


        return data
    
    def get_fields(self):
        fields = super().get_fields()
        request = self.context['request']
        if request.method =='GET':
            doctor_serializer = RegisterSerializer()
            patient_serializer = RegisterSerializer()
            doctor_serializer.fields = {'first_name': doctor_serializer.fields['first_name']}
            patient_serializer.fields = {'first_name':patient_serializer.fields['first_name']}
            fields['doctor'] = doctor_serializer
            fields['patient'] = patient_serializer
        return fields


    # def to_representation(self, instance):
    #     rep = super(AppointmentSerializer, self).to_representation(instance)
    #     rep['doctor'] = instance.doctor.username
    #     rep['patient'] = instance.patient.username
    #     return rep

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id','patient','doctor','diagnosis','treatment','test_results','report_img','progress_notes','date_created']
    doctor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role = 'Doctor'))
    patient = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role ='Patient'))
    

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id','patient','doctor','medication', 'dosage','duration','instructions']
        
    doctor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role = 'Doctor'))
    patient = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role ='Patient'))
    


def validate_comment(value):
    if ''in value:
        return ValidationError("enter atleast a word")

class CommentSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(validators = [validate_comment])
    name = serializers.SerializerMethodField()
    doctor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role = 'Doctor'),source = 'doctor.first_name')
    class Meta:
        
        model = Comments
        fields = ['id','name','doctor','comment','created_on']
    

    def get_name(self, obj):
        return 'anynomus'
   
    # def get_doctor(self,obj):
    #     if obj.doctor:
    #         return obj.Doctor.first_name


        
class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'username']
        model = CustomUser

    
    def validate_username(self, value):
        if not CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username does not exist")
        return value    
    
class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def save(self):
        username = self.validate['username']
        new_password = self.validated_data['password1']
        user = CustomUser.objects.get(username=username)
        user.password = make_password(new_password)
        user.save()
        
