import json
import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def call_gpt_for_document(raw_text: str, doc_kind: str, extracted_fields: dict) -> dict:
    prompt = (
        f"Документ тип: {doc_kind}.\n"
        f"Извлечен текст:\n\"\"\"{raw_text}\"\"\"\n"
        "Моля:\n"
        "1) JSON с ключове и стойности.\n"
        "   - Дата да е низ в DD-MM-YYYY формат.\n"
        "2) HTML таблица (<table>…</table>).\n"
        "3) Кратко обобщение.\n"
        "Форматирай отговора с маркери:\n"
        "===JSON===\n"
        "{\n"
        '  "date": "11-06-2025",\n'
        '  "TSH": 4.2\n'
        "}\n"
        "===HTML===\n"
        "<table>…</table>\n"
        "===SUMMARY===\n"
        "…"
    )
    try:
        client = openai.OpenAI()
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=700
        )
        content = resp.choices[0].message.content
        json_part = content.split("===JSON===")[1].split("===HTML===")[0].strip()
        html_part = content.split("===HTML===")[1].split("===SUMMARY===")[0].strip()
        summary_part = content.split("===SUMMARY===")[1].strip()
        json_data = json.loads(json_part)
    except Exception:
        json_data = extracted_fields
        html_part = ""
        summary_part = "Неуспешно генериране – показани са само OCR-данните."
    return {
        "json_data": json_data,
        "html_table": html_part,
        "summary": summary_part
    }
