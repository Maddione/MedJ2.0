from __future__ import annotations
import re
import json
import os
import openai
from django.conf import settings
from openai import OpenAI
from django.utils.translation import gettext as _
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def call_gpt_for_document(raw_text: str, doc_kind: str, extracted_fields: dict) -> dict:
    """
    Calls OpenAI GPT with a specific prompt and safely parses the response.
    """
    prompt = (
        f"Ти си експертен медицински асистент. Анализирай следния текст от медицински документ, който е тип '{doc_kind}'.\n"
        f"Извлечен текст:\n\"\"\"{raw_text}\"\"\"\n\n"
        "Моля направи следното:\n"
        "1) Върни JSON обект с ключове и стойности. Дата да е низ в DD-MM-YYYY формат.\n"
        "2) Върни HTML таблица със заглавия на български: Показател, Стойност, Ед., Статус, Реф. граници.\n"
        "3) Върни анализен параграф, който за всеки показател извън референтните граници указва дали е повишен или понижен.\n"
        "Форматирай отговора стриктно така, с разделители:\n"
        "===JSON===\n"
        "{\n"
        '  "date": "11-06-2025",\n'
        '  "TSH": {"value": 5.1, "unit": "mU/l", "status": "high", "reference": "0.4-4.2"}\n'
        "}\n"
        "===HTML===\n"
        "<table class='table table-bordered'>...</table>\n"
        "===SUMMARY===\n"
        "Параграф с анализ на резултатите.\n"
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            max_tokens=3500
        )
        gpt_answer = response.choices[0].message.content

        content = resp.choices[0].message.content if resp.choices else ""

    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        content = ""

    # ----  PRINT ЗА ДЕБЪГВАНЕ ----
    print("----------- СУРОВ ОТГОВОР ОТ GPT -----------")
    print(content)
    print("------------------------------------------")
    # ---------------------------------------------

    # --- ПАРСВАНЕ с REGEX ---
    json_match = re.search(r"===JSON===(.*?)===HTML===", content, re.DOTALL)
    html_match = re.search(r"===HTML===(.*?)===SUMMARY===", content, re.DOTALL)
    summary_match = re.search(r"===SUMMARY===(.*)", content, re.DOTALL)


    json_part = json_match.group(1).strip() if json_match else "{}"
    html_part = html_match.group(1).strip() if html_match else ""
    summary_part = summary_match.group(1).strip() if summary_match else _("Не може да се генерира обобщение.")

    try:
        json_data = json.loads(json_part)
    except json.JSONDecodeError:
        json_data = extracted_fields
        html_part = f"<p>{_('GPT върна невалиден формат на данните.')}</p>"

    return {"json_data": json_data, "html_table": html_part, "summary": summary_part}
