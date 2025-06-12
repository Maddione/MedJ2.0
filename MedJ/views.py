import os
import io
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from ocrapi.vision_handler import extract_text_from_image
from .utils.parse_lab import parse_lab_report
from .forms import CustomUserCreationForm


def landing_page(request):
    return render(request, 'landingpage.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('medj:dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('medj:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('medj:landingpage')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def upload(request):
    json_output = None
    html_output = None
    if request.method == 'POST' and request.FILES.get('document'):
        file = request.FILES['document']
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.name)
        with open(temp_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)
        # raw_text = extract_text_from_image(temp_path)
        os.remove(temp_path)
        # json_output, html_output = parse_lab_report(raw_text)
    return render(request, 'upload.html', {'json_output': json_output, 'html_output': html_output})


@login_required
def upload_history(request):
    return render(request, 'history.html')


@login_required
def casefiles(request):
    return render(request, 'casefiles.html')


@login_required
def personalcard(request):
    return render(request, 'personalcard.html')


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def doctors(request):
    return render(request, 'doctors.html')