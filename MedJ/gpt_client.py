import json
import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY


def _build_html_table(data: dict) -> str:
    """Return an HTML table generated from extracted OCR data."""
    if not data:
        return ""

    rows = []
    for name, info in data.items():
        if name == "date":
            continue
        rows.append(
            "<tr>"
            f"<td>{name}</td>"
            f"<td>{info.get('value')}</td>"
            f"<td>{info.get('unit')}</td>"
            f"<td>{info.get('status', '')}</td>"
            f"<td>{info.get('reference')}</td>"
            "</tr>"
        )

    header = (
        "<table class='table table-bordered'>"
        "<thead><tr>"
        "<th>Показател</th><th>Стойност</th><th>Ед.</th>"
        "<th>Статус</th><th>Реф. граници</th>"
        "</tr></thead><tbody>"
    )
    return header + "".join(rows) + "</tbody></table>"


def call_gpt_for_document(raw_text: str, doc_kind: str, extracted_fields: dict) -> dict:
    """Generate a short summary in Bulgarian using OpenAI."""
    summary_prompt = (
        f"Документ тип: {doc_kind}.\n"
        f"Извлечен текст:\n\"\"\"{raw_text}\"\"\"\n"
        "Дай кратко обобщение на български език."
    )

    try:
        client = openai.OpenAI()
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.2,
            max_tokens=200,
        )
        summary_part = resp.choices[0].message.content.strip()
    except Exception:
        summary_part = "Неуспешно генериране – показани са само OCR-данните."

    html_part = _build_html_table(extracted_fields)

    return {
        "json_data": extracted_fields,
        "html_table": html_part,
        "summary": summary_part,
    }