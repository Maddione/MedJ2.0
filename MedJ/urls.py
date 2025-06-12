from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landingpage'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('casefiles/', views.casefiles, name='casefiles'),
    path('personalcard/', views.personalcard, name='personalcard'),
    path('upload/', views.upload, name='upload'),
    path('history/', views.history, name='history'),
    path('profile/', views.profile, name='profile'),
    path('doctors/', views.doctors, name='doctors'),
    path('logout/', views.logout_view, name='logout'),
]
