# Summary
- [Summary](#summary)
  - [Mapping](#mapping)
- [Memory layout](#memory-layout)
  - [Bootloader Firmware](#bootloader-firmware)
  - [Main Firmware](#main-firmware)
  - [Backup firmware](#backup-firmware)
  - [SNU location](#snu-location)
- [Security study](#security-study)
  - [Ghidra Project](#ghidra-project)
    - [How to import](#how-to-import)
  - [Thoughts](#thoughts)
    - [Firmware CRC](#firmware-crc)
    - [Custom firmware](#custom-firmware)
      - [Boot procedure](#boot-procedure)
    - [NFC chip](#nfc-chip)
    - [Finding SD Ciphering](#finding-sd-ciphering)
- [Crypt-Analysis](#crypt-analysis)
- [Symbols](#symbols)
- [Resources](#resources)
  - [SD structure \& Files](#sd-structure--files)
  - [Bitmaps](#bitmaps)
- [Links](#links)


## Mapping
* GPIOE - display ?
* GPIOB - audio chip ?

# Memory layout
<img src="resources/mem_map.png" width="400">

Three of them are of interest:
1. QuadSPI external flash from `0x8000 0000 - 0x9FFF FFFF`   
   512KB are split in two 256KB parts. One for current firmware, and another for backup.
2. Internal flash from `0x0800 0000 - 0x0800 FFFF`
3. Internal RAM from `0x2000 0000 - 0x2003 FFFF`

## Bootloader Firmware
TBD : boot process & steps + jump to main at `0x9000 0000`

1. checks CRC of main firmware
2. in case firmware is corrupted, copy backup firmware to main
3. boot main firmware

## Main Firmware
The full firmware ! might be located at `0x9000 0000`   
**Version =** 2.22

## Backup firmware
A short mini firmware ! might be located at `0x8000 0000`   
**Version =** 2.16

## SNU location

8 bytes for SNU located at : `0x0800 C000 - 0x0800 C007` (internal flash)

# Security study

## Ghidra Project

You will find Ghidra archive in this repo. These archives contains all the work performed on understanding, renaming, decompiling the Lunii Firmware.

Thanks to the following tools:
* https://securelist.com/how-to-train-your-ghidra/108272/
* https://github.com/leveldown-security/SVD-Loader-Ghidra   
  https://raw.githubusercontent.com/posborne/cmsis-svd/master/data/STMicro/STM32F7x3.svd
* https://github.com/TorgoTorgo/ghidra-findcrypt
* ...
### How to import
1. Open Ghidra
2. Ensure that there is no active project
3. File / Restore Project
4. Pick `...something.../Lunii.RE/ghidra/Lunii_2023_MM_DD.gar` in Archive File
5. **Restore Directory** & **Project Name** must be filled automatically with
   * `...something.../Lunii.RE/ghidra`
   * `Lunii`


## Thoughts

### Firmware CRC
1. compute fw size by looking for FFFF partern
2. computes CRC32 on size - 4 (reference CRC included at the end)

### Custom firmware
* build the firmware archive
  * when is the SNU inserted ?
* to output internal values ?
* to decipher files on uart ?

Firmware archive seems to be named as :  
`boot.bin @08006294 : fa.bin`   
Firmware update seems to be a simple file starting from vectors, ending after expected CRC

#### Boot procedure
1. check for USB power source connected   
   Otherwise upgrade process is skipped
2. Looks for `fa.bin` file
3. Check internal CRC
4. Write to Main FW memory segment
5. jump to Main FW

You can retrieve this execution flow in ghidra here :   `boot.bin @08005f04`   


### NFC chip
* Match TBD dump against frame build in Main FW

### Finding SD Ciphering
There are two functions that performs the same action but from different source :
* `HAL_SCR_displayPicture_fromBuffer` (from a bitmap read in firmware, as identified in this section [Bitmaps](#bitmaps))
* `HAL_SCR_displayPicture_fromFile` (from a file in internal SD card, which are ciphered)

It means that the second handles deciphering, and next displays it (calling the first **HAL_SCR_displayPicture_fromBuffer** or calling same internal functions).

Analysis of `HAL_SCR_displayPicture_fromBuffer`
```
Outgoing References - HAL_SCR_displayPicture_fromBuffer
+- printf_level
+- FUN_9000e334
  +- FUN_9000ecec
  +- bmp_decoder_ReadDataBuff
  +- FUN_9000ed1c
  +- FUN_9000ed4c
+- FUN_900117d8
```

Analysis of `HAL_SCR_displayPicture_fromFile`
```
Outgoing References - HAL_SCR_displayPicture_fromFile
+- printf_level
+- FUN_9000e334
  +- FUN_9000ecec
  +- bmp_decoder_ReadDataBuff
  +- FUN_9000ed1c
  +- FUN_9000ed4c
+- HAL_FS_fileClose
+- sleep_ms
+- FUN_900117d8
```

Same stack.  `bmp_decoder_ReadDataBuff` might adapt based on global variables, and skip f_read part if using flash pointer.    
Other function to analyze : `CMD_sd_checksum`

```
If ciphered, it has to be unciphered.
If written ciphered, it has to be 1. read, 2. unciphered
Checking all f_read() calls

HAL_FS_fileRead -> reads & decipher
HAL_FS_decipher

No opposite operation with write. Most of writtings might be performed by host computer, already ciphered. 
To check with root files, like .md
```

# Crypt-Analysis 
[Here](CIPHERING.md)

# Symbols
[Here](SYMBOLS.md.md)

# Resources

## SD structure & Files 
`sd:0:\.pi`   
`sd:0:\.cfg`   
`sd:0:\.md` - MetaData   
`sd:0:\version` - contains a simple date      
`sd:0:\.content\XXXXXXXX\bt`   
`sd:0:\.content\XXXXXXXX\li`   
`sd:0:\.content\XXXXXXXX\ni`   
`sd:0:\.content\XXXXXXXX\nm`   
`sd:0:\.content\XXXXXXXX\ri` - Resource Index ?   
`sd:0:\.content\XXXXXXXX\si` - Song Index ?   
`sd:0:\.content\XXXXXXXX\rf\` - Resource Folder ?   
`sd:0:\.content\XXXXXXXX\rf\000\YYYYYYYY` - Resources (BMP, others ?)  
`sd:0:\.content\XXXXXXXX\sf\` - Song Folder ?   
`sd:0:\.content\XXXXXXXX\sf\000\YYYYYYYY` - Songs, story part (MP3 ?)

## Bitmaps

| Address | Label | Image |
|-|-|-|
| 0x9001C04E | BITMAP_WAKEUP | ![](dump/bitmaps/wakeup.bmp) |
| 0x9001D37E | BITMAP_LUNII_ERROR | ![](dump/bitmaps/LuniiError.bmp) |
| 0x9001EB94 | BITMAP_LUNII | ![](dump/bitmaps/Lunii.bmp) |
| 0x9001FF32 | BITMAP_LOW_BATTERY | ![](dump/bitmaps/LowBattery.bmp) |
| 0x900215F4 | BITMAP_MODE_TEST | ![](dump/bitmaps/ModeTest.bmp) |
| 0x90023C3A | BITMAP_SLEEP | ![](dump/bitmaps/Sleep.bmp) |
| 0x90024C18 | BITMAP_NOSDCARD | ![](dump/bitmaps/NoSD.bmp) |
| 0x900262A4 | BITMAP_SDERROR | ![](dump/bitmaps/SDError.bmp) |
| 0x90027B80 | BITMAP_LUNII_APP | ![](dump/bitmaps/LuniiApp.bmp) |
| 0x90028F12 | BITMAP_USB | ![](dump/bitmaps/USB.bmp) |

# Links

- https://www.youtube.com/watch?v=ZeYKieOIsC8
- https://fr.wikipedia.org/wiki/Tiny_Encryption_Algorithm
- https://github.com/coderarjob/tea-c
