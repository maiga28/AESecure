from django.urls import path
from . import views

app_name = 'crypto_app'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('encrypt/', views.encrypt_view, name='encrypt'),
    path('decrypt/', views.decrypt_view, name='decrypt'),
    path('messages/', views.messages_view, name='messages'),
]