- [TL;DR](#tldr)
  - [Wrong algorithm](#wrong-algorithm)
  - [Key vs Keys ?](#key-vs-keys-)
- [Keys initialization](#keys-initialization)
- [Target function](#target-function)
  - [Ghidra decompiled](#ghidra-decompiled)
  - [IDA Pro decompiled](#ida-pro-decompiled)
- [How to reverse](#how-to-reverse)
  - [Official version : XXTEA](#official-version--xxtea)


# TL;DR
**Ciphering is finally DEFEATED...**  

My bad assumptions 
## Wrong algorithm
I was hoping that TEA algorithm will be easy to reuse. But it does not work.    I finally found the reason. It exists two variants, XTEA and TEAB.
   * [XTEA](https://en.wikipedia.org/wiki/XTEA) stands for Extended TEA
   * [XXTEA or TEAB](https://en.wikipedia.org/wiki/XXTEA) stands for Corrected Block  TEA

Lunii relies on `XXTEA` algorithm, and I guess that for performances reasons (I can"t figure any other rationale for the following choices), they decided to limit ciphering to first 0x200 Bytes (512B, one sector maybe), and fine tune the algo to only **one** round. That makes the algorithm weaker to attacks, but faster..

## Key vs Keys ?
I was expecting only one key, however during decompiling process, I realized that two keys are used.   
The first one is hardcoded in binary.
* Key A (**Generic Key**) is made from 0x90013324 value   
  ```
  K[0]    91BD7A0A
  K[1]    91BD7A0A + 0x1596c69f = A75440A9
  K[2]    91BD7A0A + 0x2a172362 = BBD49D6C
  K[3]    E0DCC0E3
  Key_A = 91BD7A0A A75440A9 BBD49D6C E0DCC0E3
  ```
  This code is available in event_loop at 0x90013200


* Key B (**Device specific**) is made from reading internal flash @SNU location, and deciphering SNU+0x08 to SNU+0x88. Key B is the first 0x10 Bytes of this unciphered buffer, and reordered 
  ```
  K[0] = fread_buffer[16];
  K[1] = fread_buffer[20];
  K[2] = fread_buffer[8]
  K[3] = fread_buffer[12];
  ```

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
void __cdecl crypto_tea_decipher(int *buffer, int size)
{
  unsigned int sum; // r5@2
  unsigned int cur_block; // lr@2
  int nb_pairs; // r3@2
  signed int pairs_left; // r12@3
  unsigned int current_pair; // r4@3
  int v7; // r6@4
  unsigned int v8; // r7@4
  int v9; // r8@4
  int v10; // r9@4
  unsigned int v11; // r4@5
  unsigned int v12; // r3@7
  int nb_rounds; // [sp+0h] [bp-38h]@2
  unsigned int k2; // [sp+4h] [bp-34h]@2
  unsigned int k1; // [sp+8h] [bp-30h]@2

  if ( CRYPTO_TEA_ENABLE )
  {
    nb_rounds = 52 / (signed int)((unsigned int)size >> 1) + 1;
    sum = 0x9E3779B9 * nb_rounds;
    cur_block = *buffer;
    nb_pairs = 2 * (size - 0x80000001);
    k2 = (unsigned int)buffer + nb_pairs;
    k1 = (unsigned int)buffer + nb_pairs - 2;
    do
    {
      pairs_left = size - 1;
      for ( current_pair = (unsigned int)buffer + 2 * size; ; current_pair -= 4 )
      {
        v7 = 4 * cur_block;
        v8 = cur_block >> 3;
        v9 = cur_block ^ sum;
        v10 = CRYPTO_TEA_KEY_loaded[((unsigned __int8)(sum >> 2) ^ (unsigned __int8)(pairs_left >> 1)) & 3];
        if ( pairs_left <= 1 )
          break;
        pairs_left -= 2;
        v12 = *(_WORD *)(current_pair - 8) | (*(_WORD *)(current_pair - 6) << 16);
        cur_block = (*(_WORD *)(current_pair - 4) | (*(_WORD *)(current_pair - 2) << 16))
                  - (((v7 ^ (v12 >> 5)) + (v8 ^ 16 * v12)) ^ ((v12 ^ v10) + v9));
        *(_WORD *)(current_pair - 2) = HIWORD(cur_block);
        *(_WORD *)(current_pair - 4) = cur_block;
      }
      sum += -0x9E3779B9;
      v11 = *(_WORD *)k1 | (*(_WORD *)k2 << 16);
      cur_block = *buffer - (((v7 ^ (v11 >> 5)) + (v8 ^ 16 * v11)) ^ (v9 + (v11 ^ v10)));
      *(_WORD *)buffer = cur_block;
      *((_WORD *)buffer + 1) = HIWORD(cur_block);
      --nb_rounds;
    }
    while ( nb_rounds );
  }
}
```

# How to reverse

Thanks to Ghidra [FindCrypt](https://github.com/TorgoTorgo/ghidra-findcrypt), I have been able to get a name on the constant `0x9E3779B9` I previously found.   
It is referenced in Symbol Table as : **Crypt constant TEA_DELTA - 4 bytes**

A quick search on Google lead to :  
https://en.wikipedia.org/wiki/Tiny_Encryption_Algorithm

**Et voilà !**   

After many testings, TEA algorithm is not the one used.    
They might have modified somehow the processing --> NOOOOO    
It is just a different variant of TEA, like   
https://en.wikipedia.org/wiki/XXTEA


**Et voilà !** This time XXTEA sample code from Wikipedia look very close to decompiled version from Ghidra/IDA.


In order to verify if decipher is ok, I had to check against a file. I picked a randon resource from `sd:0:\.content\XXXXXXXX\rf\000` (supposely a ciphered BITMAP).
After few tries, I have been able to get a BITMAP header after deciphering.
``` 
PS C:\Work\reverse\Lunii.RE\tools\tea-c> .\lunii.exe

> 00000000 : 42 4D FA 10 00 00 00 00 00 00 76 00 00 00 28 00 00 00 40 01 00 00 F0 00 00 00 01 00 04 00 02 00
> 00000020 : 00 00 84 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 00 00 00 00 00 FF FF FF FF FF 10 10
```

## Official version : XXTEA

```C
#include <stdint.h>
#define DELTA 0x9e3779b9
#define MX (((z>>5^y<<2) + (y>>3^z<<4)) ^ ((sum^y) + (key[(p&3)^e] ^ z)))

void btea(uint32_t *v, int n, uint32_t const key[4]) {
	uint32_t y, z, sum;
	unsigned p, rounds, e;
    
    /* Coding Part */
    if (n > 1) {
        rounds = 6 + 52/n;
        sum = 0;
        z = v[n-1];
        do {
            sum += DELTA;
            e = (sum >> 2) & 3;
            for (p=0; p<n-1; p++) {
                y = v[p+1]; 
                z = v[p] += MX;
            }
            y = v[0];
            z = v[n-1] += MX;
        } while (--rounds);
    }
 
    /* Decoding Part */
    else if (n < -1) {
        n = -n;
        rounds = 6 + 52/n;
        sum = rounds*DELTA;
        y = v[0];
        do {
            e = (sum >> 2) & 3;
            for (p=n-1; p>0; p--) {
                z = v[p-1];
                y = v[p] -= MX;
            }
            z = v[n-1];
            y = v[0] -= MX;
            sum -= DELTA;
        } while (--rounds);
    }
}
```

