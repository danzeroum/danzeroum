#!/usr/bin/env python3
"""Gera o bcrypt hash de uma senha para AUTH_PASSWORD_HASH."""
import getpass
import bcrypt

password = getpass.getpass("Senha: ").encode()
hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode()
print(f"\nAUTH_PASSWORD_HASH={hashed}")
