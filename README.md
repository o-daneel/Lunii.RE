
![](resources/StoryTeller.avif)
Lunii is a French company that made an interactive box for kids to customize stories. Lunii made our children loving stories, a real helper for them to fall asleep.  
 **If you like it, BUY IT !!!  
Even if you don't, children will 😁**

# Sections

1. [Hardware](HARDWARE.md)
2. [Firmware analysis](ANALYSIS.md)
3. [Ciphering reverse](CIPHERING.md)

# TODO
* Undelete on storyteller ?
* Describe test mode
* Deep dive in file section to understand format
  * .cfg : **DONE**
  * .ni...
* Decompile 
  * Boot FW : **DONE**       > [Bootloader Firmware](ANALYSIS.md#bootloader-firmware) 
  * Main FW : in progress > [Main Firmware](ANALYSIS.md#main-firmware) 
  * Backup FW : partial but **CLOSED**, no worth > [Backup Firmware](ANALYSIS.md#backup-firmware) 
* Firmware management
  * Try loading firmware update
  * Create custom firmware (simple internal picture update)
  * Restore original FW
  * Insert dummy patch (just back and forth) + try it (using custom picture)
  * Make less dummy patch with printf call (can't be read without UART acces)
  * Make patch to write to SD :
    1.  A dummy file
    2.  File with SNU + DATA
    3.  File with KeyA & KeyB in plain
* sample code to process TEA cipher/decipher
  * in C or python ?
  * Try it on Key_A ciphered files
* How to extract Key_B ?
  
# Similar repos
* [(Hackday) Tsukuyomi Hacking Lunii](https://hackaday.io/project/167629-tsukuyomi)
* [(GitHub) Tsukuyomi](https://github.com/danksz/tsukuyomi)
* [STUdio - Story Teller Unleashed](https://marian-m12l.github.io/studio-website/)
* [(GitHub) STUdio, Story Teller Unleashed](https://github.com/marian-m12l/studio)
* [(GitHub) STUdio ](https://github.com/marian-m12l/studio/wiki/Documentation)