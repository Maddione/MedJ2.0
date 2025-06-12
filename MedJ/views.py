import os
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from ocrapi.vision_handler import extract_text_from_image
from MedJ.utils.parse_lab import parse_lab_report
from MedJ.utils.summary import generate_local_summary
from .anonymizer import anonymize_text
from .gpt_client import call_gpt_for_document
from .forms import CustomUserCreationForm, OCRUploadForm
from .models import MedicalDocument

def landing_page(request):
    return render(request, "landingpage.html")

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect("dashboard")
        return render(request, "registration/login.html", {"error": "Невалидно потребителско име или парола."})
    return render(request, "registration/login.html")

def logout_view(request):
    logout(request)
    return redirect("landingpage")

def register(request):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def casefiles(request):
    return render(request, "casefiles.html")

@login_required
def personalcard(request):
    return render(request, "personalcard.html")

@login_required
def upload(request):
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

        # parse & anonymize
        json_output = parse_lab_report(raw_text)
        anonymized = anonymize_text(raw_text)

        # call GPT or fallback summary
        try:
            gpt = call_gpt_for_document(anonymized, request.POST["doc_kind"], json_output)
            html_table = gpt["html_table"]
            summary   = gpt["summary"]
        except Exception:
            html_table = ""
            summary    = generate_local_summary(json_output)

        request.session["extracted_text"] = raw_text
        request.session["json_output"]    = json_output
        request.session["html_output"]    = html_table
        request.session["summary"]        = summary
        return redirect("upload")

    context = {
        "extracted_text": request.session.pop("extracted_text", None),
        "json_output":    request.session.pop("json_output", None),
        "html_output":    request.session.pop("html_output", None),
        "summary":        request.session.pop("summary", None),
    }
    return render(request, "upload.html", context)

@login_required
def history(request):
    docs = MedicalDocument.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "history.html", {"documents": docs})

@login_required
def profile(request):
    return render(request, "profile.html")

@login_required
def doctors(request):
    # Ако имаш модел Doctor:
    # docs = Doctor.objects.all()
    return render(request, "doctors.html", {"doctors": []})
