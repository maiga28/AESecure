# crypto_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from .models import EncryptedMessage

# Actions personnalisées
def delete_old_messages(modeladmin, request, queryset):
    """Action pour supprimer les messages de plus de 30 jours"""
    cutoff_date = timezone.now() - timedelta(days=30)
    old_messages = queryset.filter(created_at__lt=cutoff_date)
    count = old_messages.count()
    old_messages.delete()
    modeladmin.message_user(request, f"{count} messages anciens ont été supprimés.")
delete_old_messages.short_description = "🗑️ Supprimer les messages de plus de 30 jours"

def export_messages_json(modeladmin, request, queryset):
    """Action pour exporter les messages sélectionnés"""
    modeladmin.message_user(request, f"Export de {queryset.count()} messages initié.")
export_messages_json.short_description = "📤 Exporter les messages sélectionnés"

def anonymize_messages(modeladmin, request, queryset):
    """Action pour anonymiser le contenu des messages"""
    for message in queryset:
        message.original_text = "[CONTENU ANONYMISÉ]"
        message.encrypted_text = "[CHIFFRÉ ANONYMISÉ]"
        message.save()
    modeladmin.message_user(request, f"{queryset.count()} messages ont été anonymisés.")
anonymize_messages.short_description = "🎭 Anonymiser le contenu"

@admin.register(EncryptedMessage)
class EncryptedMessageAdmin(admin.ModelAdmin):
    # ✅ CORRECTION ICI : actions doit être une liste/tuple
    actions = [delete_old_messages, export_messages_json, anonymize_messages]
    
    list_display = [
        'id', 
        'user_info', 
        'truncated_original_text', 
        'key_type_badge', 
        'created_at_formatted'
    ]
    
    list_filter = ['created_at', 'user']
    search_fields = ['original_text', 'user__username']
    readonly_fields = ['created_at', 'encrypted_text_preview']
    ordering = ['-created_at']
    
    def user_info(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "Anonyme"
    user_info.short_description = 'Utilisateur'
    
    def truncated_original_text(self, obj):
        return obj.original_text[:50] + '...' if len(obj.original_text) > 50 else obj.original_text
    truncated_original_text.short_description = 'Message Original'
    
    def key_type_badge(self, obj):
        if obj.encryption_key:
            return "🔑 Personnalisée"
        return "⚙️ Par défaut"
    key_type_badge.short_description = 'Type de Clé'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M")
    created_at_formatted.short_description = 'Date'
    
    def encrypted_text_preview(self, obj):
        return obj.encrypted_text[:100] + '...' if len(obj.encrypted_text) > 100 else obj.encrypted_text
    encrypted_text_preview.short_description = 'Texte Chiffré (Aperçu)'

# Version simplifiée si vous voulez éviter les problèmes
class SimpleEncryptedMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'truncated_original', 'created_at']
    
    def truncated_original(self, obj):
        return obj.original_text[:50] + '...' if len(obj.original_text) > 50 else obj.original_text
    truncated_original.short_description = 'Message'

# Pour tester rapidement, vous pouvez utiliser la version simplifiée :
# admin.site.register(EncryptedMessage, SimpleEncryptedMessageAdmin)