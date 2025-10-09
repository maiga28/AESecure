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

def messages_view(request):
    """Affiche les messages chiffrés de l'utilisateur"""
    if not request.user.is_authenticated:
        messages.warning(request, "Veuillez vous connecter pour voir vos messages.")
        return redirect('admin:login')
    
    user_messages = EncryptedMessage.objects.filter(user=request.user)
    return render(request, 'crypto_app/messages.html', {'messages': user_messages})