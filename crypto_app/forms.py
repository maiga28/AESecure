# crypto_app/forms.py
from django import forms

class EncryptionForm(forms.Form):
    text = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
            'rows': 6,
            'placeholder': 'Entrez le texte que vous souhaitez chiffrer...'
        }),
        max_length=1000
    )
    
    custom_key = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
            'placeholder': 'Laissez vide pour utiliser la clé par défaut'
        }),
        max_length=32
    )

class DecryptionForm(forms.Form):
    encrypted_text = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
            'rows': 6,
            'placeholder': 'Collez le texte chiffré ici...'
        })
    )
    
    decryption_key = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
            'placeholder': 'Entrez la clé utilisée pour le chiffrement'
        }),
        max_length=32
    )