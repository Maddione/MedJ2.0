from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, MedicalDocumentForm
from .models import MedicalDocument

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
            login(request, user)  # автоматично логване след регистрация
            return redirect("dashboard")
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def upload(request):
    if request.method == "POST":
        form = MedicalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()
            form.save_m2m()
            return redirect("upload_success")
    else:
        form = MedicalDocumentForm()
    return render(request, "upload.html", {"form": form})

@login_required
def upload_success(request):
    return render(request, "upload_success.html")
