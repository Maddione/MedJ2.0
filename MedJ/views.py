import os
import re
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import CustomUserCreationForm, MedicalDocumentForm, OCRUploadForm
from .models import BloodTestResult, MedicalDocument
from ocrapi.vision_handler import extract_medical_fields_from_text, extract_text_from_image


def landing_page(request):
    return render(request, "landingpage.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "registration/login.html", {"error": "Невалидно потребителско име или парола."})
    return render(request, "registration/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("login")
        else:
            return render(request, "registration/register.html", {"form": form})
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})

def ocr_upload_view(request):
    extracted_text = None

    if request.method == 'POST':
        form = OCRUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            file_path = f'media/temp_{uploaded_file.name}'

            with open(file_path, 'wb+') as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)

            extracted_text = extract_text_from_image(file_path)
            os.remove(file_path)
    else:
        form = OCRUploadForm()

    return render(request, 'upload.html', {'form': form, 'extracted_text': extracted_text})

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def upload(request):
    extracted_text = None
    extracted_fields = None

    doc_kind = request.POST.get("doc_kind")
    file_type = request.POST.get("file_type")

    if request.method == "POST" and request.FILES.get("document"):
        file = request.FILES["document"]

        temp_path = os.path.join(settings.MEDIA_ROOT, "temp", file.name)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        with open(temp_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        extracted_text = extract_text_from_image(temp_path)
        extracted_fields = extract_medical_fields_from_text(extracted_text)

        os.remove(temp_path)

    return render(request, "upload.html", {
        "extracted_text": extracted_text,
        "extracted_fields": extracted_fields,
        "doc_kind": doc_kind,
        "file_type": file_type,
    })

@login_required
def upload_success(request):
    return render(request, "upload_success.html")

@csrf_exempt
def ocr_and_extract_view(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]

        temp_path = os.path.join(settings.MEDIA_ROOT, "temp", file.name)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        with open(temp_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        raw_text = extract_text_from_image(temp_path)
        anonymized_text = anonymize_text(raw_text)
        extracted_data = extract_medical_fields_from_text(extracted_text)

        os.remove(temp_path)

        return JsonResponse({
            "extracted": extracted_data,
            "text": extracted_text
        })

    return JsonResponse({"error": "Файлът е задължителен."}, status=400)

def anonymize_text(text):

    text = re.sub(r'\b[A-ZА-Я][a-zа-я]+\b', '[NAME]', text)
    text = re.sub(r'\b\d{10}\b', '[ID]', text)
    text = re.sub(r'\+?\d{2,4}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3}[\s\-]?\d{3,4}', '[PHONE]', text)
    text = re.sub(r'\b\S+@\S+\.\S+\b', '[EMAIL]', text)
    text = re.sub(r'\b(ул\.|бул\.|ж\.к\.)\s+[^\n,]+', '[ADDRESS]', text)

    return text

