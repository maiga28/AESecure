from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from .forms import EncryptionForm, DecryptionForm
from .models import EncryptedMessage
from .utils.crypto import encrypt_text, decrypt_text

class HomeView(TemplateView):
    template_name = 'crypto_app/index.html'

def encrypt_view(request):
    context = {}
    
    if request.method == 'POST':
        form = EncryptionForm(request.POST)
        if form.is_valid():
            try:
                text = form.cleaned_data['text']
                custom_key = form.cleaned_data['custom_key']
                
                # Chiffrer le texte
                encrypted_text = encrypt_text(text, custom_key or None)
                
                # Sauvegarder en base si l'utilisateur est connecté
                if request.user.is_authenticated:
                    EncryptedMessage.objects.create(
                        user=request.user,
                        original_text=text,
                        encrypted_text=encrypted_text,
                        encryption_key=custom_key or ''
                    )
                
                context['encrypted_text'] = encrypted_text
                context['original_text'] = text
                messages.success(request, "Texte chiffré avec succès !")
                
            except Exception as e:
                messages.error(request, f"Erreur lors du chiffrement: {str(e)}")
    else:
        form = EncryptionForm()
    
    context['form'] = form
    return render(request, 'crypto_app/encrypt.html', context)

def decrypt_view(request):
    context = {}
    
    if request.method == 'POST':
        form = DecryptionForm(request.POST)
        if form.is_valid():
            try:
                encrypted_text = form.cleaned_data['encrypted_text']
                decryption_key = form.cleaned_data['decryption_key']
                
                # Déchiffrer le texte
                decrypted_text = decrypt_text(encrypted_text, decryption_key or None)
                
                context['decrypted_text'] = decrypted_text
                context['encrypted_text'] = encrypted_text
                messages.success(request, "Texte déchiffré avec succès !")
                
            except Exception as e:
                messages.error(request, f"Erreur lors du déchiffrement: {str(e)}")
    else:
        form = DecryptionForm()
    
    context['form'] = form
    return render(request, 'crypto_app/decrypt.html', context)


# crypto_app/views.py
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator

def messages_view(request):
    """Affiche les messages chiffrés de l'utilisateur"""
    if not request.user.is_authenticated:
        messages.warning(request, "Veuillez vous connecter pour voir vos messages.")
        return redirect('admin:login')
    
    user_messages = EncryptedMessage.objects.filter(user=request.user).order_by('-created_at')
    
    # Statistiques
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    messages_this_month = user_messages.filter(created_at__gte=month_start).count()
    messages_today = user_messages.filter(created_at__date=today).count()
    unique_keys = user_messages.exclude(encryption_key='').values('encryption_key').distinct().count()
    
    # Pagination
    paginator = Paginator(user_messages, 10)  # 10 messages par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'messages': page_obj,
        'messages_this_month': messages_this_month,
        'messages_today': messages_today,
        'unique_keys': unique_keys,
    }
    
    return render(request, 'crypto_app/messages.html', context)