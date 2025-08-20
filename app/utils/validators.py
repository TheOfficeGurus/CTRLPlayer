import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
class Validators:
    
    @staticmethod
    def decrypt(cipher_data: str, key_string: str) -> str | None:
        try:
            iv =bytes([0x0, 0xA, 0xB, 0x3, 0x2, 0xF, 0xD, 0xA, 0x10, 0x21, 0x92, 0xA, 0xD, 0xF, 0xD, 0x3])
            key = hashlib.sha256(key_string.encode('ascii')).digest()
            encrypted_data = base64.b64decode(cipher_data)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            padding_len = decrypted_data[-1]
            unpadded_data = decrypted_data[:-padding_len]

            return unpadded_data.decode('utf-8')
        except Exception as e:
            return None