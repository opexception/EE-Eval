from functools import lru_cache

from pwdlib import PasswordHash


@lru_cache
def get_password_hasher() -> PasswordHash:
    return PasswordHash.recommended()


class PasswordService:
    def hash_password(self, password: str) -> str:
        return get_password_hasher().hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        return get_password_hasher().verify(password, password_hash)

