import os
import json
import hashlib
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _
from django.utils import timezone
from django.views.decorators.http import require_POST

from ocrapi.vision_handler import extract_text_from_image, extract_medical_fields_from_text
from ocrapi.gpt_client import call_gpt_for_document
from ocrapi.anonymizer import anonymize_text
from .forms import CustomUserCreationForm
from .models import MedicalEvent, MedicalDocument, Tag, BloodTestResult


# --- Публични изгледи ---
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
    return redirect('medj:landingpage')


# --- Изгледи за логнати потребители ---
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# VIEW 1 САМО ЗАРЕЖДА СТРАНИЦАТА С ФОРМАТА
@login_required
def upload_page(request):
    return render(request, 'upload.html')

# VIEW 2  ПРИЕМА ФАЙЛ И ВРЪЩА OCR ТЕКСТ
@login_required
@require_POST
def perform_ocr(request):
    temp_file_path = None
    try:
        uploaded_file = request.FILES.get('document')
        if not uploaded_file:
            return JsonResponse({'status': 'error', 'message': _('Файлът не беше получен.')}, status=400)

        file_content = uploaded_file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()

        if MedicalDocument.objects.filter(file_hash=file_hash, event__user=request.user).exists():
            return JsonResponse({
                'status': 'error',
                'message': _('Този документ вече е качен от Вас.')
            }, status=409)

        uploaded_file.seek(0)

        file_name = default_storage.save(f"temp/{uploaded_file.name}", uploaded_file)
        temp_file_path = default_storage.path(file_name)

        raw_text = extract_text_from_image(temp_file_path)
        if not raw_text:
            raise ValueError(_('Не беше разчетен текст от документа.'))

        return JsonResponse({
            'status': 'success',
            'ocr_text': raw_text,
            'file_hash': file_hash
        })

    except Exception as e:
        print(f"ERROR in perform_ocr: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    finally:
        if temp_file_path and default_storage.exists(temp_file_path):
            default_storage.delete(temp_file_path)


# VIEW 3 ПРИЕМА РЕДАКТИРАН ТЕКСТ, АНАЛИЗИРА И ЗАПИСВА В БАЗАТА
@login_required
@require_POST
def analyze_document(request):
    try:
        data = json.loads(request.body)
        edited_text = data.get('edited_text')
        category = data.get('category')
        specialist = data.get('specialist')
        file_hash = data.get('file_hash')

        if not all([edited_text, category, specialist, file_hash]):
            missing_fields = []
            if not edited_text:
                missing_fields.append('редактиран текст')
            if not category:
                missing_fields.append('категория')
            if not specialist:
                missing_fields.append('специалист')
            if not file_hash:
                missing_fields.append('хеш на файл')
            return JsonResponse({'status': 'error', 'message': _(f'Липсват необходими данни за анализ: {", ".join(missing_fields)}.')},
                                status=400)

        if MedicalDocument.objects.filter(file_hash=file_hash, event__user=request.user).exists():
            return JsonResponse({
                'status': 'error',
                'message': _('Този документ вече е записан в базата данни от Вас (повторна проверка).')
            }, status=409)

        anonymized_text = anonymize_text(edited_text)
        extracted_fields = extract_medical_fields_from_text(anonymized_text)
        gpt_result = call_gpt_for_document(anonymized_text, category, extracted_fields)

        # ЗАПИС В БАЗАТА ДАННИ
        try:
            event_date_str = gpt_result.get("json_data", {}).get("date")
            event_date = timezone.datetime.strptime(event_date_str, "%d-%m-%Y").date() if event_date_str else timezone.now().date()
        except (ValueError, TypeError):
            event_date = timezone.now().date()
            print("DEBUG: Невалиден формат на дата от GPT, използвана е текущата дата.")

        medical_event = MedicalEvent.objects.create(
            user=request.user,
            date=event_date,
            title=f"Анализ на документ ({_(category)}) от {event_date.strftime('%d.%m.%Y')}",
        )

        category_tag, created_cat = Tag.objects.get_or_create(name=category_name)
        specialist_tag, created_spec = Tag.objects.get_or_create(name=specialist_tag_name)

        medical_event.category = category_tag
        medical_event.save()

        medical_document = MedicalDocument.objects.create(
            event=medical_event,
            summary=gpt_result.get("summary", ""),
            file_hash=file_hash,
        )
        medical_document.tags.add(category_tag, specialist_tag)


        if category == "Кръвни изследвания" and "json_data" in gpt_result:
            for param_name, param_data in gpt_result["json_data"].items():
                if param_name != "date":
                    BloodTestResult.objects.create(
                        document=medical_document,
                        parameter=param_name,
                        value=param_data.get("value"),
                        unit=param_data.get("unit", ""),
                        reference_range=param_data.get("reference", ""),
                        status=param_data.get("status", ""),
                        measured_at=event_date
                    )
        # КРАЙ НА ЗАПИС В БАЗАТА ДАННИ

        return JsonResponse({
            'status': 'success',
            'summary': gpt_result.get("summary", _("Данните бяха обработени и запазени.")),
            'html_table': gpt_result.get("html_table", "")
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': _('Невалиден JSON формат на заявката.')}, status=400)
    except Exception as e:
        print(f"ERROR in analyze_document view: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Невалиден метод'}, status=405)


@login_required
def upload_history(request):
    user_documents = MedicalDocument.objects.filter(event__user=request.user).order_by('-uploaded_at')
    context = {
        'documents': user_documents
    }
    return render(request, 'history.html', context)


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