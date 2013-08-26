import zlib
import struct
from Crypto.Cipher import AES
from Crypto import Random


class CheckSumError(Exception):
    pass

def _lazysecret(secret, blocksize=32, padding='}'):
    """pads secret if not legal AES block size (16, 24, 32)"""
    if not len(secret) in (16, 24, 32):
        return secret + (blocksize - len(secret)) * padding
    return secret

def encrypt(plaintext, secret, lazy=True, checksum=True):
    """encrypt plaintext with secret
    plaintext   - content to encrypt
    secret      - secret to encrypt plaintext
    lazy        - pad secret if less than legal blocksize (default: True)
    checksum    - attach crc32 byte encoded (default: True)
    returns ciphertext
    """

    if lazy:
        secret = _lazysecret(secret) 

    iv = Random.new().read(AES.block_size)
    encobj = AES.new(secret, AES.MODE_CFB, iv)

    if checksum:
        plaintext += struct.pack("i", zlib.crc32(plaintext))

    return iv + encobj.encrypt(plaintext)

def decrypt(ciphertext, secret, lazy=True, checksum=True):
    """decrypt ciphertext with secret
    ciphertext  - encrypted content to decrypt
    secret      - secret to decrypt ciphertext
    lazy        - pad secret if less than legal blocksize (default: True)
    checksum    - verify crc32 byte encoded checksum (default: True)
    returns plaintext
    """

    if lazy:
        secret = _lazysecret(secret)

    (iv, ciphertext) = (ciphertext[:16], ciphertext[16:])
    encobj = AES.new(secret, AES.MODE_CFB, iv)
    plaintext = encobj.decrypt(ciphertext)

    if checksum:
        crc, plaintext = (plaintext[-4:], plaintext[:-4])
        if not crc == struct.pack("i", zlib.crc32(plaintext)):
            raise CheckSumError("checksum mismatch")

    return plaintext

