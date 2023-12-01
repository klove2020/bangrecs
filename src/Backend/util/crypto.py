""" 已弃用
作为bangumi授权使用的身份验证使用
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from base64 import urlsafe_b64encode, urlsafe_b64decode

# 初始化AES Cipher的密钥
key = b'sixteen_byte_key'  # 注意：密钥需要是16/24/32字节长

# 加密
def encrypt(data):
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded_data = pad(data.encode('utf-8'), 16)
    encrypted_data = cipher.encrypt(padded_data)
    return urlsafe_b64encode(iv + encrypted_data).decode('utf-8')

# 解密
def decrypt(encrypted_data):
    encrypted_data = urlsafe_b64decode(encrypted_data.encode('utf-8'))
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), 16).decode('utf-8')
    return decrypted_data
