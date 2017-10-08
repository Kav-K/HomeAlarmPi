#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal

continue_reading = True


#This is which sector block you wish to write to
sector = 12
# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        # Print UID
        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
    
        # This is the default key for authentication
        #You may change this as needed to be able to access the desired block.
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, sector, key, uid)
        print "\n"

        # Check if authenticated
        if status == MIFAREReader.MI_OK:

            # Full 16 bytes to write to the specified sector block.
            # Make sure not to write to the fourth block in a sector, as it will block out access unless you know what you are doing.
            #Replace this with your writing
            data = [0x62,0x78,0x33,0x32,0x5A,0x5A,0x7A,0x38,0x72,0x73,0x67,0x51,0x51,0x35,0x74,0x37]


            # Fill the data with 0xFF

            print "Sector",sector,"looked like this:"
            # Read block 8
            MIFAREReader.MFRC522_Read(sector)
            print "\n"

            print "Sector",sector,"will now be filled with Sequential"
            # Write the data
            MIFAREReader.MFRC522_Write(sector, data)
            print "\n"

            print "It now looks like this:"
            # Check to see if it was written
              

            MIFAREReader.MFRC522_Read(sector)
           # print string1
           # data = []
           # # Fill the data with 0x00
           # for x in range(0,16):
                #data.append(0x4B)

#            print "Now we fill it with 0x00:"
 #           MIFAREReader.MFRC522_Write(8, data)
  #          print "\n"
#
 #           print "It is now empty:"
            # Check to see if it was written
  #          MIFAREReader.MFRC522_Read(8)
   #         print "\n"

            # Stop
            MIFAREReader.MFRC522_StopCrypto1()

            # Make sure to stop reading for cards
            continue_reading = False
        else:
            print "Authentication error"
