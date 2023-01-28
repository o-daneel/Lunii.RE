
# Hardware

* Battery : Li-ion 4.2v 600mA
* Voltage Regulator : AP7362 (DIODES) 4.2v -> 3.3v
* Battery Management System (BMS) : MCP73833
* Main CPU : STM32F730Z8T6 Cortex M7
  RAM : 256KB
  Flash : 64KB
* External Flash : adesto AT25SF041 - 512MB
  QSPI interface
* SD 16GB (SDIO interface)
* ST25DV04K (I2C interface)
* Audio ampli : PAM8019

## Mapping
* GPIOE - display ?
* GPIOB - audio chip ?

# Memory layout
<img src="resources/mem_map.png" width="400">

Two of them are of interest:
1. QuadSPI external flash from `0x8000 0000 - 0x9FFF FFFF`
2. Internal flash from `0x0800 0000 - 0x080? ????`
3. Internal RAM from `0x2000 0000 - 0x2003 FFFF`

## SNU location

8 bytes for SNU located at : `0x0800 C000 - 0x0800 C007` (internal flash)

# Security study

## Ghidra Project
TBFilled

## Thoughts
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

# Symbols

**!! OBSOLETE !!**
To be updated with new symbols from ghidra

## HALs

### FatFs
| Name | Location | Type | Namespace | Source | Ref count |
| --- | --- | --- | :---: | --- | ---: |
| HAL_FS_fileCreate | `0x9000f448` | Function | Global | User Defined | 1 |
| HAL_FS_fileOpen | `0x9000f4d8` | Function | Global | User Defined | 5 |
| HAL_FS_fileDelete? | `0x9000f5e8` | Function | Global | User Defined | 2 |
| HAL_FS_fileClose | `0x9000f634` | Function | Global | User Defined | 17 |

### Audio
| Name | Location | Type | Namespace | Source | Ref count |
| --- | --- | --- | :---: | --- | ---: |
| HAL_AUDIO_pause | `0x9000f370` | Function | Global | User Defined | 2 |
| HAL_AUDIO_pause | `0x90010538` | Function | Global | User Defined | 1 |
| HAL_AUDIO_play | `0x9000f6bc` | Function | Global | User Defined | 1 |
| HAL_AUDIO_resume | `0x9000f394` | Function | Global | User Defined | 1 |

### Screen
| Name | Location | Type | Namespace | Source | Ref count |
| --- | --- | --- | :---: | --- | ---: |
| HAL_SCR_activate | `0x9000f218` | Function | Global | User Defined | 4 |
| HAL_SCR_displayPicture_fromBuffer | `0x9000f294` | Function | Global | User Defined | 15 |
| HAL_SCR_displayPicture_fromFile | `0x9000f664` | Function | Global | User Defined | 1 |

### NFC
| Name | Location | Type | Namespace | Source | Ref count |
| --- | --- | --- | :---: | --- | ---: |
| HAL_NFC_update | `0x9001161c` | Function | Global | User Defined | 1 |
| HAL_NFC_write | `0x9001166c` | Function | Global | User Defined | 1 |

### Others
| Name | Location | Type | Namespace | Source | Ref count |
| --- | --- | --- | :---: | --- | ---: |
| HAL_enterSleep | `0x9000f188` | Function | Global | User Defined | 11 |
| HAL_reset | `0x9000f170` | Function | Global | User Defined | 5 |

## Core

VectorTable

### Vector Table
Location `0x9000 0000` ? seems to be more relevant @ `0x0000 0000`

See chapter [9.1.2 Interrupt and exception vectors ](docs/rm0431-stm32f72xxx-and-stm32f73xxx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)

| Name | Location | Type | Namespace | Source | Ref count |
| --- | --- | --- | :---: | --- | ---: |
| Reset_Handler | `0x9001702c` | Function | Global | User Defined | 1 |
| OTG_HS_Handler | `0x90015b4c` | Function | Global | User Defined | 0 |
| EXTI2_Handler | `0x90015ada` | Function | Global | User Defined | 0 |
| EXTI1_Handler | `0x90015ad4` | Function | Global | User Defined | 0 |
| TIM6_DAC_Handler | `0x90015b18` | Function | Global | User Defined | 0 |
| DMA1_Stream5_Handler | `0x90015ae0` | Function | Global | User Defined | 0 |
| EXTI9_5_Handler | `0x90015aec` | Function | Global | User Defined | 0 |
| TIM3_Handler | `0x90015af4` | Function | Global | User Defined | 0 |
| EXTI15_10_Handler | `0x90015b00` | Function | Global | User Defined | 0 |
| DMA2_Stream0_Handler | `0x90015b34` | Function | Global | User Defined | 0 |
| DMA2_Stream5_Handler | `0x90015b40` | Function | Global | User Defined | 0 |
| SDMMC2_Handler | `0x90015b58` | Function | Global | User Defined | 0 |
| SysTick_Handler | `0x9000a3f4` | Function | Global | User Defined | 0 |
| PendSV_Handler | `0x9000a390` | Function | Global | User Defined | 0 |
| DebugMonitor_Handler | `0x90015ad2` | Function | Global | User Defined | 0 |
| SVCall_Handler | `0x9000a2f0` | Function | Global | User Defined | 0 |
| UsageFault_Handler | `0x90015ad0` | Function | Global | User Defined | 2 |
| BusFault_Handler | `0x90015ace` | Function | Global | User Defined | 1 |
| Undefined_Handler | `0x9001707c` | Function | Global | User Defined | 1 |
| MemManage_Handler | `0x90015acc` | Function | Global | User Defined | 1 |
| HardFault_Handler | `0x90015aca` | Function | Global | User Defined | 1 |
| HardFault_Handler | `0x90015acb` | Label | Global | User Defined | 1 |
| NMI_Handler | `0x90015ac8` | Function | Global | User Defined | 0 |


### Low-Level
| Name | Location | Type | Namespace | Source | Ref count |
| --- | --- | --- | :---: | --- | ---: |
| ADC3_init | `0x900144c0` | Function | Global | User Defined | 1 |
| DAC_init | `0x90013f9c` | Function | Global | User Defined | 1 |
| DMA_init | `0x900145b8` | Function | Global | User Defined | 1 |
| I2C3_init | `0x900143bc` | Function | Global | User Defined | 1 |
| IDWG_init | `0x900147b0` | Function | Global | User Defined | 1 |
| PERIPHERALS_init | `0x900126a8` | Function | Global | User Defined | 1 |
| SDMMC2_init | `0x900148a8` | Function | Global | User Defined | 1 |
| SPI4_init | `0x90014d88` | Function | Global | User Defined | 1 |
| TIM1_init | `0x90014f3c` | Function | Global | User Defined | 1 |
| TIM6_init | `0x90015d30` | Function | Global | User Defined | 1 |

### OS & Lib C

| Name | Location | Type | Namespace | Source | Ref count |
| --- | --- | --- | :---: | --- | ---: |
| file_exist | `0x9000f568` | Function | Global | User Defined | 2 |
| file_open | `0x900077e8` | Function | Global | User Defined | 10 |
| file_close | `0x90007d84` | Function | Global | User Defined | 10 |
| file_delete? | `0x900080d8` | Function | Global | User Defined | 3 |
| file_read? | `0x900079c0` | Function | Global | User Defined | 5 |
| file_write | `0x90007b38` | Function | Global | User Defined | 3 |
| sleep_1s | `0x9000f204` | Function | Global | User Defined | 1 |
| sleep_ms | `0x90014194` | Function | Global | User Defined | 6 |
| strcpy | `0x900172ae` | Function | Global | User Defined | 10 |
| strcat | `0x90017290` | Function | Global | User Defined | 24 |
| strcmp | `0x90000450` | Function | Global | User Defined | 10 |
| printf_level | `0x9000e534` | Function | Global | User Defined | 152 |
| printf_vararg | `0x90016ffc` | Function | Global | User Defined | 33 |
| sprintf | `0x90017214` | Function | Global | User Defined | 3 |

### Others


| Name | Location | Type | Namespace | Source | Ref count |
| --- | --- | --- | :---: | --- | ---: |
| main | `0x90014990` | Function | Global | User Defined | 1 |
| event_loop | `0x9001291c` | Function | Global | User Defined | 1 |
| nfc_write | `0x900114c8` | Function | Global | User Defined | 2 |
| TASK_eventHandler | `0x90014544` | Function | Global | User Defined | 2 |
| MP3_DECODER_requestPlay | `0x90010f2c` | Function | Global | User Defined | 2 |
| | | | | | | |
| | | | | | | |
| cur_audio_handler | `0x20011f78` | Data Label | Global | User Defined | 7 | 0 |
| audio_play_state | `0x2001202c` | Data Label | Global | User Defined | 19 | 0 |
| audio_resume | `0x9001117c` | Function | Global | User Defined | 3 |
| audio_pause | `0x9001115c` | Function | Global | User Defined | 3 |
| audio_getState | `0x90011150` | Function | Global | User Defined | 3 |
| | | | | | | |
| | | | | | | |
| story_play_picture | `0x9000fd34` | Function | Global | User Defined | 1 |
| story_display_picture | `0x9000fb10` | Function | Global | User Defined | 2 |
| story_display_error | `0x9000fa9c` | Function | Global | User Defined | 13 |
| | | | | | | |
| | | | | | | |
| get_battery_level | `0x9000f1e4` | Function | Global | User Defined | 3 |
| get_battery_voltage | `0x9000e230` | Function | Global | User Defined | 7 |
| get_gpio_state | `0x90001a9c` | Function | Global | User Defined | 48 |
| get_version | `0x90013340` | Function | Global | User Defined | 2 |
| get_sd_mounted_state | `0x9001275c` | Function | Global | User Defined | 1 |
| get_PropValue | `0x900115e0` | Function | Global | User Defined | 5 |



## Test mode

| Name | Location | Type | Namespace | Source | Ref count |
| --- | --- | --- | :---: | --- | ---: |
| lunii_shell | `0x90013d50` | Function | Global | User Defined | 1 |
| | | | | | | |
| | | | | | | |
| CMD_jack_presence | `0x900133b4` | Function | Global | User | 0 |
| CMD_bouton_selection | `0x900133e4` | Function | Global | User Defined | 0 |
| CMD_boutons_poussoirs | `0x90013458` | Function | Global | User Defined | 0 |
| CMD_mcu_uuid | `0x900134c4` | Function | Global | User Defined | 0 |
| CMD_nfc_uuid | `0x900134f8` | Function | Global | User Defined | 0 |
| CMD_vbat | `0x90013538` | Function | Global | User Defined | 0 |
| CMD_audio_off | `0x9001355c` | Function | Global | User Defined | 0 |
| CMD_sd_version | `0x900135c0` | Function | Global | User Defined | 0 |
| CMD_sd_checksum | `0x90013628` | Function | Global | User Defined | 0 |
| CMD_autotest | `0x900136c8` | Function | Global | User Defined | 0 |
| CMD_softVersion | `0x9001383c` | Function | Global | User Defined | 1 |
| CMD_audio_jack | `0x900138f8` | Function | Global | User Defined | 0 |
| CMD_reboot | `0x90013914` | Function | Global | User Defined | 0 |
| CMD_sd_mounted | `0x9001392c` | Function | Global | User Defined | 0 |
| CMD_ecran_blanc | `0x90013954` | Function | Global | User Defined | 0 |
| CMD_ecran_off | `0x90013970` | Function | Global | User Defined | 0 |
| CMD_ecran_logo | `0x90013988` | Function | Global | User Defined | 0 |
| CMD_nfc_write | `0x900139a4` | Function | Global | User Defined | 0 |
| CMD_nfc_read | `0x900139d0` | Function | Global | User Defined | 0 |
| CMD_hw_version | `0x90013a20` | Function | Global | User Defined | 0 |
| CMD_write_key_uuid | `0x90013aa8` | Function | Global | User Defined | 0 |


## Raw Table
Data to consider for previous section update
```
ADC3_init                           0x900144c0    Function    Global  User Defined    1   0
audio_getState                      0x90011150    Function    Global  User Defined    3   0
audio_pause                         0x9001115c    Function    Global  User Defined    3   0
audio_play_state                    0x2001202c    Data Label  Global  User Defined    19  0
audio_resume                        0x9001117c    Function    Global  User Defined    3   0
BITMAP_LOW_BATTERY                  0x9001ff32    Data Label  Global  User Defined    9   0
BITMAP_LUNII                        0x9001eb94    Data Label  Global  User Defined    6   0
BITMAP_LUNII_APP                    0x90027b80    Data Label  Global  User Defined    2   0
BITMAP_LUNII_ERROR                  0x9001d37e    Data Label  Global  User Defined    2   0
BITMAP_MODE_TEST                    0x900215f4    Data Label  Global  User Defined    2   0
BITMAP_NOSDCARD                     0x90024c18    Data Label  Global  User Defined    2   0
BITMAP_SDERROR                      0x900262a4    Data Label  Global  User Defined    2   0
BITMAP_SLEEP                        0x90023c3a    Data Label  Global  User Defined    2   0
BITMAP_USB                          0x90028f12    Data Label  Global  User Defined    2   0
BITMAP_WAKEUP                       0x9001c04e    Data Label  Global  User Defined    2   0
bmp_decoder_ReadDataBuff            0x9000e280    Function    Global  User Defined    4   0
BusFault_Handler                    0x90015ace    Function    Global  User Defined    1   1
clmt_clust                          0x9000662e    Function    Global  User Defined    3   0
clst2sect                           0x90006618    Function    Global  User Defined    8   0
CMD_audio_jack                      0x900138f8    Function    Global  User Defined    0   1
CMD_audio_off                       0x9001355c    Function    Global  User Defined    0   1
CMD_audio_speaker                   0x900138dc    Function    Global  User Defined    0   1
CMD_autotest                        0x900136c8    Function    Global  User Defined    0   1
CMD_bouton_selection                0x900133e4    Function    Global  User Defined    0   1
CMD_boutons_poussoirs               0x90013458    Function    Global  User Defined    0   1
CMD_ecran_blanc                     0x90013954    Function    Global  User Defined    0   1
CMD_ecran_damier                    0x90013bc0    Function    Global  User Defined    0   1
CMD_ecran_damier_inv                0x90013bd8    Function    Global  User Defined    0   1
CMD_ecran_logo                      0x90013988    Function    Global  User Defined    0   1
CMD_ecran_off                       0x90013970    Function    Global  User Defined    0   1
CMD_hw_version                      0x90013a20    Function    Global  User Defined    0   1
CMD_jack_presence                   0x900133b4    Function    Global  User Defined    0   1
CMD_mcu_uuid                        0x900134c4    Function    Global  User Defined    0   1
CMD_nfc_read                        0x900139d0    Function    Global  User Defined    0   1
CMD_nfc_uuid                        0x900134f8    Function    Global  User Defined    0   1
CMD_nfc_write                       0x900139a4    Function    Global  User Defined    0   1
CMD_reboot                          0x90013914    Function    Global  User Defined    0   1
CMD_sd_checksum                     0x90013628    Function    Global  User Defined    0   1
CMD_sd_mounted                      0x9001392c    Function    Global  User Defined    0   1
CMD_sd_version                      0x900135c0    Function    Global  User Defined    0   1
CMD_softVersion                     0x9001383c    Function    Global  User Defined    1   1
CMD_vbat                            0x90013538    Function    Global  User Defined    0   1
CMD_write_key_uuid                  0x90013aa8    Function    Global  User Defined    0   1
create_chain                        0x90006cbe    Function    Global  User Defined    4   0
Crypto_KEY?                         0x9000eafc    Data Label  Global  User Defined    1   0
cur_audio_handler                   0x20011f78    Data Label  Global  User Defined    8   0
DAC_init                            0x90013f9c    Function    Global  User Defined    1   0
DebugMonitor_Handler                0x90015ad2    Function    Global  User Defined    0   1
dir_clear                           0x900066e6    Function    Global  User Defined    2   0
dir_next                            0x90006e88    Function    Global  User Defined    5   0
dir_read                            0x90006fb8    Function    Global  User Defined    2   0
dir_register                        0x90007298    Function    Global  User Defined    1   0
dir_remove                          0x900070e4    Function    Global  User Defined    1   0
dir_sdi                             0x90006c3a    Function    Global  User Defined    7   0
disk_ioctl                          0x900065d0    Function    Global  User Defined    4   0
disk_read                           0x90006598    Function    Global  User Defined    7   0
disk_write                          0x900065b4    Function    Global  User Defined    16  0
display_damier                      0x90013b38    Function    Global  User Defined    2   0
display_frame_buffer                0x20011f74    Data Label  Global  User Defined    10  0
dist_status                         0x90006564    Function    Global  User Defined    2   0
DMA_init                            0x900145b8    Function    Global  User Defined    1   0
DMA_Stream                          0x90001310    Function    Global  User Defined    3   0
DMA1_Stream5_Handler                0x90015ae0    Function    Global  User Defined    0   1
DMA2_Stream0_Handler                0x90015b34    Function    Global  User Defined    0   1
DMA2_Stream5_Handler                0x90015b40    Function    Global  User Defined    0   1
empty_fn_1                          0x9000f7c4    Function    Global  User Defined    8   0
event_loop                          0x9001291c    Function    Global  User Defined    1   0
EXTI                                0x40013c00    Data Label  Global  User Defined    11  0
EXTI                                0x90001ab4    Function    Global  User Defined    5   0
EXTI1_Handler                       0x90015ad4    Function    Global  User Defined    0   1
EXTI15_10_Handler                   0x90015b00    Function    Global  User Defined    0   1
EXTI2_Handler                       0x90015ada    Function    Global  User Defined    0   1
EXTI9_5_Handler                     0x90015aec    Function    Global  User Defined    0   1
f_close                             0x90007d84    Function    Global  User Defined    10  0
f_getfree                           0x90008000    Function    Global  User Defined    30  0
f_lseek                             0x90007dac    Function    Global  User Defined    5   0
f_mount                             0x9000776c    Function    Global  User Defined    2   0
f_open                              0x900077e8    Function    Global  User Defined    10  0
f_read                              0x900079c0    Function    Global  User Defined    5   0
f_sync                              0x90007ce4    Function    Global  User Defined    1   0
f_unlink                            0x900080d8    Function    Global  User Defined    3   0
f_write                             0x90007b38    Function    Global  User Defined    3   0
FatFs                               0x2000a668    Data Label  Global  User Defined    1   0
ff_mutex_create                     0x90008998    Function    Global  User Defined    1   0
ff_mutex_delete                     0x900089bc    Function    Global  User Defined    1   0
ff_mutex_give                       0x900141a4    Function    Global  User Defined    2   0
ff_mutex_take                       0x90014230    Function    Global  User Defined    3   0
file_exist                          0x9000f568    Function    Global  User Defined    2   0
follow_path                         0x900074bc    Function    Global  User Defined    3   0
fread_buffer                        0x200163d4    Data Label  Global  User Defined    13  9
get_battery_level                   0x9000f1e4    Function    Global  User Defined    3   0
get_battery_voltage                 0x9000e230    Function    Global  User Defined    7   0
get_fat                             0x90006b86    Function    Global  User Defined    10  0
GET_FATTIME                         0x90014540    Function    Global  User Defined    5   0
get_gpio_state                      0x90001a9c    Function    Global  User Defined    48  0
get_ldnumber                        0x9000666e    Function    Global  User Defined    3   0
get_sd_mounted_state                0x9001275c    Function    Global  User Defined    1   0
get_version                         0x90013340    Function    Global  User Defined    2   0
GPIO_A                              0x40020000    Data Label  Global  User Defined    1   0
GPIO_B                              0x40020400    Data Label  Global  User Defined    1   0
GPIO_bitmask_reset                  0x90001aa8    Function    Global  User Defined    32  0
GPIO_C                              0x40020800    Data Label  Global  User Defined    1   0
GPIO_D                              0x40020c00    Data Label  Global  User Defined    1   0
GPIO_E                              0x40021000    Data Label  Global  User Defined    5   0
GPIO_F                              0x40021400    Data Label  Global  User Defined    2   0
GPIOE_reset                         0x9000ed4c    Function    Global  User Defined    3   0
HAL_AUDIO_pause                     0x9000f370    Function    Global  User Defined    2   0
HAL_AUDIO_pause&resume              0x90010538    Function    Global  User Defined    1   0
HAL_AUDIO_play                      0x9000f6bc    Function    Global  User Defined    1   0
HAL_AUDIO_resume                    0x9000f394    Function    Global  User Defined    1   0
HAL_AUDIO_stop                      0x9000f6fc    Function    Global  User Defined    16  0
HAL_enterSleep                      0x9000f188    Function    Global  User Defined    11  0
HAL_FS_decipher                     0x9000efe4    Function    Global  User Defined    3   0
HAL_FS_fileClose                    0x9000f634    Function    Global  User Defined    17  0
HAL_FS_fileCreate                   0x9000f448    Function    Global  User Defined    1   0
HAL_FS_fileDelete                   0x9000f5e8    Function    Global  User Defined    2   0
HAL_FS_fileOpen                     0x9000f4d8    Function    Global  User Defined    5   0
HAL_FS_fileRead                     0x9000f778    Function    Global  User Defined    8   0
HAL_FS_lseek                        0x9000f764    Function    Global  User Defined    5   0
HAL_memcpy                          0x900170f2    Function    Global  User Defined    19  0
HAL_memset                          0x9001713a    Function    Global  User Defined    22  0
HAL_NFC_update                      0x9001161c    Function    Global  User Defined    1   0
HAL_NFC_write                       0x9001166c    Function    Global  User Defined    1   0
HAL_reset                           0x9000f170    Function    Global  User Defined    5   0
HAL_SCR_activate                    0x9000f218    Function    Global  User Defined    4   0
HAL_SCR_displayPicture_fromBuffer   0x9000f294    Function    Global  User Defined    15  0
HAL_SCR_displayPicture_fromFile     0x9000f664    Function    Global  User Defined    1   0
HardFault_Handler                   0x90015aca    Function    Global  User Defined    1   1
HardFault_Handler                   0x90015acb    Label       Global  User Defined    1   1
I2C3_init                           0x900143bc    Function    Global  User Defined    1   0
IDWG_init                           0x900147b0    Function    Global  User Defined    1   0
ld_clust                            0x900066b0    Function    Global  User Defined    4   0
ld_dword                            0x900065ec    Function    Global  User Defined    14  0
lock_volume                         0x900089c6    Function    Global  User Defined    2   0
lunii_shell                         0x90013d50    Function    Global  User Defined    1   0
main                                0x90014990    Function    Global  User Defined    1   0
mass_storage_enable                 0x90013f14    Function    Global  User Defined    1   0
memcpy                              0x9000669e    Function    Global  User Defined    10  0
MemManage_Handler                   0x90015acc    Function    Global  User Defined    1   1
memset                              0x9000660c    Function    Global  User Defined    11  0
mount_volume                        0x900067f0    Function    Global  User Defined    6   0
move_window                         0x90006738    Function    Global  User Defined    19  0
MP3_DECODER_requestPlay             0x90010f2c    Function    Global  User Defined    2   0
NDEF_get_value                      0x900115e0    Function    Global  User Defined    5   0
nfc_write                           0x900114c8    Function    Global  User Defined    2   0
NMI_Handler                         0x90015ac8    Function    Global  User Defined    0   1
os_MutexDelete                      0x900141ec    Function    Global  User Defined    2   0
OTG_HS_Handler                      0x90015b4c    Function    Global  User Defined    0   1
PCD_Init                            0x90015030    Function    Global  User Defined    1   0
PendSV_Handler                      0x9000a390    Function    Global  User Defined    0   1
PERIPHERALS_init                    0x900126a8    Function    Global  User Defined    1   0
printf_level                        0x9000e534    Function    Global  User Defined    152 0
printf_vararg                       0x90016ffc    Function    Global  User Defined    33  0
put_fat                             0x90006a8c    Function    Global  User Defined    4   0
RCC                                 0x40023800    Data Label  Global  User Defined    121 0
REG_gpioe                           0x9000ed18    Data Label  Global  User Defined    1   0
REG_gpioe                           0x9000ed58    Data Label  Global  User Defined    1   0
remove_chain                        0x90006d6e    Function    Global  User Defined    2   0
Reset_Handler                       0x9001702c    Function    Global  User Defined    1   1
sd_checksum                         0x20013554    Data Label  Global  User Defined    6   0
SD_MOUNTED_STATE                    0x20013024    Data Label  Global  User Defined    7   0
SD_ReadBlocks_DMA                   0x90016908    Function    Global  User Defined    0   1
SD_WriteBlocks_DMA                  0x900168a4    Function    Global  User Defined    0   1
sdmmc_process                       0x90003808    Function    Global  User Defined    1   0
SDMMC2_Handler                      0x90015b58    Function    Global  User Defined    0   1
SDMMC2_init                         0x900148a8    Function    Global  User Defined    1   0
sleep_1s                            0x9000f204    Function    Global  User Defined    1   0
sleep_ms                            0x90014194    Function    Global  User Defined    6   0
some_periph_init_gpioe              0x9000ed5c    Function    Global  User Defined    1   0
SPI4_init                           0x90014d88    Function    Global  User Defined    1   0
sprintf                             0x90017214    Function    Global  User Defined    3   0
st_clust                            0x900066ce    Function    Global  User Defined    2   0
st_dword                            0x900065fc    Function    Global  User Defined    16  0
story_content_display_picture       0x9000fb10    Function    Global  User Defined    2   0
story_content_get_resname           0x9000fa2c    Function    Global  User Defined    3   0
story_content_open                  0x9000f7c8    Function    Global  User Defined    6   0
story_content_play                  0x9000fd34    Function    Global  User Defined    1   0
story_display_error                 0x9000fa9c    Function    Global  User Defined    13  0
story_open_ni                       0x9000faec    Function    Global  User Defined    2   0
strcat                              0x90017290    Function    Global  User Defined    24  0
strcmp                              0x90000450    Function    Global  User Defined    10  0
strcpy                              0x900172ae    Function    Global  User Defined    10  0
sum_sfn                             0x90006650    Function    Global  User Defined    3   0
SVCall_Handler                      0x9000a2f0    Function    Global  User Defined    0   1
sync_fs                             0x90006df2    Function    Global  User Defined    4   0
sync_window                         0x9000672c    Function    Global  User Defined    3   0
SysTick_Handler                     0x9000a3f4    Function    Global  User Defined    0   1
TASK_eventHandler                   0x90014544    Function    Global  User Defined    2   1
TIM1_init                           0x90014f3c    Function    Global  User Defined    1   0
TIM3_Handler                        0x90015af4    Function    Global  User Defined    0   1
TIM6_DAC_Handler                    0x90015b18    Function    Global  User Defined    0   1
TIM6_init                           0x90015d30    Function    Global  User Defined    1   0
TM_dump_state                       0x90013bf0    Function    Global  User Defined    1   0
Undefined_Handler                   0x9001707c    Function    Global  User Defined    1   1
unlock_volume                       0x90006ddc    Function    Global  User Defined    16  0
UsageFault_Handler                  0x90015ad0    Function    Global  User Defined    2   1
USB_check_buffer_size               0x90013ee0    Function    Global  User Defined    2   0
validate                            0x90007720    Function    Global  User Defined    5   0
vectors                             0x00000000    Label       Global  User Defined    0   0
```

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
