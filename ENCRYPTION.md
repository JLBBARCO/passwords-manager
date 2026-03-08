# Technical Documentation - Encryption System

## Overview

Password Manager now includes a robust encryption system to protect stored passwords. This document describes the implementation and operation of the system.

## Technology Used

- **Library**: `cryptography` (Python)
- **Algorithm**: Fernet (AES implementation in CBC mode with HMAC for authentication)
- **Key Size**: 256 bits
- **Security**: Authenticated symmetric encryption

## Architecture

### Main Component: CryptoManager

Located in `src/lib/crypto/__init__.py`, the `CryptoManager` is responsible for:

1. **Key Management**
   - Generate a new cryptographic key on first execution
   - Load the existing key in subsequent executions
   - Store the key in `encryption.key` (in the project root)

2. **Encryption**
   - Method: `encrypt_password(password: str) -> str`
   - Converts the password to bytes
   - Applies Fernet encryption
   - Returns the encrypted password as a string

3. **Decryption**
   - Method: `decrypt_password(encrypted_password: str) -> str`
   - Converts the encrypted password back to bytes
   - Applies Fernet decryption
   - Returns the password in plain text
   - Has fallback for unencrypted passwords (useful during migration)

## Module Integration

### 1. Addition Module (`src/lib/add/__init__.py`)

**Changes:**

- Imports `get_crypto_manager()` from crypto module
- Initializes encryption manager in `__init__`
- Encrypts password before saving to JSON

**Flow:**

```text
Password (plaintext) → CryptoManager.encrypt_password() → Encrypted password → JSON
```

### 2. Reading Module (`src/lib/read_passwords/__init__.py`)

**Changes:**

- Imports `get_crypto_manager()` from crypto module
- Initializes encryption manager in `__init__`
- Decrypts all passwords after loading from JSON

**Flow:**

```text
JSON → Encrypted password → CryptoManager.decrypt_password() → Password (plaintext) → Application
```

### 3. Search Module (`src/lib/Search/__init__.py`)

**Changes:**

- Imports `get_crypto_manager()` from crypto module
- Initializes encryption manager in `__init__`
- Decrypts passwords before displaying in results
- Search works on decrypted passwords

**Flow:**

```text
JSON → Encrypted password → CryptoManager.decrypt_password() → Search (plaintext) → Results
```

### 4. Converter Module (`src/lib/converter/__init__.py`)

**Changes:**

- Imports `get_crypto_manager()` from crypto module
- Encrypts passwords when converting from CSV to JSON
- Deletes CSV file after successful conversion

**Flow:**

```text
CSV → Read → CryptoManager.encrypt_password() → Encrypted JSON → Delete CSV
```

## Automatic Migration

### Detection of Unencrypted Passwords

The system implements automatic detection of unencrypted passwords through the `_check_needs_encryption()` method in the `PasswordLoader` class:

1. **Verification**: When loading the JSON file, the system checks if passwords are encrypted
2. **Automatic Backup**: If unencrypted passwords are detected, a backup is created automatically
3. **Encryption**: All passwords are encrypted in-place
4. **Saving**: The file is saved with encrypted passwords
5. **Cleanup**: The temporary backup is deleted after success

### Automatic CSV Conversion

When a `passwords.csv` file is detected:

1. The file is read and converted to JSON
2. Passwords are encrypted during conversion
3. The JSON file is saved
4. The original CSV file is **automatically deleted**

### Complete Migration Flow

```text
Old File (Unencrypted CSV/JSON)
    ↓
[Automatic Detection]
    ↓
[Create Temporary Backup]
    ↓
[Encrypt All Passwords]
    ↓
[Save Updated File]
    ↓
[Delete Backup/Old File]
    ↓
New File (Encrypted JSON)
```

### Advantages of Automatic Migration

- **Zero user intervention**: Everything happens automatically
- **Security**: Temporary backup ensures data is not lost
- **Cleanup**: Old files are automatically removed
- **Transparency**: User sees progress messages but does not need to act

## Security

### Strengths

1. **AES-128 in CBC mode**: Robust and widely tested algorithm
2. **HMAC for authentication**: Prevents tampering with encrypted passwords
3. **Unique key per installation**: Each installation has its own key
4. **Transparent encryption**: The user does not need to manage the process

### Important Considerations

1. **Key Protection**
   - The key is stored in `encryption.key` and SHOULD NOT be versioned in Git
   - If the key is lost, passwords cannot be recovered
   - Recommendation: Backup the key in a secure location

2. **Limitations**
   - The key is stored in the file system (not protected by a master password)
   - For greater security, consider implementing:
     - Master password to protect the key
     - Key derivation using PBKDF2
     - Key storage in operating system keyring

## Manual Migration Script

**Note**: As of this version, migration is automatic. The manual script is optional.

The file `migrate_to_encrypted.py` allows you to manually migrate existing passwords with more control:

**Features:**

- Detects if passwords are already encrypted
- Creates permanent backup before migration (`passwords_backup.json`)
- Encrypts all passwords in the file
- Maintains original JSON structure
- Keeps backup after migration (different from automatic migration)

**Usage:**

```bash
python migrate_to_encrypted.py
```

## Data Format Example

### Before Encryption

```json
[
  {
    "Address": "github.com",
    "User": "user@email.com",
    "Password": "myPassword123"
  }
]
```

### After Encryption

```json
[
  {
    "Address": "github.com",
    "User": "user@email.com",
    "Password": "gAAAAABh8x9YZ..."
  }
]
```

## Error Handling

The system is designed to be resilient:

1. **Encryption Error**: Returns the original password and logs error
2. **Decryption Error**: Returns the original password (useful for migration)
3. **Missing Key**: Automatically generates a new key

## Recommended Tests

1. **Addition Test**
   - Add new password
   - Verify if it is encrypted in JSON
   - Verify if it is displayed correctly in the interface

2. **Search Test**
   - Search for encrypted passwords
   - Verify if search works in plaintext

3. **Migration Test**
   - Create unencrypted passwords
   - Run migration script
   - Verify all were encrypted

4. **Recovery Test**
   - Delete `encryption.key`
   - Verify if a new key is generated
   - Verify that old passwords cannot be decrypted

## Future Improvements

1. **Master Password**: Add a master password to protect the key
2. **OS Keyring**: Use the operating system keyring system
3. **Multiple Profiles**: Support multiple users with different keys
4. **Audit**: Log password access attempts
5. **Password Expiration**: Notify about old passwords

## Compliance

This system implements strong encryption and is suitable for personal use. For corporate use or compliance with specific regulations (GDPR, LGPD, etc.), consider:

- Professional security audit
- Implementation of additional access controls
- Key rotation policies
- Audit logs

## Support

For technical questions or improvement suggestions related to the encryption system, open an issue in the project repository.
