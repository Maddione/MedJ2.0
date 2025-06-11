# MedJ/views.py

import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from ocrapi.vision_handler import extract_text_from_image
from MedJ.utils.parse_lab import parse_lab_report
from MedJ.utils.summary import generate_local_summary
from .anonymizer import anonymize_text
from .gpt_client import call_gpt_for_document
from django.contrib.auth import authenticate, login, logout

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
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    return render(request, "dashboard.html")
@login_required
def upload(request):
    #---- POST обработка ----#
    if request.method == "POST" and request.FILES.get("document"):
        file = request.FILES["document"]
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.name)
        with open(temp_path, "wb+") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        raw_text = extract_text_from_image(temp_path)
        os.remove(temp_path)

        json_output = parse_lab_report(raw_text)
        anonymized = anonymize_text(raw_text)

        try:
            gpt = call_gpt_for_document(anonymized, request.POST.get("doc_kind"), json_output)
            html_output = gpt["html_table"]
            summary = gpt["summary"]
        except:
            html_output = ""
            summary = generate_local_summary(json_output)

        # Записваме в сесия
        request.session["extracted_text"] = raw_text
        request.session["json_output"]    = json_output
        request.session["html_output"]    = html_output
        request.session["summary"]        = summary

        return redirect("upload")

    #---- GET рендер ----#
    extracted_text = request.session.pop("extracted_text", None)
    json_output    = request.session.pop("json_output", None)
    html_output    = request.session.pop("html_output", None)
    summary        = request.session.pop("summary", None)

    return render(request, "upload.html", {
        "extracted_text": extracted_text,
        "json_output": json_output,
        "html_output": html_output,
        "summary": summary,
        "doc_kind": request.POST.get("doc_kind"),
        "file_type": request.POST.get("file_type"),
    })
