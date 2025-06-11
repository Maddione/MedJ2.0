import os
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from ocrapi.vision_handler import extract_text_from_image
from MedJ.utils.parse_lab import parse_lab_report
from .anonymizer import anonymize_text
from .gpt_client import call_gpt_for_document
from .forms import CustomUserCreationForm, OCRUploadForm

def landing_page(request):
    return render(request, "landingpage.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        return render(request, "login.html", {"error": "Невалидно потребителско име или парола."})
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def upload(request):
    json_output = None
    html_output = None
    summary = None

    if request.method == "POST" and request.FILES.get("document"):
        file = request.FILES["document"]
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.name)
        with open(temp_path, "wb+") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        raw_text = extract_text_from_image(temp_path)
        print("OCR raw text:", raw_text)
        os.remove(temp_path)

        json_output = parse_lab_report(raw_text)

        anonymized_text = anonymize_text(raw_text)
        gpt_results = call_gpt_for_document(
            anonymized_text,
            request.POST.get("doc_kind"),
            json_output
        )
        html_output = gpt_results["html_table"]
        summary = gpt_results["summary"]

    return render(request, "upload.html", {
        "json_output": json_output,
        "html_output": html_output,
        "summary": summary,
        "doc_kind": request.POST.get("doc_kind"),
        "file_type": request.POST.get("file_type"),
    })

@csrf_exempt
def ocr_and_extract_view(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.name)
        with open(temp_path, "wb+") as dest:
            for chunk in file.chunks():
                dest.write(chunk)
        raw_text = extract_text_from_image(temp_path)
        anonymized_text = anonymize_text(raw_text)
        extracted_data = parse_lab_report(raw_text)
        os.remove(temp_path)
        return JsonResponse({"extracted": extracted_data, "text": anonymized_text})
    return JsonResponse({"error": "Файлът е задължителен."}, status=400)
