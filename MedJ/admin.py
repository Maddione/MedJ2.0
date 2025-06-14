from django.contrib import admin

from .models import (
    Tag,
    Doctor,
    PatientProfile,
    MedicalEvent,
    MedicalDocument,
    BloodTestResult,
    UpcomingAppointment,
    Prescription
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'phone']
    search_fields = ['name', 'specialty']


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'gender', 'blood_group', 'personal_doctor']
    search_fields = ['user__username', 'blood_group']


@admin.register(MedicalEvent)
class MedicalEventAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'date', 'category', 'doctor']
    list_filter = ['category', 'date']
    search_fields = ['title', 'description']


@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ['event', 'uploaded_at']
    search_fields = ['extracted_text', 'summary']
    filter_horizontal = ['tags']


@admin.register(BloodTestResult)
class BloodTestResultAdmin(admin.ModelAdmin):
    list_display = ['parameter', 'value', 'unit', 'measured_at']
    list_filter = ['measured_at']
    search_fields = ['parameter']


@admin.register(UpcomingAppointment)
class UpcomingAppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'doctor', 'date']
    search_fields = ['doctor__name', 'user__username']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'medicine_name', 'dose', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['medicine_name']
