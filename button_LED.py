#!/usr/bin/env python3
# pylint: disable=missing-docstring

#!/usr/bin/env python3

# MIT License see https://opensource.org/licenses/MIT
# copyright (c) 2021 Klaus Mezger, ECOM Engineering

''' Simple python 3.x shutdown control using switch and LED

This script allows a controlled shutdown preventing SD-Card damage
Switch:
    press >3 seconds:  secure system shutdown is triggered
    double click:      secure shutdown and restart
    press >6 seconds:  optional supply shutdown with external hardware
LED:
    turns on, as soon as raspberry is ready
    turns off, as soon as controlled power down is compleded

For help use commandline "python3 button_LED.py -h"
For auto start: 
sudo nano /lib/systemd/system/shutdown.service


    

Hardware component used:
    * 330Ohm resistor
    * Low current (green) LED
    * SPST switch 

Connections:
    * Raspi output port --> LED(anode)-LED(cathode) --> resistor --> GND
    * Raspi input Port --> switch --> GND
    * [optional, if not programmed in config.txt) Raspi input Port --> 10kOhm resistor to 3.3V]

Prerequisites, if using Raspberry internal pullup for switch:
    * Enable internal pullup on input port on bottom in file /boot/config.txt
        #set GPIO20 as input with pullup high
        gpio=20=ip,pu 
    
'''



import sys
import os
from datetime import timedelta, datetime
import time
from gpiod import chip, line_request, line_event

# todo: use new BIAS instead of pullup defined in /boot/config.txt

def getArgs():
    '''Read arguments from command line.'''

    ledDefault = 21
    switchDefault = 20
    powerDefault = 0  # standard GPIO 26

    parser = argparse.ArgumentParser(description="controlled raspberry shutdown service")

    #sys.argv = ["-f"]    # workaround https://stackoverflow.com/a/30662356                              
    parser.add_argument("-l","--ledPort", type=int, default=ledDefault, metavar='',
                        help='LED output bcm port default = ' + str(ledDefault))
    parser.add_argument("-s", "--switchPort", type=int, default=switchDefault, metavar='',
                        help='Switch control input bcm port default = ' + str(switchDefault))
    parser.add_argument("-p", "--powerPort", type=int, default=powerDefault, metavar='',
                        help='Optional bcm port for external power timer')

    args=parser.parse_args()
    buttonHandler(args)
    


#key press time in sec
C_SHORT = 0.2
C_LONG = 3         #shutdown Raspberry off
C_SUPERLONG = 5    #shutdown & power off: needs external hardware

def buttonHandler(ports):
    # defaults
    BUTTON_CHIP = 0
    BUTTON_EDGE = line_request.EVENT_BOTH_EDGES
    # BUTTON_LINE_OFFSET = 20
    # LED_LINE_OFFSET = 21
    # POWER_PORT_OFFSET = 0  # default not used


    #try:
    # if 0 == 0:
    #     if len(sys.argv) > 2:
    #         LED_LINE_OFFSET = int(sys.argv[1])
    #         BUTTON_LINE_OFFSET = int(sys.argv[2])
    #         POWER_PORT_OFFSET = int(sys.argv[3])
    
    LED_LINE_OFFSET = ports.ledPort
    BUTTON_LINE_OFFSET = ports.switchPort
    POWER_PORT_OFFSET = ports.powerPort

    c = chip(BUTTON_CHIP)
    button = c.get_line(BUTTON_LINE_OFFSET)
    led = c.get_line(LED_LINE_OFFSET)

    config = line_request()
    config.consumer = "LED"
    config.request_type = line_request.DIRECTION_OUTPUT
    config.flags = line_request.FLAG_BIAS_PULL_UP

    led.request(config)
    led.set_value(1)

    config.consumer = "Button"
    config.request_type = BUTTON_EDGE

    button.request(config)

    startTime = 0.0
    endTime = 0.0
    pulseTime = 0.0
    pauseTime = 0.0
    blinkCount = int(0)
    key_press = False
    checkDoublePress = False
    line_level = 1

    print("event fd: ", button.event_get_fd())
    oldStamp = 0.0
    # lastStamp = 0.0
    timeDiff = 0.0


    while True:
        try:
            if button.event_wait(timedelta(seconds=0.5)):  # loop t = 0.5s
                # event_read() is blocking function.
                event = button.event_read()
                newStamp = event.timestamp
                if oldStamp == 0:        # first event?
                    oldStamp = newStamp  # make oldStamp a timedelta type
                else:
                    timeDiff = (newStamp - oldStamp).total_seconds()    
                    oldStamp = event.timestamp

                line_level = button.get_value()

                if event.event_type == line_event.FALLING_EDGE: 
                    print("falling: ", event.timestamp)   # key pressed!
                    if key_press == False:
                        keypress = True
                        pauseTime = pulseTime
                        print("timeDiff", timeDiff)
                else:
                    print("rising: ", event.timestamp)  # key released
                    if timeDiff > 0.02:
                        pulseTime = timeDiff
                        key_press = False


            else:  # 0.5 sec clock
                if line_level == 0:
                    blinkCount += 1
                    if blinkCount % 2 == 0:
                        print("BlinkCount =", blinkCount)
                        led.set_value(1)
                    else:
                        led.set_value(0)
                else:  # key is released
                    led.set_value(1)
                    blinkCount = 0 
                    keyAction = "NO_KEY"
                    if pulseTime > 0 and pulseTime < 0.2: 
                        if checkDoublePress == False:
                            checkDoublePress = True
                        else:
                            if pauseTime < 0.5: #this is a double click
                                keyAction = "DOUBLE_PRESS restart"
                                print(keyAction)
                                os.system("sudo shutdown -r now")
                    else:          
                        checkDoublePress = False
                        

                    if pulseTime > C_SUPERLONG:
                        keyAction = "SUPER_LONG_PRESS shutdown and power OFF"
                        print(keyAction)
                        # power down needs power off through external circuitry
        #               powerPort.set_value(1) 
                        os.system("sudo shutdown -P now")      

                    elif pulseTime > C_LONG:
                        keyAction = "LONG_PRESS shutdown"
                        print(keyAction)
                        os.system("sudo shutdown -h now")

                    elif pulseTime > C_SHORT:
                        keyAction = "SHORT PRESS not used"  
                        print(keyAction)

        #            print("keyAction =", keyAction)       
        #            print("pulseTime =", pulseTime,"pauseTime =", pauseTime)
        #               keyAction = "NO_KEY"
        except KeyboardInterrupt: 
            led.set_value(0)
            c.reset()
            print('  ciao---')
            break

if __name__ == '__main__':
    import argparse
    getArgs()

    
 
 

