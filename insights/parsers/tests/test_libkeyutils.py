from insights.parsers.libkeyutils import Libkeyutils, LibkeyutilsObjdumps
from insights.tests import context_wrap

SEARCH_NOT_FOUND = '''
/lib/libkeyutils.so.1
/lib/libkeyutils.so.1.6
/lib/debug/usr/lib64/libkeyutils.so.1.5.debug
/lib/debug/usr/lib64/libkeyutils.so.1.debug
/lib/debug/usr/lib64/libkeyutils.so.debug
/lib64/libkeyutils.so.1
/lib64/libkeyutils.so.1.6
/lib64/libkeyutils.so
'''

SEARCH_FOUND_1 = '''
/lib/libkeyutils.so.1
/lib/tls/libkeyutils.so.1.6
/lib/debug/usr/lib64/libkeyutils.so.1.5.debug
/lib/debug/usr/lib64/libkeyutils.so.1.debug
/lib/debug/usr/lib64/libkeyutils.so.debug
/lib64/libkeyutils.so.1
/lib64/libkeyutils.so.1.6
/lib64/libkeyutils.so
'''

SEARCH_FOUND_2 = '''
/lib/libkeyutils.so.1
/lib/tls/libkeyutils.so.1.6
/lib/debug/usr/lib64/libkeyutils.so.1.5.debug
/lib/debug/usr/lib64/libkeyutils.so.1.debug
/lib/debug/usr/lib64/libkeyutils.so.debug
/lib64/tls/libkeyutils.so.1
/lib64/libkeyutils.so.1.6
/lib64/libkeyutils.so
'''

DUMP_NOT_FOUND = '''

/lib/libkeyutils.so.1:     file format elf32-i386
/lib/libkeyutils.so.1
architecture: i386, flags 0x00000150:
HAS_SYMS, DYNAMIC, D_PAGED
start address 0x00000f80

Program Header:
    LOAD off    0x00000000 vaddr 0x00000000 paddr 0x00000000 align 2**12
         filesz 0x000028b4 memsz 0x000028b4 flags r-x
    LOAD off    0x00002e6c vaddr 0x00003e6c paddr 0x00003e6c align 2**12
         filesz 0x00000194 memsz 0x00000198 flags rw-
 DYNAMIC off    0x00002e78 vaddr 0x00003e78 paddr 0x00003e78 align 2**2
         filesz 0x000000f8 memsz 0x000000f8 flags rw-
    NOTE off    0x00000114 vaddr 0x00000114 paddr 0x00000114 align 2**2
         filesz 0x00000024 memsz 0x00000024 flags r--
EH_FRAME off    0x000021d8 vaddr 0x000021d8 paddr 0x000021d8 align 2**2
         filesz 0x00000134 memsz 0x00000134 flags r--
   STACK off    0x00000000 vaddr 0x00000000 paddr 0x00000000 align 2**4
         filesz 0x00000000 memsz 0x00000000 flags rw-
   RELRO off    0x00002e6c vaddr 0x00003e6c paddr 0x00003e6c align 2**0
         filesz 0x00000194 memsz 0x00000194 flags r--

Dynamic Section:
  NEEDED               libdl.so.2
  NEEDED               libc.so.6
  SONAME               libkeyutils.so.1
  INIT                 0x00000e54
  FINI                 0x00002134
  INIT_ARRAY           0x00003e6c
  INIT_ARRAYSZ         0x00000004
  FINI_ARRAY           0x00003e70
  FINI_ARRAYSZ         0x00000004
  GNU_HASH             0x00000138
  STRTAB               0x000006f8
  SYMTAB               0x000002b8
  STRSZ                0x00000457
  SYMENT               0x00000010
  PLTGOT               0x00003f70
  REL                  0x00000d34
  RELSZ                0x00000120
  RELENT               0x00000008
  VERDEF               0x00000bd8
  VERDEFNUM            0x00000007
  BIND_NOW             0x00000000
  FLAGS_1              0x00000001
  VERNEED              0x00000cc4
  VERNEEDNUM           0x00000001
  VERSYM               0x00000b50
  RELCOUNT             0x00000003

Version definitions:
1 0x01 0x02928561 libkeyutils.so.1
2 0x00 0x0ae3c993 KEYUTILS_0.3
3 0x00 0x0ae3ca90 KEYUTILS_1.0
	KEYUTILS_0.3
4 0x00 0x0ae3ca93 KEYUTILS_1.3
	KEYUTILS_1.0
5 0x00 0x0ae3ca94 KEYUTILS_1.4
	KEYUTILS_1.3
6 0x00 0x0ae3ca95 KEYUTILS_1.5
	KEYUTILS_1.4
7 0x00 0x0ae3ca96 KEYUTILS_1.6
	KEYUTILS_1.5

Version References:
  required from libc.so.6:
    0x09691974 0x00 13 GLIBC_2.3.4
    0x0d696917 0x00 12 GLIBC_2.7
    0x09691f73 0x00 11 GLIBC_2.1.3
    0x0d696914 0x00 10 GLIBC_2.4
    0x0d696911 0x00 09 GLIBC_2.1
    0x0d696910 0x00 08 GLIBC_2.0

Sections:
Idx Name          Size      VMA       LMA       File off  Algn
  0 .note.gnu.build-id 00000024  00000114  00000114  00000114  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  1 .gnu.hash     00000180  00000138  00000138  00000138  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  2 .dynsym       00000440  000002b8  000002b8  000002b8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  3 .dynstr       00000457  000006f8  000006f8  000006f8  2**0
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  4 .gnu.version  00000088  00000b50  00000b50  00000b50  2**1
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  5 .gnu.version_d 000000ec  00000bd8  00000bd8  00000bd8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  6 .gnu.version_r 00000070  00000cc4  00000cc4  00000cc4  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  7 .rel.dyn      00000120  00000d34  00000d34  00000d34  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  8 .init         00000023  00000e54  00000e54  00000e54  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
  9 .plt          00000010  00000e80  00000e80  00000e80  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 10 .plt.got      000000f0  00000e90  00000e90  00000e90  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 11 .text         000011b4  00000f80  00000f80  00000f80  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 12 .fini         00000014  00002134  00002134  00002134  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 13 .rodata       00000090  00002148  00002148  00002148  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 14 .eh_frame_hdr 00000134  000021d8  000021d8  000021d8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 15 .eh_frame     000005a8  0000230c  0000230c  0000230c  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 16 .init_array   00000004  00003e6c  00003e6c  00002e6c  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 17 .fini_array   00000004  00003e70  00003e70  00002e70  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 18 .data.rel.ro  00000004  00003e74  00003e74  00002e74  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 19 .dynamic      000000f8  00003e78  00003e78  00002e78  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 20 .got          00000090  00003f70  00003f70  00002f70  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 21 .bss          00000004  00004000  00004000  00003000  2**0
                  ALLOC
 22 .gnu_debuglink 00000020  00000000  00000000  00003000  2**2
                  CONTENTS, READONLY
 23 .gnu_debugdata 00000424  00000000  00000000  00003020  2**0
                  CONTENTS, READONLY
SYMBOL TABLE:
no symbols



/lib64/libkeyutils.so.1:     file format elf64-x86-64
/lib64/libkeyutils.so.1
architecture: i386:x86-64, flags 0x00000150:
HAS_SYMS, DYNAMIC, D_PAGED
start address 0x00000000000014b0

Program Header:
    LOAD off    0x0000000000000000 vaddr 0x0000000000000000 paddr 0x0000000000000000 align 2**21
         filesz 0x000000000000290c memsz 0x000000000000290c flags r-x
    LOAD off    0x0000000000002cd0 vaddr 0x0000000000202cd0 paddr 0x0000000000202cd0 align 2**21
         filesz 0x0000000000000330 memsz 0x0000000000000338 flags rw-
 DYNAMIC off    0x0000000000002ce8 vaddr 0x0000000000202ce8 paddr 0x0000000000202ce8 align 2**3
         filesz 0x00000000000001f0 memsz 0x00000000000001f0 flags rw-
    NOTE off    0x00000000000001c8 vaddr 0x00000000000001c8 paddr 0x00000000000001c8 align 2**2
         filesz 0x0000000000000024 memsz 0x0000000000000024 flags r--
EH_FRAME off    0x0000000000002250 vaddr 0x0000000000002250 paddr 0x0000000000002250 align 2**2
         filesz 0x000000000000012c memsz 0x000000000000012c flags r--
   STACK off    0x0000000000000000 vaddr 0x0000000000000000 paddr 0x0000000000000000 align 2**4
         filesz 0x0000000000000000 memsz 0x0000000000000000 flags rw-
   RELRO off    0x0000000000002cd0 vaddr 0x0000000000202cd0 paddr 0x0000000000202cd0 align 2**0
         filesz 0x0000000000000330 memsz 0x0000000000000330 flags r--

Dynamic Section:
  NEEDED               libdl.so.2
  NEEDED               libc.so.6
  SONAME               libkeyutils.so.1
  INIT                 0x0000000000001390
  FINI                 0x000000000000219c
  INIT_ARRAY           0x0000000000202cd0
  INIT_ARRAYSZ         0x0000000000000008
  FINI_ARRAY           0x0000000000202cd8
  FINI_ARRAYSZ         0x0000000000000008
  GNU_HASH             0x00000000000001f0
  STRTAB               0x00000000000009e8
  SYMTAB               0x0000000000000370
  STRSZ                0x0000000000000455
  SYMENT               0x0000000000000018
  PLTGOT               0x0000000000202ed8
  RELA                 0x0000000000001018
  RELASZ               0x0000000000000378
  RELAENT              0x0000000000000018
  VERDEF               0x0000000000000ec8
  VERDEFNUM            0x0000000000000007
  BIND_NOW             0x0000000000000000
  FLAGS_1              0x0000000000000001
  VERNEED              0x0000000000000fb8
  VERNEEDNUM           0x0000000000000001
  VERSYM               0x0000000000000e3e
  RELACOUNT            0x0000000000000003

Version definitions:
1 0x01 0x02928561 libkeyutils.so.1
2 0x00 0x0ae3c993 KEYUTILS_0.3
3 0x00 0x0ae3ca90 KEYUTILS_1.0
	KEYUTILS_0.3
4 0x00 0x0ae3ca93 KEYUTILS_1.3
	KEYUTILS_1.0
5 0x00 0x0ae3ca94 KEYUTILS_1.4
	KEYUTILS_1.3
6 0x00 0x0ae3ca95 KEYUTILS_1.5
	KEYUTILS_1.4
7 0x00 0x0ae3ca96 KEYUTILS_1.6
	KEYUTILS_1.5

Version References:
  required from libc.so.6:
    0x09691974 0x00 12 GLIBC_2.3.4
    0x0d696917 0x00 11 GLIBC_2.7
    0x06969194 0x00 10 GLIBC_2.14
    0x0d696914 0x00 09 GLIBC_2.4
    0x09691a75 0x00 08 GLIBC_2.2.5

Sections:
Idx Name          Size      VMA               LMA               File off  Algn
  0 .note.gnu.build-id 00000024  00000000000001c8  00000000000001c8  000001c8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  1 .gnu.hash     00000180  00000000000001f0  00000000000001f0  000001f0  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  2 .dynsym       00000678  0000000000000370  0000000000000370  00000370  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  3 .dynstr       00000455  00000000000009e8  00000000000009e8  000009e8  2**0
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  4 .gnu.version  0000008a  0000000000000e3e  0000000000000e3e  00000e3e  2**1
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  5 .gnu.version_d 000000ec  0000000000000ec8  0000000000000ec8  00000ec8  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  6 .gnu.version_r 00000060  0000000000000fb8  0000000000000fb8  00000fb8  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  7 .rela.dyn     00000378  0000000000001018  0000000000001018  00001018  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  8 .init         00000017  0000000000001390  0000000000001390  00001390  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
  9 .plt          00000010  00000000000013b0  00000000000013b0  000013b0  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 10 .plt.got      000000f0  00000000000013c0  00000000000013c0  000013c0  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 11 .text         00000cec  00000000000014b0  00000000000014b0  000014b0  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 12 .fini         00000009  000000000000219c  000000000000219c  0000219c  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 13 .rodata       000000a0  00000000000021b0  00000000000021b0  000021b0  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 14 .eh_frame_hdr 0000012c  0000000000002250  0000000000002250  00002250  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 15 .eh_frame     0000058c  0000000000002380  0000000000002380  00002380  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 16 .init_array   00000008  0000000000202cd0  0000000000202cd0  00002cd0  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 17 .fini_array   00000008  0000000000202cd8  0000000000202cd8  00002cd8  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 18 .data.rel.ro  00000008  0000000000202ce0  0000000000202ce0  00002ce0  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 19 .dynamic      000001f0  0000000000202ce8  0000000000202ce8  00002ce8  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 20 .got          00000128  0000000000202ed8  0000000000202ed8  00002ed8  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 21 .bss          00000008  0000000000203000  0000000000203000  00003000  2**0
                  ALLOC
 22 .gnu_debuglink 00000020  0000000000000000  0000000000000000  00003000  2**2
                  CONTENTS, READONLY
 23 .gnu_debugdata 00000414  0000000000000000  0000000000000000  00003020  2**0
                  CONTENTS, READONLY
SYMBOL TABLE:
no symbols
'''  # noqa

DUMP_FOUND_1 = '''

/lib/libkeyutils.so.1:     file format elf32-i386
/lib/libkeyutils.so.1
architecture: i386, flags 0x00000150:
HAS_SYMS, DYNAMIC, D_PAGED
start address 0x00000f80

Program Header:
    LOAD off    0x00000000 vaddr 0x00000000 paddr 0x00000000 align 2**12
         filesz 0x000028b4 memsz 0x000028b4 flags r-x
    LOAD off    0x00002e6c vaddr 0x00003e6c paddr 0x00003e6c align 2**12
         filesz 0x00000194 memsz 0x00000198 flags rw-
 DYNAMIC off    0x00002e78 vaddr 0x00003e78 paddr 0x00003e78 align 2**2
         filesz 0x000000f8 memsz 0x000000f8 flags rw-
    NOTE off    0x00000114 vaddr 0x00000114 paddr 0x00000114 align 2**2
         filesz 0x00000024 memsz 0x00000024 flags r--
EH_FRAME off    0x000021d8 vaddr 0x000021d8 paddr 0x000021d8 align 2**2
         filesz 0x00000134 memsz 0x00000134 flags r--
   STACK off    0x00000000 vaddr 0x00000000 paddr 0x00000000 align 2**4
         filesz 0x00000000 memsz 0x00000000 flags rw-
   RELRO off    0x00002e6c vaddr 0x00003e6c paddr 0x00003e6c align 2**0
         filesz 0x00000194 memsz 0x00000194 flags r--

Dynamic Section:
  NEEDED               libdl.so.2
  NEEDED               libc.so.6
  NEEDED               libsbr.so
  SONAME               libkeyutils.so.1
  INIT                 0x00000e54
  FINI                 0x00002134
  INIT_ARRAY           0x00003e6c
  INIT_ARRAYSZ         0x00000004
  FINI_ARRAY           0x00003e70
  FINI_ARRAYSZ         0x00000004
  GNU_HASH             0x00000138
  STRTAB               0x000006f8
  SYMTAB               0x000002b8
  STRSZ                0x00000457
  SYMENT               0x00000010
  PLTGOT               0x00003f70
  REL                  0x00000d34
  RELSZ                0x00000120
  RELENT               0x00000008
  VERDEF               0x00000bd8
  VERDEFNUM            0x00000007
  BIND_NOW             0x00000000
  FLAGS_1              0x00000001
  VERNEED              0x00000cc4
  VERNEEDNUM           0x00000001
  VERSYM               0x00000b50
  RELCOUNT             0x00000003

Version definitions:
1 0x01 0x02928561 libkeyutils.so.1
2 0x00 0x0ae3c993 KEYUTILS_0.3
3 0x00 0x0ae3ca90 KEYUTILS_1.0
	KEYUTILS_0.3
4 0x00 0x0ae3ca93 KEYUTILS_1.3
	KEYUTILS_1.0
5 0x00 0x0ae3ca94 KEYUTILS_1.4
	KEYUTILS_1.3
6 0x00 0x0ae3ca95 KEYUTILS_1.5
	KEYUTILS_1.4
7 0x00 0x0ae3ca96 KEYUTILS_1.6
	KEYUTILS_1.5

Version References:
  required from libc.so.6:
    0x09691974 0x00 13 GLIBC_2.3.4
    0x0d696917 0x00 12 GLIBC_2.7
    0x09691f73 0x00 11 GLIBC_2.1.3
    0x0d696914 0x00 10 GLIBC_2.4
    0x0d696911 0x00 09 GLIBC_2.1
    0x0d696910 0x00 08 GLIBC_2.0

Sections:
Idx Name          Size      VMA       LMA       File off  Algn
  0 .note.gnu.build-id 00000024  00000114  00000114  00000114  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  1 .gnu.hash     00000180  00000138  00000138  00000138  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  2 .dynsym       00000440  000002b8  000002b8  000002b8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  3 .dynstr       00000457  000006f8  000006f8  000006f8  2**0
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  4 .gnu.version  00000088  00000b50  00000b50  00000b50  2**1
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  5 .gnu.version_d 000000ec  00000bd8  00000bd8  00000bd8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  6 .gnu.version_r 00000070  00000cc4  00000cc4  00000cc4  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  7 .rel.dyn      00000120  00000d34  00000d34  00000d34  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  8 .init         00000023  00000e54  00000e54  00000e54  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
  9 .plt          00000010  00000e80  00000e80  00000e80  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 10 .plt.got      000000f0  00000e90  00000e90  00000e90  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 11 .text         000011b4  00000f80  00000f80  00000f80  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 12 .fini         00000014  00002134  00002134  00002134  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 13 .rodata       00000090  00002148  00002148  00002148  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 14 .eh_frame_hdr 00000134  000021d8  000021d8  000021d8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 15 .eh_frame     000005a8  0000230c  0000230c  0000230c  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 16 .init_array   00000004  00003e6c  00003e6c  00002e6c  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 17 .fini_array   00000004  00003e70  00003e70  00002e70  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 18 .data.rel.ro  00000004  00003e74  00003e74  00002e74  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 19 .dynamic      000000f8  00003e78  00003e78  00002e78  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 20 .got          00000090  00003f70  00003f70  00002f70  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 21 .bss          00000004  00004000  00004000  00003000  2**0
                  ALLOC
 22 .gnu_debuglink 00000020  00000000  00000000  00003000  2**2
                  CONTENTS, READONLY
 23 .gnu_debugdata 00000424  00000000  00000000  00003020  2**0
                  CONTENTS, READONLY
SYMBOL TABLE:
no symbols



/lib64/libkeyutils.so.1:     file format elf64-x86-64
/lib64/libkeyutils.so.1
architecture: i386:x86-64, flags 0x00000150:
HAS_SYMS, DYNAMIC, D_PAGED
start address 0x00000000000014b0

Program Header:
    LOAD off    0x0000000000000000 vaddr 0x0000000000000000 paddr 0x0000000000000000 align 2**21
         filesz 0x000000000000290c memsz 0x000000000000290c flags r-x
    LOAD off    0x0000000000002cd0 vaddr 0x0000000000202cd0 paddr 0x0000000000202cd0 align 2**21
         filesz 0x0000000000000330 memsz 0x0000000000000338 flags rw-
 DYNAMIC off    0x0000000000002ce8 vaddr 0x0000000000202ce8 paddr 0x0000000000202ce8 align 2**3
         filesz 0x00000000000001f0 memsz 0x00000000000001f0 flags rw-
    NOTE off    0x00000000000001c8 vaddr 0x00000000000001c8 paddr 0x00000000000001c8 align 2**2
         filesz 0x0000000000000024 memsz 0x0000000000000024 flags r--
EH_FRAME off    0x0000000000002250 vaddr 0x0000000000002250 paddr 0x0000000000002250 align 2**2
         filesz 0x000000000000012c memsz 0x000000000000012c flags r--
   STACK off    0x0000000000000000 vaddr 0x0000000000000000 paddr 0x0000000000000000 align 2**4
         filesz 0x0000000000000000 memsz 0x0000000000000000 flags rw-
   RELRO off    0x0000000000002cd0 vaddr 0x0000000000202cd0 paddr 0x0000000000202cd0 align 2**0
         filesz 0x0000000000000330 memsz 0x0000000000000330 flags r--

Dynamic Section:
  NEEDED               libdl.so.2
  NEEDED               libc.so.6
  SONAME               libkeyutils.so.1
  INIT                 0x0000000000001390
  FINI                 0x000000000000219c
  INIT_ARRAY           0x0000000000202cd0
  INIT_ARRAYSZ         0x0000000000000008
  FINI_ARRAY           0x0000000000202cd8
  FINI_ARRAYSZ         0x0000000000000008
  GNU_HASH             0x00000000000001f0
  STRTAB               0x00000000000009e8
  SYMTAB               0x0000000000000370
  STRSZ                0x0000000000000455
  SYMENT               0x0000000000000018
  PLTGOT               0x0000000000202ed8
  RELA                 0x0000000000001018
  RELASZ               0x0000000000000378
  RELAENT              0x0000000000000018
  VERDEF               0x0000000000000ec8
  VERDEFNUM            0x0000000000000007
  BIND_NOW             0x0000000000000000
  FLAGS_1              0x0000000000000001
  VERNEED              0x0000000000000fb8
  VERNEEDNUM           0x0000000000000001
  VERSYM               0x0000000000000e3e
  RELACOUNT            0x0000000000000003

Version definitions:
1 0x01 0x02928561 libkeyutils.so.1
2 0x00 0x0ae3c993 KEYUTILS_0.3
3 0x00 0x0ae3ca90 KEYUTILS_1.0
	KEYUTILS_0.3
4 0x00 0x0ae3ca93 KEYUTILS_1.3
	KEYUTILS_1.0
5 0x00 0x0ae3ca94 KEYUTILS_1.4
	KEYUTILS_1.3
6 0x00 0x0ae3ca95 KEYUTILS_1.5
	KEYUTILS_1.4
7 0x00 0x0ae3ca96 KEYUTILS_1.6
	KEYUTILS_1.5

Version References:
  required from libc.so.6:
    0x09691974 0x00 12 GLIBC_2.3.4
    0x0d696917 0x00 11 GLIBC_2.7
    0x06969194 0x00 10 GLIBC_2.14
    0x0d696914 0x00 09 GLIBC_2.4
    0x09691a75 0x00 08 GLIBC_2.2.5

Sections:
Idx Name          Size      VMA               LMA               File off  Algn
  0 .note.gnu.build-id 00000024  00000000000001c8  00000000000001c8  000001c8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  1 .gnu.hash     00000180  00000000000001f0  00000000000001f0  000001f0  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  2 .dynsym       00000678  0000000000000370  0000000000000370  00000370  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  3 .dynstr       00000455  00000000000009e8  00000000000009e8  000009e8  2**0
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  4 .gnu.version  0000008a  0000000000000e3e  0000000000000e3e  00000e3e  2**1
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  5 .gnu.version_d 000000ec  0000000000000ec8  0000000000000ec8  00000ec8  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  6 .gnu.version_r 00000060  0000000000000fb8  0000000000000fb8  00000fb8  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  7 .rela.dyn     00000378  0000000000001018  0000000000001018  00001018  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  8 .init         00000017  0000000000001390  0000000000001390  00001390  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
  9 .plt          00000010  00000000000013b0  00000000000013b0  000013b0  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 10 .plt.got      000000f0  00000000000013c0  00000000000013c0  000013c0  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 11 .text         00000cec  00000000000014b0  00000000000014b0  000014b0  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 12 .fini         00000009  000000000000219c  000000000000219c  0000219c  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 13 .rodata       000000a0  00000000000021b0  00000000000021b0  000021b0  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 14 .eh_frame_hdr 0000012c  0000000000002250  0000000000002250  00002250  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 15 .eh_frame     0000058c  0000000000002380  0000000000002380  00002380  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 16 .init_array   00000008  0000000000202cd0  0000000000202cd0  00002cd0  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 17 .fini_array   00000008  0000000000202cd8  0000000000202cd8  00002cd8  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 18 .data.rel.ro  00000008  0000000000202ce0  0000000000202ce0  00002ce0  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 19 .dynamic      000001f0  0000000000202ce8  0000000000202ce8  00002ce8  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 20 .got          00000128  0000000000202ed8  0000000000202ed8  00002ed8  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 21 .bss          00000008  0000000000203000  0000000000203000  00003000  2**0
                  ALLOC
 22 .gnu_debuglink 00000020  0000000000000000  0000000000000000  00003000  2**2
                  CONTENTS, READONLY
 23 .gnu_debugdata 00000414  0000000000000000  0000000000000000  00003020  2**0
                  CONTENTS, READONLY
SYMBOL TABLE:
no symbols
'''  # noqa

DUMP_FOUND_2 = '''

/lib/libkeyutils.so.1:     file format elf32-i386
/lib/libkeyutils.so.1
architecture: i386, flags 0x00000150:
HAS_SYMS, DYNAMIC, D_PAGED
start address 0x00000f80

Program Header:
    LOAD off    0x00000000 vaddr 0x00000000 paddr 0x00000000 align 2**12
         filesz 0x000028b4 memsz 0x000028b4 flags r-x
    LOAD off    0x00002e6c vaddr 0x00003e6c paddr 0x00003e6c align 2**12
         filesz 0x00000194 memsz 0x00000198 flags rw-
 DYNAMIC off    0x00002e78 vaddr 0x00003e78 paddr 0x00003e78 align 2**2
         filesz 0x000000f8 memsz 0x000000f8 flags rw-
    NOTE off    0x00000114 vaddr 0x00000114 paddr 0x00000114 align 2**2
         filesz 0x00000024 memsz 0x00000024 flags r--
EH_FRAME off    0x000021d8 vaddr 0x000021d8 paddr 0x000021d8 align 2**2
         filesz 0x00000134 memsz 0x00000134 flags r--
   STACK off    0x00000000 vaddr 0x00000000 paddr 0x00000000 align 2**4
         filesz 0x00000000 memsz 0x00000000 flags rw-
   RELRO off    0x00002e6c vaddr 0x00003e6c paddr 0x00003e6c align 2**0
         filesz 0x00000194 memsz 0x00000194 flags r--

Dynamic Section:
  NEEDED               libdl.so.2
  NEEDED               libc.so.6
  NEEDED               libsbr.so
  SONAME               libkeyutils.so.1
  INIT                 0x00000e54
  FINI                 0x00002134
  INIT_ARRAY           0x00003e6c
  INIT_ARRAYSZ         0x00000004
  FINI_ARRAY           0x00003e70
  FINI_ARRAYSZ         0x00000004
  GNU_HASH             0x00000138
  STRTAB               0x000006f8
  SYMTAB               0x000002b8
  STRSZ                0x00000457
  SYMENT               0x00000010
  PLTGOT               0x00003f70
  REL                  0x00000d34
  RELSZ                0x00000120
  RELENT               0x00000008
  VERDEF               0x00000bd8
  VERDEFNUM            0x00000007
  BIND_NOW             0x00000000
  FLAGS_1              0x00000001
  VERNEED              0x00000cc4
  VERNEEDNUM           0x00000001
  VERSYM               0x00000b50
  RELCOUNT             0x00000003

Version definitions:
1 0x01 0x02928561 libkeyutils.so.1
2 0x00 0x0ae3c993 KEYUTILS_0.3
3 0x00 0x0ae3ca90 KEYUTILS_1.0
	KEYUTILS_0.3
4 0x00 0x0ae3ca93 KEYUTILS_1.3
	KEYUTILS_1.0
5 0x00 0x0ae3ca94 KEYUTILS_1.4
	KEYUTILS_1.3
6 0x00 0x0ae3ca95 KEYUTILS_1.5
	KEYUTILS_1.4
7 0x00 0x0ae3ca96 KEYUTILS_1.6
	KEYUTILS_1.5

Version References:
  required from libc.so.6:
    0x09691974 0x00 13 GLIBC_2.3.4
    0x0d696917 0x00 12 GLIBC_2.7
    0x09691f73 0x00 11 GLIBC_2.1.3
    0x0d696914 0x00 10 GLIBC_2.4
    0x0d696911 0x00 09 GLIBC_2.1
    0x0d696910 0x00 08 GLIBC_2.0

Sections:
Idx Name          Size      VMA       LMA       File off  Algn
  0 .note.gnu.build-id 00000024  00000114  00000114  00000114  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  1 .gnu.hash     00000180  00000138  00000138  00000138  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  2 .dynsym       00000440  000002b8  000002b8  000002b8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  3 .dynstr       00000457  000006f8  000006f8  000006f8  2**0
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  4 .gnu.version  00000088  00000b50  00000b50  00000b50  2**1
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  5 .gnu.version_d 000000ec  00000bd8  00000bd8  00000bd8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  6 .gnu.version_r 00000070  00000cc4  00000cc4  00000cc4  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  7 .rel.dyn      00000120  00000d34  00000d34  00000d34  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  8 .init         00000023  00000e54  00000e54  00000e54  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
  9 .plt          00000010  00000e80  00000e80  00000e80  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 10 .plt.got      000000f0  00000e90  00000e90  00000e90  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 11 .text         000011b4  00000f80  00000f80  00000f80  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 12 .fini         00000014  00002134  00002134  00002134  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 13 .rodata       00000090  00002148  00002148  00002148  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 14 .eh_frame_hdr 00000134  000021d8  000021d8  000021d8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 15 .eh_frame     000005a8  0000230c  0000230c  0000230c  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 16 .init_array   00000004  00003e6c  00003e6c  00002e6c  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 17 .fini_array   00000004  00003e70  00003e70  00002e70  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 18 .data.rel.ro  00000004  00003e74  00003e74  00002e74  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 19 .dynamic      000000f8  00003e78  00003e78  00002e78  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 20 .got          00000090  00003f70  00003f70  00002f70  2**2
                  CONTENTS, ALLOC, LOAD, DATA
 21 .bss          00000004  00004000  00004000  00003000  2**0
                  ALLOC
 22 .gnu_debuglink 00000020  00000000  00000000  00003000  2**2
                  CONTENTS, READONLY
 23 .gnu_debugdata 00000424  00000000  00000000  00003020  2**0
                  CONTENTS, READONLY
SYMBOL TABLE:
no symbols



/lib64/libkeyutils.so.1:     file format elf64-x86-64
/lib64/libkeyutils.so.1
architecture: i386:x86-64, flags 0x00000150:
HAS_SYMS, DYNAMIC, D_PAGED
start address 0x00000000000014b0

Program Header:
    LOAD off    0x0000000000000000 vaddr 0x0000000000000000 paddr 0x0000000000000000 align 2**21
         filesz 0x000000000000290c memsz 0x000000000000290c flags r-x
    LOAD off    0x0000000000002cd0 vaddr 0x0000000000202cd0 paddr 0x0000000000202cd0 align 2**21
         filesz 0x0000000000000330 memsz 0x0000000000000338 flags rw-
 DYNAMIC off    0x0000000000002ce8 vaddr 0x0000000000202ce8 paddr 0x0000000000202ce8 align 2**3
         filesz 0x00000000000001f0 memsz 0x00000000000001f0 flags rw-
    NOTE off    0x00000000000001c8 vaddr 0x00000000000001c8 paddr 0x00000000000001c8 align 2**2
         filesz 0x0000000000000024 memsz 0x0000000000000024 flags r--
EH_FRAME off    0x0000000000002250 vaddr 0x0000000000002250 paddr 0x0000000000002250 align 2**2
         filesz 0x000000000000012c memsz 0x000000000000012c flags r--
   STACK off    0x0000000000000000 vaddr 0x0000000000000000 paddr 0x0000000000000000 align 2**4
         filesz 0x0000000000000000 memsz 0x0000000000000000 flags rw-
   RELRO off    0x0000000000002cd0 vaddr 0x0000000000202cd0 paddr 0x0000000000202cd0 align 2**0
         filesz 0x0000000000000330 memsz 0x0000000000000330 flags r--

Dynamic Section:
  NEEDED               libdl.so.2
  NEEDED               libsbr.so.6
  NEEDED               libfake.so
  SONAME               libkeyutils.so.1
  INIT                 0x0000000000001390
  FINI                 0x000000000000219c
  INIT_ARRAY           0x0000000000202cd0
  INIT_ARRAYSZ         0x0000000000000008
  FINI_ARRAY           0x0000000000202cd8
  FINI_ARRAYSZ         0x0000000000000008
  GNU_HASH             0x00000000000001f0
  STRTAB               0x00000000000009e8
  SYMTAB               0x0000000000000370
  STRSZ                0x0000000000000455
  SYMENT               0x0000000000000018
  PLTGOT               0x0000000000202ed8
  RELA                 0x0000000000001018
  RELASZ               0x0000000000000378
  RELAENT              0x0000000000000018
  VERDEF               0x0000000000000ec8
  VERDEFNUM            0x0000000000000007
  BIND_NOW             0x0000000000000000
  FLAGS_1              0x0000000000000001
  VERNEED              0x0000000000000fb8
  VERNEEDNUM           0x0000000000000001
  VERSYM               0x0000000000000e3e
  RELACOUNT            0x0000000000000003

Version definitions:
1 0x01 0x02928561 libkeyutils.so.1
2 0x00 0x0ae3c993 KEYUTILS_0.3
3 0x00 0x0ae3ca90 KEYUTILS_1.0
	KEYUTILS_0.3
4 0x00 0x0ae3ca93 KEYUTILS_1.3
	KEYUTILS_1.0
5 0x00 0x0ae3ca94 KEYUTILS_1.4
	KEYUTILS_1.3
6 0x00 0x0ae3ca95 KEYUTILS_1.5
	KEYUTILS_1.4
7 0x00 0x0ae3ca96 KEYUTILS_1.6
	KEYUTILS_1.5

Version References:
  required from libc.so.6:
    0x09691974 0x00 12 GLIBC_2.3.4
    0x0d696917 0x00 11 GLIBC_2.7
    0x06969194 0x00 10 GLIBC_2.14
    0x0d696914 0x00 09 GLIBC_2.4
    0x09691a75 0x00 08 GLIBC_2.2.5

Sections:
Idx Name          Size      VMA               LMA               File off  Algn
  0 .note.gnu.build-id 00000024  00000000000001c8  00000000000001c8  000001c8  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  1 .gnu.hash     00000180  00000000000001f0  00000000000001f0  000001f0  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  2 .dynsym       00000678  0000000000000370  0000000000000370  00000370  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  3 .dynstr       00000455  00000000000009e8  00000000000009e8  000009e8  2**0
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  4 .gnu.version  0000008a  0000000000000e3e  0000000000000e3e  00000e3e  2**1
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  5 .gnu.version_d 000000ec  0000000000000ec8  0000000000000ec8  00000ec8  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  6 .gnu.version_r 00000060  0000000000000fb8  0000000000000fb8  00000fb8  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  7 .rela.dyn     00000378  0000000000001018  0000000000001018  00001018  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
  8 .init         00000017  0000000000001390  0000000000001390  00001390  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
  9 .plt          00000010  00000000000013b0  00000000000013b0  000013b0  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 10 .plt.got      000000f0  00000000000013c0  00000000000013c0  000013c0  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 11 .text         00000cec  00000000000014b0  00000000000014b0  000014b0  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 12 .fini         00000009  000000000000219c  000000000000219c  0000219c  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
 13 .rodata       000000a0  00000000000021b0  00000000000021b0  000021b0  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 14 .eh_frame_hdr 0000012c  0000000000002250  0000000000002250  00002250  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 15 .eh_frame     0000058c  0000000000002380  0000000000002380  00002380  2**3
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
 16 .init_array   00000008  0000000000202cd0  0000000000202cd0  00002cd0  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 17 .fini_array   00000008  0000000000202cd8  0000000000202cd8  00002cd8  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 18 .data.rel.ro  00000008  0000000000202ce0  0000000000202ce0  00002ce0  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 19 .dynamic      000001f0  0000000000202ce8  0000000000202ce8  00002ce8  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 20 .got          00000128  0000000000202ed8  0000000000202ed8  00002ed8  2**3
                  CONTENTS, ALLOC, LOAD, DATA
 21 .bss          00000008  0000000000203000  0000000000203000  00003000  2**0
                  ALLOC
 22 .gnu_debuglink 00000020  0000000000000000  0000000000000000  00003000  2**2
                  CONTENTS, READONLY
 23 .gnu_debugdata 00000414  0000000000000000  0000000000000000  00003020  2**0
                  CONTENTS, READONLY
SYMBOL TABLE:
no symbols
'''  # noqa


def test_libkeyutils():
    libkeyutils_search = Libkeyutils(context_wrap(SEARCH_NOT_FOUND))
    assert libkeyutils_search.libraries == SEARCH_NOT_FOUND.strip().split('\n')

    libkeyutils_search = Libkeyutils(context_wrap(SEARCH_FOUND_1))
    assert libkeyutils_search.libraries == SEARCH_FOUND_1.strip().split('\n')

    libkeyutils_search = Libkeyutils(context_wrap(SEARCH_FOUND_2))
    assert libkeyutils_search.libraries == SEARCH_FOUND_2.strip().split('\n')


def test_libkeyutilsobjdumps():
    libkeyutils_dumps = LibkeyutilsObjdumps(context_wrap(DUMP_NOT_FOUND))
    assert len(libkeyutils_dumps.linked_libraries) == 2
    assert libkeyutils_dumps.linked_libraries == {'/lib/libkeyutils.so.1':
                                                  ['libdl.so.2', 'libc.so.6'],
                                                  '/lib64/libkeyutils.so.1':
                                                  ['libdl.so.2', 'libc.so.6'],
                                                  }

    libkeyutils_dumps = LibkeyutilsObjdumps(context_wrap(DUMP_FOUND_1))
    assert len(libkeyutils_dumps.linked_libraries) == 2
    assert libkeyutils_dumps.linked_libraries == {'/lib/libkeyutils.so.1':
                                                  ['libdl.so.2', 'libc.so.6', 'libsbr.so'],
                                                  '/lib64/libkeyutils.so.1':
                                                  ['libdl.so.2', 'libc.so.6'],
                                                  }

    libkeyutils_dumps = LibkeyutilsObjdumps(context_wrap(DUMP_FOUND_2))
    assert len(libkeyutils_dumps.linked_libraries) == 2
    assert libkeyutils_dumps.linked_libraries == {'/lib/libkeyutils.so.1':
                                                  ['libdl.so.2', 'libc.so.6', 'libsbr.so'],
                                                  '/lib64/libkeyutils.so.1':
                                                  ['libdl.so.2', 'libsbr.so.6', 'libfake.so'],
                                                  }
