import re

def anonymize_text(text: str) -> str:

    text = re.sub(r'\b[A-ZА-Я][a-zа-я]+\b', '[NAME]', text)
    text = re.sub(r'\b\d{10}\b', '[ID]', text)
    text = re.sub(r'\+?\d{2,4}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3}[\s\-]?\d{3,4}', '[PHONE]', text)
    text = re.sub(r'\b\S+@\S+\.\S+\b', '[EMAIL]', text)
    text = re.sub(r'\b(ул\.|бул\.|ж\.к\.)\s+[^\n,]+', '[ADDRESS]', text)
    return text
