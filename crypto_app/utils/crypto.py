import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings

class AESCipher:
    def __init__(self, key=None):
        self.key = key or settings.AES_SECRET_KEY
        # S'assurer que la clé fait 16, 24 ou 32 octets
        if isinstance(self.key, str):
            self.key = self.key.encode('utf-8')
        
        if len(self.key) not in [16, 24, 32]:
            self.key = self.key[:32].ljust(32, b'\0')
    
    def encrypt(self, data):
        """Chiffre les données avec AES en mode CBC"""
        try:
            # Convertir en bytes si nécessaire
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Générer un IV aléatoire
            iv = os.urandom(16)
            
            # Créer le cipher
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            
            # Chiffrer les données - CORRECTION ICI
            encrypted_data = cipher.encrypt(pad(data, AES.block_size))
            
            # Combiner IV et données chiffrées
            combined = iv + encrypted_data
            
            # Encoder en base64 pour stockage
            return base64.b64encode(combined).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Erreur lors du chiffrement: {str(e)}")
    
    def decrypt(self, encrypted_data):
        """Déchiffre les données avec AES en mode CBC"""
        try:
            # Décoder la base64
            combined = base64.b64decode(encrypted_data)
            
            # Extraire l'IV et les données chiffrées
            iv = combined[:16]
            encrypted_data = combined[16:]
            
            # Créer le cipher
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            
            # Déchiffrer les données - CORRECTION ICI
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Erreur lors du déchiffrement: {str(e)}")

# Fonctions utilitaires pour une utilisation facile
def encrypt_text(text, key=None):
    cipher = AESCipher(key)
    return cipher.encrypt(text)

def decrypt_text(encrypted_text, key=None):
    cipher = AESCipher(key)
    return cipher.decrypt(encrypted_text)