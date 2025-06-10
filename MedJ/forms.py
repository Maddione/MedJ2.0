from django import forms
from .models import MedicalDocument
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class MedicalDocumentForm(forms.ModelForm):
    class Meta:
        model = MedicalDocument
        fields = ['event', 'file', 'tags']
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),

        }
class OCRUploadForm(forms.Form):
    file = forms.FileField(label="Качи изображение или PDF")