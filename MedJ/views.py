import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, MedicalDocumentForm
from .models import MedicalDocument
from .forms import OCRUploadForm
from ocrapi.vision_handler import extract_text_from_image, extract_medical_fields_from_text
from .models import BloodTestResult
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime

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
    extracted_data = None  # празно по начало
    if request.method == "POST" and request.FILES.get("document"):
        file = request.FILES["document"]

        # Временно запазване
        temp_path = os.path.join(settings.MEDIA_ROOT, "temp", file.name)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        with open(temp_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)


        extracted_text = extract_text_from_image(temp_path)


        extracted_data = extract_medical_fields_from_text(extracted_text)

        if extracted_data:
            BloodTestResult.objects.create(
                user=request.user,
                tsh=extracted_data.get("TSH"),
                glucose=extracted_data.get("Глюкоза"),
                t4=extracted_data.get("Т4"),
                hba1c=extracted_data.get("HbA1c"),
                date=datetime.strptime(extracted_data.get("Дата"), "%d.%m.%Y") if extracted_data.get("Дата") else None
            )

        # Премахване на временния файл
        os.remove(temp_path)

    return render(request, "upload.html", {"extracted": extracted_data})

@login_required
def upload_success(request):
    return render(request, "upload_success.html")

@csrf_exempt
def ocr_and_extract_view(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]

        # 1. Запазване временно
        temp_path = os.path.join(settings.MEDIA_ROOT, "temp", file.name)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        with open(temp_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)


        extracted_text = extract_text_from_image(temp_path)
        extracted_data = extract_medical_fields_from_text(extracted_text)

        if extracted_data:
            result = BloodTestResult.objects.create(
                user=request.user,
                tsh=extracted_data.get("TSH"),
                glucose=extracted_data.get("Глюкоза"),
                t4=extracted_data.get("Т4"),
                hba1c=extracted_data.get("HbA1c"),
                date=datetime.strptime(extracted_data.get("Дата"), "%d.%m.%Y") if extracted_data.get("Дата") else None
            )
            result.save()

        return JsonResponse({
            "extracted": extracted_data,
            "text": extracted_text
        })

    return JsonResponse({"error": "Файлът е задължителен."}, status=400)