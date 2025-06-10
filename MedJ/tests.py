import os
import django
from django.test import TestCase
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MedJ2.settings')
django.setup()

class RegistrationViewTests(TestCase):
    def test_registration_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Регистрация', response.content.decode())
