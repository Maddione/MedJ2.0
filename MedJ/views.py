# views.py

import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _
from ocrapi.vision_handler import extract_text_from_image, extract_medical_fields_from_text
from ocrapi.gpt_client import call_gpt_for_document
from .forms import CustomUserCreationForm


# --- Публични изгледи (без промяна) ---
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


# --- Изгледи за логнати потребители ---

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def upload(request):
    """
    Основна функция за качване и обработка на документи.
    - При GET заявка: показва празната форма.
    - При POST заявка (от AJAX): обработва файла и връща JSON.
    """
    # Сценарий 1: Потребителят отваря страницата, показваме HTML
    if request.method == 'GET':
        return render(request, 'upload.html')

    # Сценарий 2: Потребителят изпраща файл, обработваме и връщаме JSON
    if request.method == 'POST':
        temp_file_path = None
        try:
            uploaded_file = request.FILES.get('document')
            doc_kind = request.POST.get('doc_kind')

            if not uploaded_file or not doc_kind:
                return JsonResponse({'status': 'error', 'message': _('Моля, изберете файл и вид документ.')},
                                    status=400)

            # 1. Запазваме файла временно, за да получим пътя до него
            file_name = default_storage.save(f"temp/{uploaded_file.name}", uploaded_file)
            temp_file_path = default_storage.path(file_name)

            # 2. Извикваме OCR функцията от vision_handler.py
            raw_text = extract_text_from_image(temp_file_path)
            if not raw_text:
                raise ValueError(_('Не беше разчетен текст от документа.'))

            # 3. Извикваме Regex функцията (по желание, за fallback)
            extracted_fields = extract_medical_fields_from_text(raw_text)

            # 4. Извикваме GPT функцията от gpt_client.py
            gpt_result = call_gpt_for_document(raw_text, doc_kind, extracted_fields)

            # 5. (По желание) Запазваме резултата в базата данни
            # Document.objects.create(...)

            # 6. Връщаме успешен JSON отговор към JavaScript
            return JsonResponse({
                'status': 'success',
                'summary': gpt_result.get("summary", _("Няма налично обобщение.")),
                'html_table': gpt_result.get("html_table", "")
            })

        except Exception as e:
            # Прихваща всяка грешка и я връща като JSON
            print(f"ERROR in upload view: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        finally:
            # 7. Винаги изтриваме временния файл накрая
            if temp_file_path and default_storage.exists(temp_file_path):
                default_storage.delete(temp_file_path)

    # Ако заявката не е нито GET, нито POST
    return JsonResponse({'status': 'error', 'message': 'Невалиден метод'}, status=405)


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