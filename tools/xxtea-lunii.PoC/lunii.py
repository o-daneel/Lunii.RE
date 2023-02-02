import glob
import pathlib

import xxtea
import os
import binascii
import click


def vectkey_to_bytes(key_vect):
    joined = [k.to_bytes(4, 'little') for k in key_vect]
    return b''.join(joined)


# external flash hardcoded value
# 91BD7A0A A75440A9 BBD49D6C E0DCC0E3
raw_key_generic = [0x91BD7A0A, 0xA75440A9, 0xBBD49D6C, 0xE0DCC0E3]
lunii_generic_key = vectkey_to_bytes(raw_key_generic)

# internal flash contents
# AABBCCDD AABBCCDD AABBCCDD AABBCCDD
# reordered
# AABBCCDD AABBCCDD AABBCCDD AABBCCDD
raw_key_device = [0xAABBCCDD, 0xAABBCCDD, 0xAABBCCDD, 0xAABBCCDD]
lunii_device_key = vectkey_to_bytes(raw_key_device)

# lunii_hexkey = b'AABBCCDDAABBCCDDAABBCCDDAABBCCDD'
# lunii_keyB = binascii.unhexlify(lunii_hexkey)


def sample_code():
    print(f"Key : {binascii.hexlify(lunii_generic_key)}")

    s = b"xxtea is good"

    enc = xxtea.encrypt(s, lunii_generic_key)
    dec = xxtea.decrypt(enc, lunii_generic_key)
    print(s)
    print(enc)
    print(dec)

    hexenc = xxtea.encrypt_hex(s, lunii_generic_key)
    hexdec = xxtea.decrypt_hex(hexenc, lunii_generic_key)
    print(s)
    print(hexenc)
    print(hexdec)


def sample_file():
    print("hello")

    with open("../../dump/1362862A/rf/000/0ACBC5FB", "rb") as fp:
        ciphered = fp.read(0x200)
        print(len(ciphered))
        print(ciphered)
        ciph_hex = binascii.hexlify(ciphered)

        print(ciph_hex)
        dec = xxtea.decrypt(ciphered, lunii_generic_key, padding=False, rounds=1)
        hexdec = binascii.hexlify(dec)
        print(dec)
        print(hexdec)


def untea_file(key, filename, extension):
    if pathlib.Path(filename).is_dir():
        return

    with open(filename, "rb") as fp:
        # processing first block
        ciphered = fp.read(0x200)
        if len(ciphered) == 0:
            return

        print(f"Processing {filename}", end="")

        with open(fp.name + extension, "wb") as bmp_file:
            dec = xxtea.decrypt(ciphered, key, padding=False, rounds=1)
            bmp_file.write(dec)

            # if anything left, copy
            plain = fp.read()
            bmp_file.write(plain)
    print(f" as {filename}{extension}")


def untea_dir(key, dirname, extension):
    res_list = glob.glob(dirname + "*")
    res_list = [item for item in res_list if os.path.splitext(item)[1] == ""]
    print(res_list)

    for file in res_list:
        untea_file(key, file, extension)


def untea_story():
    untea_dir(lunii_generic_key, "../../dump/1362862A/rf/000/", ".bmp")
    untea_dir(lunii_generic_key, "../../dump/1362862A/sf/000/", ".mp3")
    untea_dir(lunii_generic_key, "../../dump/1362862A/", ".bin")
    # untea_file(lunii_generic_key, "../../dump/root_sd/.md_p2", ".bin")
    # untea_file(lunii_device_key, "../../dump/1362862A/bt_p1", ".bin")


if __name__ == '__main__':
    untea_story()