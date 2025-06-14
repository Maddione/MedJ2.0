import io
import os
import re

from dotenv import load_dotenv
from google.cloud import vision

load_dotenv()

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if credentials_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    client = vision.ImageAnnotatorClient()
else:
    client = None


def extract_text_from_image(image_path):
    """Извлича текст от изображение чрез Google Cloud Vision API."""
    if client is None:
        return ""

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    texts = response.text_annotations
    if texts:
        return texts[0].description
    return ""


def extract_medical_fields_from_text(text):
    """
    Търси ключови медицински стойности в текста и ги връща като речник.
    """
    fields = {
        "TSH": r"TSH\s*[:=]?\s*(\d+[.,]?\d*)",
        "Глюкоза": r"Глюкоза\s*[:=]?\s*(\d+[.,]?\d*)",
        "Дата": r"(\d{2}[./-]\d{2}[./-]\d{4})"
    }

    results = {}
    for key, pattern in fields.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results[key] = match.group(1).replace(",", ".")
    return results
