from django.db import models
from django.contrib.auth.models import User
from .utils.crypto import encrypt_text, decrypt_text

class EncryptedMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    original_text = models.TextField(verbose_name="Texte original")
    encrypted_text = models.TextField(verbose_name="Texte chiffré")
    encryption_key = models.CharField(max_length=255, blank=True, verbose_name="Clé de chiffrement")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    def save(self, *args, **kwargs):
        # Chiffrer le texte avant sauvegarde
        if self.original_text and not self.encrypted_text:
            self.encrypted_text = encrypt_text(self.original_text, self.encryption_key or None)
        super().save(*args, **kwargs)
    
    def get_decrypted_text(self, key=None):
        """Retourne le texte déchiffré"""
        try:
            return decrypt_text(self.encrypted_text, key or self.encryption_key or None)
        except Exception as e:
            return f"Erreur de déchiffrement: {str(e)}"
    
    def __str__(self):
        return f"Message {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Message chiffré"
        verbose_name_plural = "Messages chiffrés"
        ordering = ['-created_at']