"""Encryption utilities"""

from cryptography.fernet import Fernet


def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key"""
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    print("Generated Encryption Key:")
    print(generate_encryption_key())
    print("\nAdd this to your .env file as ENCRYPTION_KEY")
