#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import time
import signal
GPIO.cleanup()
continue_reading = True
global pressed,armed
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

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."
armed = False
buzzer2 = 35
buzzer = 7
pressed = False
switch = 12
blue = 40
red = 38
green = 36
GPIO.setup(switch,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(buzzer2,GPIO.OUT)
GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_UP)
buzzer2pwm = GPIO.PWM(buzzer2,1300)
buzzer2pwm.start(0)
GPIO.setup(red,GPIO.OUT)
GPIO.setup(green,GPIO.OUT)
GPIO.output(green,0)
GPIO.output(red,0)
GPIO.setup(blue,GPIO.OUT)
GPIO.setup(buzzer,GPIO.OUT)
buzzerpwm = GPIO.PWM(buzzer,4000)
bluepwm = GPIO.PWM(blue,6000)
redpwm = GPIO.PWM(red,4000)
greenpwm = GPIO.PWM(green,4000)
bluepwm.start(100)
redpwm.start(5)
greenpwm.start(5)
buzzerpwm.start(0)
disarmed = False
readsector = 12
validpass = [0x62,0x78,0x33,0x32,0x5A,0x5A,0x7A,0x38,0x72,0x73,0x67,0x51,0x51,0x35,0x74,0x37]
# This loop keeps checking for chips. If one is near it will get the UID and authenticate
def read():
    GPIO.setmode(GPIO.BOARD)

    
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
        key = [0x69,0x13,0x24,0x35,0x43,0x21]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, readsector, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            obtained = MIFAREReader.MFRC522_Read2(readsector)
          #  print obtained
            obtained = obtained.replace("[","")
            obtained = obtained.replace("]","")
            obtainedarray = obtained.split(",")
            result = 0
            for x in range (0,16):
                obtainedarray[x] = obtainedarray[x].strip()
                obtainedarray[x] = int(obtainedarray[x])
            print obtainedarray
            print validpass
            if (obtainedarray == validpass):
                print "Valid Key"
                redpwm.ChangeDutyCycle(0)
                bluepwm.ChangeDutyCycle(0)
                greenpwm.ChangeDutyCycle(100)
                buzzerpwm.ChangeDutyCycle(100)
                buzzer2pwm.ChangeDutyCycle(0)
                time.sleep(0.5)
                bluepwm.ChangeDutyCycle(100)
                greenpwm.ChangeDutyCycle(0)
                buzzerpwm.ChangeDutyCycle(0)
                buzzer2pwm.ChangeDutyCycle(0)
                result = 1
                
            else:
                print "Invalid Password"
                redpwm.ChangeDutyCycle(75)
                redpwm.ChangeFrequency(10)
                bluepwm.ChangeDutyCycle(0)
                greenpwm.ChangeDutyCycle(0)
                buzzer2pwm.ChangeFrequency(10)
                buzzerpwm.ChangeFrequency(10)
                time.sleep(2)
                result = 0
            MIFAREReader.MFRC522_StopCrypto1()
            return result
            
        else:
            print "Authentication error"
dutyset = False
def callbackTriggered(channel):
    global pressed,armed
    if (GPIO.input(switch) == 0):
        if (pressed == True):
            pressed = False
            return
        redpwm.ChangeDutyCycle(75)
        redpwm.ChangeFrequency(5)
        bluepwm.ChangeDutyCycle(0)
        greenpwm.ChangeDutyCycle(0)
        buzzerpwm.ChangeDutyCycle(75)
        buzzer2pwm.ChangeDutyCycle(75)
        buzzer2pwm.ChangeFrequency(5)
        buzzerpwm.ChangeFrequency(5)
        dutyset = True
        armed = True        
        while True:
            if (read() == 1):
                redpwm.ChangeDutyCycle(0)
                bluepwm.ChangeDutyCycle(100)
                buzzerpwm.ChangeDutyCycle(0)
                buzzer2pwm.ChangeDutyCycle(0)
                dutyset = False
                armed = False
                break
    else:
        if (armed == False):
            pressed = False
            buzzerpwm.ChangeDutyCycle(100)
            bluepwm.ChangeDutyCycle(0)       
            greenpwm.ChangeDutyCycle(100)
            
            time.sleep(0.5)
            greenpwm.ChangeDutyCycle(0)
            bluepwm.ChangeDutyCycle(100)
            buzzerpwm.ChangeDutyCycle(0)
                
        print "Triggered"
def pressedSensor(channel):
    global pressed
    print "PRESSED"
    pressed = True
    time.sleep(3)
GPIO.add_event_detect(switch, GPIO.FALLING, callback=callbackTriggered, bouncetime=1000)
GPIO.add_event_detect(11,GPIO.RISING,callback=pressedSensor,bouncetime=300)
#GPIO.add_event_detect(switch,GPIO.RISING,callback=callbackRested,bouncetime=300)



while True:
    #print GPIO.input(switch)
    time.sleep(0.05)
