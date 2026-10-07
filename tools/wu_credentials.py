"""Optional authenticated encryption for a locally held Weather Underground key."""
import argparse
import base64
import getpass
import json
import os
from pathlib import Path


def derive(password, salt):
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    return Scrypt(salt=salt, length=32, n=32768, r=8, p=1).derive(password.encode())


def encrypt(key, password):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if not key.strip() or len(key) > 256:
        raise ValueError('Invalid key length')
    if len(password) < 12:
        raise ValueError('Use a passphrase of at least 12 characters')
    salt, nonce = os.urandom(16), os.urandom(12)
    ciphertext = AESGCM(derive(password, salt)).encrypt(nonce, key.strip().encode(), b'Flame-WU-v1')
    encode = lambda value: base64.b64encode(value).decode()
    return json.dumps(dict(version=1, salt=encode(salt), nonce=encode(nonce), ciphertext=encode(ciphertext)))


def decrypt(content, password):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if len(content) > 8192:
        raise ValueError('Invalid encrypted file')
    data = json.loads(content)
    if data['version'] != 1:
        raise ValueError('Unsupported encrypted file')
    decode = lambda value: base64.b64decode(value, validate=True)
    salt, nonce = decode(data['salt']), decode(data['nonce'])
    if len(salt) != 16 or len(nonce) != 12:
        raise ValueError('Invalid encrypted file')
    return AESGCM(derive(password, salt)).decrypt(nonce, decode(data['ciphertext']), b'Flame-WU-v1').decode()


def unlock(path):
    password = getpass.getpass('Palavra-passe do ficheiro cifrado: ')
    try:
        return decrypt(Path(path).read_text(), password)
    except Exception:
        raise SystemExit('Não foi possível decifrar a chave. Verifique ficheiro e palavra-passe.') from None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('.wu-key.enc'))
    args = parser.parse_args()
    key = getpass.getpass('Chave Weather Underground (oculta): ')
    password = getpass.getpass('Nova palavra-passe (pelo menos 12 caracteres): ')
    if password != getpass.getpass('Repita a palavra-passe: '):
        raise SystemExit('As palavras-passe não coincidem.')
    try:
        content = encrypt(key, password)
        # Exclusive creation protects a previous credential file; permission is owner-only.
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as handle:
            handle.write(content)
    except Exception:
        raise SystemExit('Não foi possível criar o ficheiro. Verifique dependências, palavra-passe e se o ficheiro já existe.') from None
    print('Chave cifrada guardada. A palavra-passe não foi guardada.')
