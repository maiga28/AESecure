# crypto_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import json
from .models import EncryptedMessage
from .utils.crypto import decrypt_text

# Actions personnalisées
def delete_old_messages(modeladmin, request, queryset):
    """Action pour supprimer les messages de plus de 30 jours"""
    cutoff_date = timezone.now() - timedelta(days=30)
    old_messages = queryset.filter(created_at__lt=cutcutoff_date)
    count = old_messages.count()
    old_messages.delete()
    modeladmin.message_user(request, f"{count} messages anciens ont été supprimés.")
delete_old_messages.short_description = "🗑️ Supprimer les messages de plus de 30 jours"

def export_messages_json(modeladmin, request, queryset):
    """Action pour exporter les messages sélectionnés"""
    data = []
    for message in queryset:
        data.append({
            'id': message.id,
            'user': message.user.username if message.user else 'Anonyme',
            'original_text': message.original_text,
            'encrypted_text': message.encrypted_text,
            'encryption_key': message.encryption_key or 'Défaut',
            'created_at': message.created_at.isoformat(),
        })
    
    response = HttpResponse(json.dumps(data, indent=2, ensure_ascii=False), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="messages_export.json"'
    return response
export_messages_json.short_description = "📤 Exporter en JSON"

def anonymize_messages(modeladmin, request, queryset):
    """Action pour anonymiser le contenu des messages"""
    for message in queryset:
        message.original_text = "[CONTENU ANONYMISÉ]"
        message.encrypted_text = "[CHIFFRÉ ANONYMISÉ]"
        message.save()
    modeladmin.message_user(request, f"{queryset.count()} messages ont été anonymisés.")
anonymize_messages.short_description = "🎭 Anonymiser le contenu"

def decrypt_selected_messages(modeladmin, request, queryset):
    """Action pour déchiffrer les messages sélectionnés"""
    results = []
    for message in queryset:
        try:
            decrypted_text = decrypt_text(message.encrypted_text, message.encryption_key or None)
            results.append({
                'id': message.id,
                'status': '✅ Succès',
                'decrypted_text': decrypted_text
            })
        except Exception as e:
            results.append({
                'id': message.id,
                'status': '❌ Erreur',
                'error': str(e)
            })
    
    # Créer un rapport de déchiffrement
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="rapport_dechiffrement.txt"'
    
    content = "RAPPORT DE DÉCHIFFREMENT\n"
    content += "=" * 50 + "\n\n"
    
    for result in results:
        content += f"Message ID: {result['id']}\n"
        content += f"Status: {result['status']}\n"
        if 'decrypted_text' in result:
            content += f"Texte déchiffré: {result['decrypted_text']}\n"
        else:
            content += f"Erreur: {result['error']}\n"
        content += "-" * 30 + "\n"
    
    response.write(content)
    return response
decrypt_selected_messages.short_description = "🔓 Déchiffrer et exporter"

@admin.register(EncryptedMessage)
class EncryptedMessageAdmin(admin.ModelAdmin):
    # Actions disponibles
    actions = [
        decrypt_selected_messages,
        delete_old_messages, 
        export_messages_json, 
        anonymize_messages
    ]
    
    # Configuration de l'affichage de la liste
    list_display = [
        'id', 
        'user_info', 
        'truncated_original_text', 
        'key_type_badge', 
        'created_at_formatted',
        'quick_decrypt'
    ]
    
    list_filter = ['created_at', 'user']
    search_fields = ['original_text', 'encrypted_text', 'user__username', 'user__email']
    readonly_fields = [
        'created_at', 
        'encrypted_text_preview',
        'decryption_status',
        'security_info'
    ]
    ordering = ['-created_at']
    list_per_page = 25
    
    # Champs affichés dans le détail
    fieldsets = (
        ('Informations du Message', {
            'fields': (
                'user_info_detailed',
                'original_text',
                'encrypted_text_preview',
            )
        }),
        ('Déchiffrement', {
            'fields': (
                'decryption_status',
                'manual_decryption',
            ),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': (
                'encryption_key',
                'key_type_display',
            )
        }),
        ('Métadonnées', {
            'fields': (
                'created_at',
                'security_info',
            )
        }),
    )
    
    # Méthodes d'affichage personnalisées
    def user_info(self, obj):
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.user.username,
                obj.user.email
            )
        return "Anonyme"
    user_info.short_description = 'Utilisateur'
    user_info.admin_order_field = 'user__username'
    
    def user_info_detailed(self, obj):
        if obj.user:
            return format_html(
                '''
                <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                    <strong>👤 {}</strong><br>
                    <small>📧 {}</small><br>
                    <small>🆔 ID: {}</small>
                </div>
                ''',
                obj.user.username,
                obj.user.email,
                obj.user.id
            )
        return "Anonyme"
    user_info_detailed.short_description = 'Informations Utilisateur'
    
    def truncated_original_text(self, obj):
        truncated = obj.original_text[:50] + '...' if len(obj.original_text) > 50 else obj.original_text
        return format_html(
            '<div title="{}" style="max-width: 200px;">{}</div>',
            obj.original_text,
            truncated
        )
    truncated_original_text.short_description = 'Message Original'
    
    def key_type_badge(self, obj):
        if obj.encryption_key:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px;">🔑 Personnalisée</span>'
            )
        return format_html(
            '<span style="background: #6b7280; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px;">⚙️ Par défaut</span>'
        )
    key_type_badge.short_description = 'Type de Clé'
    
    def key_type_display(self, obj):
        if obj.encryption_key:
            return format_html(
                '<div style="color: #10b981; font-weight: bold;">🔑 Clé personnalisée utilisée</div>'
            )
        return format_html(
            '<div style="color: #6b7280; font-weight: bold;">⚙️ Clé par défaut utilisée</div>'
        )
    key_type_display.short_description = 'Type de Clé'
    
    def encrypted_text_preview(self, obj):
        preview = obj.encrypted_text[:100] + '...' if len(obj.encrypted_text) > 100 else obj.encrypted_text
        return format_html(
            '<div style="font-family: monospace; background: #1f2937; color: #10b981; padding: 10px; border-radius: 5px; overflow-x: auto; font-size: 12px;">{}</div>',
            preview
        )
    encrypted_text_preview.short_description = 'Texte Chiffré (Aperçu)'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M")
    created_at_formatted.short_description = 'Date'
    created_at_formatted.admin_order_field = 'created_at'
    
    def quick_decrypt(self, obj):
        return format_html(
            '''
            <button onclick="decryptSingleMessage({})" 
                    style="background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer;">
                🔓 Test
            </button>
            ''',
            obj.id
        )
    quick_decrypt.short_description = 'Test Déchiffrement'
    
    def decryption_status(self, obj):
        try:
            decrypted_text = decrypt_text(obj.encrypted_text, obj.encryption_key or None)
            return format_html(
                '''
                <div style="padding: 10px; background: #d1fae5; border: 1px solid #10b981; border-radius: 5px;">
                    <strong style="color: #065f46;">✅ Déchiffrement réussi</strong><br>
                    <div style="margin-top: 8px; padding: 8px; background: white; border-radius: 3px; font-family: monospace; font-size: 12px;">
                        {}
                    </div>
                </div>
                ''',
                decrypted_text
            )
        except Exception as e:
            return format_html(
                '''
                <div style="padding: 10px; background: #fee2e2; border: 1px solid #ef4444; border-radius: 5px;">
                    <strong style="color: #991b1b;">❌ Erreur de déchiffrement</strong><br>
                    <small>{}</small>
                </div>
                ''',
                str(e)
            )
    decryption_status.short_description = 'Statut Déchiffrement'
    
    def security_info(self, obj):
        key_length = len(obj.encryption_key) if obj.encryption_key else "Défaut"
        text_length = len(obj.original_text)
        age_days = (timezone.now() - obj.created_at).days
        
        return format_html(
            '''
            <div style="padding: 10px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px;">
                <strong>🔒 Informations de Sécurité</strong><br>
                <small>📏 Longueur clé: <strong>{}</strong></small><br>
                <small>📝 Longueur texte: <strong>{} caractères</strong></small><br>
                <small>🕐 Âge: <strong>{} jours</strong></small><br>
                <small>👤 Utilisateur: <strong>{}</strong></small>
            </div>
            ''',
            key_length,
            text_length,
            age_days,
            obj.user.username if obj.user else "Anonyme"
        )
    security_info.short_description = 'Informations de Sécurité'
    
    def manual_decryption(self, obj):
        return format_html(
            '''
            <div style="padding: 10px; background: #e0f2fe; border-radius: 5px;">
                <strong>🔧 Déchiffrement Manuel</strong><br>
                <small>Utilisez la clé: <code>{}</code></small>
            </div>
            ''',
            obj.encryption_key if obj.encryption_key else "Clé par défaut"
        )
    manual_decryption.short_description = 'Aide Déchiffrement'

# Script JavaScript pour le déchiffrement en direct
class EncryptedMessageAdminWithJS(EncryptedMessageAdmin):
    class Media:
        js = (
            'admin/js/crypto_admin.js',  # Vous pouvez créer ce fichier
        )

# Version simplifiée alternative
class SimpleEncryptedMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'truncated_original', 'created_at', 'quick_actions']
    
    def truncated_original(self, obj):
        return obj.original_text[:50] + '...' if len(obj.original_text) > 50 else obj.original_text
    truncated_original.short_description = 'Message'
    
    def quick_actions(self, obj):
        return format_html(
            '''
            <div style="display: flex; gap: 5px;">
                <button style="background: #3b82f6; color: white; border: none; padding: 2px 6px; border-radius: 3px; font-size: 10px; cursor: pointer;">
                    🔓
                </button>
                <button style="background: #ef4444; color: white; border: none; padding: 2px 6px; border-radius: 3px; font-size: 10px; cursor: pointer;">
                    🗑️
                </button>
            </div>
            '''
        )
    quick_actions.short_description = 'Actions'

# Pour utiliser la version simplifiée, décommentez la ligne suivante :
# admin.site.register(EncryptedMessage, SimpleEncryptedMessageAdmin)