import io
import os
from google.cloud import vision
from google.oauth2 import service_account

def extract_text_from_image(image_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        return texts[0].description
    return "Не е открит текст"

def extract_medical_fields_from_text(text):
    extracted = {}

    patterns = {
        "TSH": r"(?:TSH|тиреотропен хормон)[^\d]*([\d.,]+)",
        "Глюкоза": r"(?:глюкоза|glucose)[^\d]*([\d.,]+)",
        "Дата": r"(?:\b|\D)(\d{2}[./-]\d{2}[./-]\d{4})(?:\b|\D)",
        "Т4": r"(?:T4|тироксин)[^\d]*([\d.,]+)",
        "HbA1c": r"(?:HbA1c)[^\d]*([\d.,]+)"
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            extracted[field] = match.group(1).replace(",", ".")

    return extracted
