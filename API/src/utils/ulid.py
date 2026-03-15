from ulid import ULID

def generate_id(prefix: str):
    return f"{prefix}{ULID()}"