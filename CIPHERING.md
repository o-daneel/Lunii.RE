- [TL;DR](#tldr)
- [Keys initialization](#keys-initialization)
- [Target function](#target-function)
  - [Ghidra decompiled](#ghidra-decompiled)
  - [IDA Pro decompiled](#ida-pro-decompiled)
- [How to reverse](#how-to-reverse)
  - [Official version](#official-version)


# TL;DR
My bad, I was expecting only one key, however during decompiling process, I realized that two keys are used.   
A first one is hardcoded in binary

.md file might be the one that contains everything about the box. Key B and SNU ?

* Key A is made from 0x90013324 value   
  ```
  K[0]    91BD7A0A
  K[1]    91BD7A0A + 0x1596c69f = A75440A9
  K[2]    91BD7A0A + 0x2a172362 = BBD49D6C
  K[3]    E0DCC0E3
  Key_A = 91BD7A0A A75440A9 BBD49D6C E0DCC0E3
  ```
  This code is available in event_loop at 0x90013200

* <s>Key B is make of deciphering .md file from 0x08 to 0x18.   
  Those four **UINT** make Key_B[0] Key_B[1] Key_B[2] Key_B[3]

  The section from 0x08 to 0x18 is made of
  * 2 Bytes : 0x1600
  * 8 Bytes : SNU
  * 4 Bytes : 83 04 41 A3 (static)
  * 2 Bytes : NS (static)
  
  Thus Key_B is made of SNU & Key_A</s>
* Key B is made from reading internal flash @SNU location, and deciphering SNU+0x08 to SNU+0x18 

# Keys initialization
Here is the chunk of code that initialize the Keys   
``` C
// Located @900131f4
    FUN_9001245c();
    read_.md();
    CRYPTO_TEA_KEY_A[0] = 0x91bd7a0a;
    CRYPTO_TEA_KEY_A[1] = 0xa75440a9;
    CRYPTO_TEA_KEY_A[2] = 0xbbd49d6c;
    CRYPTO_TEA_KEY_A[3] = 0xe0dcc0e3;
    HAL_snu_to_buffer(fread_buffer,0x200);
    crypto_tea_deciph_enable(true);
    crypto_tea_load_key(CRYPTO_TEA_KEY_A);
    to_exit = false;
    crypto_tea_decipher(fread_buffer + 8,0x80);
    CRYPTO_TEA_KEY_B[0] = fread_buffer._16_4_;
    CRYPTO_TEA_KEY_B[1] = fread_buffer._20_4_;
    CRYPTO_TEA_KEY_B[2] = fread_buffer._8_4_;
    CRYPTO_TEA_KEY_B[3] = fread_buffer._12_4_;
```

# Target function
```
crypto_decipher                       0x9000eb34    Function    Global  User Defined    2   0
```

## Ghidra decompiled
``` C
// Located @9000eb34
byte * crypto_tea_decipher(byte *buffer,uint key_offset)
{
  uint uVar1;
  int iVar2;
  uint *key;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  int local_38;
  
  if (CRYPTO_TEA_ENABLE != 0) {
    local_38 = 0x34 / (key_offset >> 1) + 1;
    uVar4 = local_38 * 0x9e3779b9;
    uVar8 = *(uint *)buffer;
    iVar2 = (key_offset + 0x7fffffff) * 2;
    do {
      uVar6 = uVar4 >> 2;
      iVar7 = key_offset - 1;
      key = (uint *)(buffer + key_offset * 2);
      while( true ) {
        uVar1 = iVar7 >> 1;
        uVar5 = uVar8 ^ uVar4;
        if (iVar7 < 2) break;
        iVar7 = iVar7 + -2;
        uVar3 = key[-2];
        uVar8 = key[-1] - ((uVar8 << 2 ^ uVar3 >> 5) + (uVar8 >> 3 ^ uVar3 << 4) ^
                          (uVar3 ^ CRYPTO_TEA_KEY_loaded[(uVar6 ^ uVar1) & 3]) + uVar5);
        key = key + -1;
        *key = uVar8;
      }
      uVar4 = uVar4 + 0x61c88647;
      uVar3 = CONCAT22(*(undefined2 *)(buffer + iVar2),*(undefined2 *)(buffer + iVar2 + -2));
      uVar8 = *(int *)buffer -
              ((uVar8 << 2 ^ uVar3 >> 5) + (uVar8 >> 3 ^ uVar3 << 4) ^
              uVar5 + (uVar3 ^ CRYPTO_TEA_KEY_loaded[(uVar6 ^ uVar1) & 3]));
      *(uint *)buffer = uVar8;
      local_38 = local_38 + -1;
    } while (local_38 != 0);
    return buffer;
  }
  return buffer;
}
```

## IDA Pro decompiled
``` C
char *__cdecl crypto_decipher(char *buffer, int offset)
{
  unsigned int v2; // r5@2
  unsigned int cur_block; // lr@2
  int v4; // r3@2
  signed int v5; // r12@3
  char *i; // r4@3
  int v7; // r6@4
  unsigned int v8; // r7@4
  int v9; // r8@4
  int v10; // r9@4
  unsigned int v11; // r4@5
  unsigned int v12; // r3@7
  int nb_block; // [sp+0h] [bp-38h]@2
  char *v14; // [sp+4h] [bp-34h]@2
  char *v15; // [sp+8h] [bp-30h]@2

  if ( word_200115A0 )
  {
    nb_block = 52 / (signed int)((unsigned int)offset >> 1) + 1;
    v2 = 0x9E3779B9 * nb_block;
    cur_block = *(_DWORD *)buffer;
    v4 = 2 * (offset + 0x7FFFFFFF);
    v14 = &buffer[v4];
    v15 = &buffer[v4 - 2];
    do
    {
      v5 = offset - 1;
      for ( i = &buffer[2 * offset]; ; i -= 4 )
      {
        v7 = 4 * cur_block;
        v8 = cur_block >> 3;
        v9 = cur_block ^ v2;
        v10 = dword_200115A4[((unsigned __int8)(v2 >> 2) ^ (unsigned __int8)(v5 >> 1)) & 3];
        if ( v5 <= 1 )
          break;
        v5 -= 2;
        v12 = *((_WORD *)i - 4) | (*((_WORD *)i - 3) << 16);
        cur_block = (*((_WORD *)i - 2) | (*((_WORD *)i - 1) << 16))
                  - (((v7 ^ (v12 >> 5)) + (v8 ^ 16 * v12)) ^ ((v12 ^ v10) + v9));
        *((_WORD *)i - 1) = HIWORD(cur_block);
        *((_WORD *)i - 2) = cur_block;
      }
      v2 += 0x61C88647;
      v11 = *(_WORD *)v15 | (*(_WORD *)v14 << 16);
      cur_block = *(_DWORD *)buffer - (((v7 ^ (v11 >> 5)) + (v8 ^ 16 * v11)) ^ (v9 + (v11 ^ v10)));
      *(_WORD *)buffer = cur_block;
      *((_WORD *)buffer + 1) = HIWORD(cur_block);
      --nb_block;
    }
    while ( nb_block );
  }
  return buffer;
}
```

# How to reverse

Thanks to Ghidra [FindCrypt](https://github.com/TorgoTorgo/ghidra-findcrypt), I have been able to get a name on the constant `0x9E3779B9` I previously found.   
It is referenced in Symbol Table as : **Crypt constant TEA_DELTA - 4 bytes**

A quick search on Google lead to :  
https://en.wikipedia.org/wiki/Tiny_Encryption_Algorithm

Et voilà !

## Official version 

```C
void encrypt (uint32_t v[2], const uint32_t k[4]) {
    uint32_t v0=v[0], v1=v[1], sum=0, i;           /* set up */
    uint32_t delta=0x9E3779B9;                     /* a key schedule constant */
    uint32_t k0=k[0], k1=k[1], k2=k[2], k3=k[3];   /* cache key */
    for (i=0; i<32; i++) {                         /* basic cycle start */
        sum += delta;
        v0 += ((v1<<4) + k0) ^ (v1 + sum) ^ ((v1>>5) + k1);
        v1 += ((v0<<4) + k2) ^ (v0 + sum) ^ ((v0>>5) + k3);
    }                                              /* end cycle */
    v[0]=v0; v[1]=v1;
}

void decrypt (uint32_t v[2], const uint32_t k[4]) {
    uint32_t v0=v[0], v1=v[1], sum=0xC6EF3720, i;  /* set up; sum is (delta << 5) & 0xFFFFFFFF */
    uint32_t delta=0x9E3779B9;                     /* a key schedule constant */
    uint32_t k0=k[0], k1=k[1], k2=k[2], k3=k[3];   /* cache key */
    for (i=0; i<32; i++) {                         /* basic cycle start */
        v1 -= ((v0<<4) + k2) ^ (v0 + sum) ^ ((v0>>5) + k3);
        v0 -= ((v1<<4) + k0) ^ (v1 + sum) ^ ((v1>>5) + k1);
        sum -= delta;
    }                                              /* end cycle */
    v[0]=v0; v[1]=v1;
}
```

