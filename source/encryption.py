import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class RSA:
    def generate_keys():
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        
        public_key = private_key.public_key()
        public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_key, public_key
    

    def key_validation(key):
        try:
            public_key = serialization.load_pem_public_key(key)
            return isinstance(public_key, rsa.RSAPublicKey)
        except (ValueError, TypeError):
            return False
    

    def encrypt(data, public_key):
        return public_key.encrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))


    def decrypt(data, private_key):
        return private_key.decrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    

class AES:
    # aes_key = os.urandom(32)
    def encrypt(data, key):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
        encryptor = cipher.encryptor()

        return iv + encryptor.update(data.encode()) + encryptor.finalize()


    def decrypt(data, key):
        iv, ciphertext = data[:16], data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
        decryptor = cipher.decryptor()

        return decryptor.update(ciphertext) + decryptor.finalize()