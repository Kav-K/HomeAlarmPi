#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import time
import signal
GPIO.cleanup()
continue_reading = True
global pressed,active,armed
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

recentlyDeactivated = False

#Set the pins for the different modules.
button = 16
active = False
buzzer2 = 35
buzzer = 7
pressed = False
switch = 12
blue = 40
red = 38
green = 36


#Setup the GPIO Inputs and outputs
GPIO.setup(button,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(buzzer2,GPIO.OUT)
GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(red,GPIO.OUT)
GPIO.setup(green,GPIO.OUT)
GPIO.setup(blue,GPIO.OUT)
GPIO.setup(buzzer,GPIO.OUT)

#Setup PWMs
buzzer2pwm = GPIO.PWM(buzzer2,1300)
bluepwm = GPIO.PWM(blue,6000)
redpwm = GPIO.PWM(red,4000)
greenpwm = GPIO.PWM(green,4000)
buzzerpwm = GPIO.PWM(buzzer,4000)

#Start PWMs
buzzer2pwm.start(0)
bluepwm.start(50)
redpwm.start(75)
greenpwm.start(0)
buzzerpwm.start(0)

#Just in case 
GPIO.output(green,0)
GPIO.output(red,0)

#Set default values for global variables
disarmed = False

#Block of the card to read
readsector = 12

#Not armed by default
armed = False

#Valid password for Mifare auth
validpass = [0x62,0x78,0x33,0x32,0x5A,0x5A,0x7A,0x38,0x72,0x73,0x67,0x51,0x51,0x35,0x74,0x37]
# This checks for chips. If one is near it will get the UID and authenticate
def rearmEffect():
    global pressed
    pressed = False
    buzzerpwm.ChangeDutyCycle(100)
    bluepwm.ChangeDutyCycle(0)       
    greenpwm.ChangeDutyCycle(100)

    time.sleep(0.5)
    greenpwm.ChangeDutyCycle(0)
    bluepwm.ChangeDutyCycle(100)
    buzzerpwm.ChangeDutyCycle(0)



def startAlarm():
    redpwm.ChangeDutyCycle(75)
    redpwm.ChangeFrequency(5)
    bluepwm.ChangeDutyCycle(0)
    greenpwm.ChangeDutyCycle(0)
    buzzerpwm.ChangeDutyCycle(75)
    buzzer2pwm.ChangeDutyCycle(75)
    buzzer2pwm.ChangeFrequency(5)
    buzzerpwm.ChangeFrequency(5)


def invalidAuthNotify():
    #Increase frequency, get more intense
    redpwm.ChangeDutyCycle(75)
    redpwm.ChangeFrequency(10)
    bluepwm.ChangeDutyCycle(0)
    greenpwm.ChangeDutyCycle(0)
    buzzer2pwm.ChangeFrequency(10)
    buzzerpwm.ChangeFrequency(10)
    time.sleep(2)

def armedIdle():
    #Return to idle blue state
    redpwm.ChangeDutyCycle(0)
    bluepwm.ChangeDutyCycle(100)
    buzzerpwm.ChangeDutyCycle(0)
    buzzer2pwm.ChangeDutyCycle(0)

def validAuthNotify():
    #Sustained tone and green light. Return to IDLE.
    redpwm.ChangeDutyCycle(0)
    bluepwm.ChangeDutyCycle(0)
    greenpwm.ChangeDutyCycle(100)
    buzzerpwm.ChangeDutyCycle(100)
    buzzer2pwm.ChangeDutyCycle(0)
    time.sleep(0.3)
    bluepwm.ChangeDutyCycle(100)
    greenpwm.ChangeDutyCycle(0)
    buzzerpwm.ChangeDutyCycle(0)
    buzzer2pwm.ChangeDutyCycle(0)


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
            #Convert the obtained into an array for comparison
            obtained = obtained.replace("[","")
            obtained = obtained.replace("]","")
            obtainedarray = obtained.split(",")
            #Default result is zero.
            result = 0
            
            for x in range (0,16):
                #Strip any possible white spaces, convert array values into integers for comparison
                obtainedarray[x] = obtainedarray[x].strip()
                obtainedarray[x] = int(obtainedarray[x])
            print obtainedarray
            print validpass
            
            if (obtainedarray == validpass):
                print "Valid Key"
                validAuthNotify()
                result = 1
                
            else:
                print "Invalid Password"
                invalidAuthNotify()
                result = 0
            #Stop Reading
            MIFAREReader.MFRC522_StopCrypto1()
            return result
            
        else:
            print "Authentication error"



def callbackTriggered(channel):
    global pressed,active,armed
    if (GPIO.input(switch) == 0):
        if (pressed == True):
            pressed = False
            return
        if (armed == False):
            print "Not armed, returning"
            print armed
            return
        startAlarm()
        #Alarm is active, block clicking of sensor and button now
        active = True        
        while True:
            if (read() == 1):
                #Return to armed, idle blue state
                armedIdle()

                active = False
                break
        #This compensates for late falling edges
        #bluepwm.ChangeDutyCycle(100)
        #redpwm.ChangeDutyCycle(0)
        #armed = True
        arm()
        recentlyDeactivated = True
        time.sleep(2)
        recentlyDeactivated = False

    else:
        if (active == False):
            if (armed == True):
                rearmEffect()
                
        print "Triggered"
def pressedSensor(channel):
    global armed
    if (armed == True):

        global pressed
        print "PRESSED"
        pressed = True
        time.sleep(0.05)




#function for arming, the armed variable basically controls the functions
def arm():
    global armed
    armed = True
    print "Now Armed"
    print armed
    bluepwm.ChangeDutyCycle(100)
    redpwm.ChangeDutyCycle(0)
    greenpwm.ChangeDutyCycle(0)
    buzzerpwm.ChangeDutyCycle(100)
    time.sleep(0.3)
    buzzerpwm.ChangeDutyCycle(0)
def unArm():
    global armed
    armed = False
    print "Now Unarmed"
    buzzerpwm.ChangeDutyCycle(0)
    time.sleep(0.2)
    buzzerpwm.ChangeDutyCycle(100)
    time.sleep(0.3)
    buzzerpwm.ChangeDutyCycle(0)
    time.sleep(0.3)
    buzzerpwm.ChangeDutyCycle(100)
    time.sleep(0.3)
    buzzerpwm.ChangeDutyCycle(0)
    
    bluepwm.ChangeDutyCycle(50)
    redpwm.ChangeDutyCycle(75)
    redpwm.ChangeFrequency(4000)
    bluepwm.ChangeFrequency(4000)
    greenpwm.ChangeDutyCycle(0)

def pressedButton(channel):
    global armed,active
    if (active != True):
        
        if (armed == False):
            arm()

        elif (armed == True):
            if (recentlyDeactivated == True):
                return
            else:
                unArm()
    return
    



#Add GPIO events to concurrently check for rising and falling edges.
GPIO.add_event_detect(switch, GPIO.FALLING, callback=callbackTriggered, bouncetime=1000)
GPIO.add_event_detect(11,GPIO.RISING,callback=pressedSensor,bouncetime=300)
GPIO.add_event_detect(button,GPIO.FALLING,callback=pressedButton,bouncetime=3000)
#GPIO.add_event_detect(switch,GPIO.RISING,callback=callbackRested,bouncetime=300)


#Just keep the program running, since all rising/falling edge events are being threaded
while True:
    time.sleep(0.05)
