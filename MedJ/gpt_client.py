import json
import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def call_gpt_for_document(raw_text: str, doc_kind: str, extracted_fields: dict) -> dict:
    prompt = (
        f"Документ тип: {doc_kind}.\n"
        f"Извлечен текст:\n\"\"\"{raw_text}\"\"\"\n\n"
        "Моля направи следното:\n"
        "1) Върни JSON обект с ключове и стойности. Дата да е низ в DD-MM-YYYY формат.\n"
        "2) Върни HTML таблица със заглавия на български: Показател, Стойност, Ед., Статус, Реф. граници.\n"
        "3) Върни анализен параграф, който за всеки показател извън референтните граници указва дали е повишен или понижен.\n"
        "Форматирай отговора така:\n"
        "===JSON===\n"
        "{\n"
        '  "date": "11-06-2025",\n'
        '  "Хемоглобин": 124.0\n'
        "}\n"
        "===HTML===\n"
        "<table>…</table>\n"
        "===SUMMARY===\n"
        "…анализен текст…"
    )
    resp = openai.OpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=700
    )
    content = resp.choices[0].message.content
    json_part = content.split("===JSON===")[1].split("===HTML===")[0].strip()
    html_part = content.split("===HTML===")[1].split("===SUMMARY===")[0].strip()
    summary_part = content.split("===SUMMARY===")[1].strip()
    try:
        json_data = json.loads(json_part)
    except:
        json_data = extracted_fields
        html_part = ""
        from MedJ.utils.summary import generate_local_summary
        summary_part = generate_local_summary(extracted_fields)
    return {"json_data": json_data, "html_table": html_part, "summary": summary_part}
