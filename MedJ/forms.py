from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import MedicalDocument


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


class UploadForm(forms.Form):
    doc_kind = forms.ChoiceField(
        choices=[
            ("кръвни", _("Кръвни изследвания")),
            ("епикриза", _("Епикриза")),
            ("рецепта", _("Рецепта")),
        ],
        required=True,
        label=_("Вид документ"),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_doc_kind'
        })
    )
    file_type = forms.ChoiceField(
        choices=[
            ("image", _("Изображение")),
            ("pdf", _("PDF"))
        ],
        required=True,
        label=_("Тип файл"),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_file_type'
        })
    )
    file = forms.FileField(
        label=_("Файл"),
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'id_file'
        })
    )
