# ProcessHollowMultiCrypt

# Shellcode Encryption and C# Template Generator

**A Python script to encrypt shellcode using various encryption algorithms (AES, Caesar, RC4, XOR) and generate a C# template for process hollowing with the encrypted shellcode. The generated C# file decrypts the shellcode at runtime and injects it into the target process (`svchost.exe`).**

## 🔑 Key Features:
- **Multiple Encryption Methods**: Supports AES, Caesar, RC4, and XOR encryption to protect the shellcode.
- **Dynamic C# Code Generation**: Generates a C# template for process hollowing with the specified encryption method.
- **Process Hollowing**: The generated C# code performs process hollowing by injecting the decrypted shellcode into `svchost.exe`.
- **Flexible Encryption**: Allows for various encryption methods to add an extra layer of security.

## 📝 Usage:

### Command to Run the Script:
```bash
Usage: python3 script.py <shellcode.bin> <output.cs> <method>
Methods: AES, Caesar, RC4, XOR

```
### Example
```bash
python3 script.py shellcode.bin process_hollow.cs AES / RC4 / XOR / Caesaer
```
## 🔐 Encryption Methods:

## AES Encryption:

Uses 256-bit AES in CBC mode with a randomly generated IV and key.
Decryption is handled within the generated C# template.

## Caesar Cipher:

A simple shift cipher where each byte of the shellcode is shifted by a fixed value (e.g., 3).
The generated C# code will shift the bytes back to their original values at runtime.

## RC4 Encryption:

A stream cipher with a randomly generated key.
The RC4 decryption routine is included in the C# template to decrypt the shellcode during process injection.

## XOR Encryption:

Uses a single-byte XOR key to encrypt the shellcode.
The C# template includes the necessary XOR decryption logic.
