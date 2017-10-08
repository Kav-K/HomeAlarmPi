HOMEALARMPI - Kaveen Kumarasinghe
=============
Monitors a doorway and sounds a buzzer and light when opened while armed.
Uses RFID/NFC cards to disable it. Specific passphrases for disabling of the alarm
can be set through the Write mechanism. Further comments exist in the code.

The flexibility of this code means you can add multiple modules and/or remove multiple modules to be
activated during an alarm event, one such example would be adding relays to trigger higher-power devices, adding stepper motors connected to
door locks to remotely lock doors, and so forth. Expansion ideas are not limited.

BASE of this project is off the MFRC522 Python library.

Code will be cleaned up (it is extremely messy right now) and pin numberings will be added on this page ASAP.

THE FOURTH BLOCK OF ANY SECTOR HOLDS THE AUTHENTICATION INFORMATION.

If you would like to change the default authentication key please input the following into the 4th block of the desired sector

A= KEY VALUE (Part of your passphrase)

inputbytes = [A,A,A,A,A,A,0xFF,0x07,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]

The access modifiers 0xFF,0x07,0x00,0x00 ensure that the first 6 bytes will be used for authentication. Also known as KEY A





MFRC522-python
==============

A small class to interface with the NFC reader Module MFRC522 on the Raspberry Pi.

This is a Python port of the example code for the NFC module MF522-AN.

##Requirements
This code requires you to have SPI-Py installed from the following repository:
https://github.com/lthiery/SPI-Py

##Revision
The MFRC522py library has been edited slightly by me to better output chip data.
