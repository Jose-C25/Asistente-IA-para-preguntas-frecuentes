import hashlib
import hmac
import os
import re

# Secret key para salting de hashes en el backend
SECRET_SALT = os.getenv("APP_SECRET_SALT", "DonJoseBot_OWASP_Secure_Salt_2026").encode('utf-8')

def generar_hash_password(password: str) -> str:
    """Genera un hash seguro con salting usando PBKDF2 (HMAC-SHA256)."""
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt + SECRET_SALT, 100000)
    return f"{salt.hex()}:{pw_hash.hex()}"

def verificar_password(password: str, stored_hash: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash almacenado."""
    try:
        salt_hex, pw_hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(pw_hash_hex)
        actual_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt + SECRET_SALT, 100000)
        return hmac.compare_digest(expected_hash, actual_hash)
    except Exception:
        return False

def sanitizar_entrada(texto: str) -> str:
    """Limpia caracteres potencialmente peligrosos contra inyecciones de comandos/scripting."""
    if not texto:
        return ""
    # Remover etiquetas HTML / Scripts
    texto_limpio = re.sub(r'<[^>]*?>', '', texto)
    return texto_limpio.strip()