#!/usr/bin/env python3
# pylint: disable=missing-docstring

import sys
import os
from datetime import timedelta, datetime
import time
from gpiod import chip, line_request, line_event

# todo: use new BIAS instead of pullup defined in /boot/config.txt


#key press time in sec
C_SHORT = 0.2
C_LONG = 3         #shutdown Raspberry off
C_SUPERLONG = 5    #shutdown & power off: needs external hardware

def buttonHandler():
    # defaults
    BUTTON_CHIP = 0
    BUTTON_EDGE = line_request.EVENT_BOTH_EDGES
    BUTTON_LINE_OFFSET = 20
    LED_LINE_OFFSET = 21

    #try:
    if 0 == 0:
        if len(sys.argv) > 2:
            BUTTON_CHIP = sys.argv[1]
            BUTTON_LINE_OFFSET = int(sys.argv[3])
            LED_LINE_OFFSET = int(sys.argv[2])
            if len(sys.argv) > 3:
                edge = sys.argv[3]
                if edge[0] == "r":
                    BUTTON_EDGE = line_request.EVENT_RISING_EDGE
                elif edge[0] == "f":
                    BUTTON_EDGE = line_request.EVENT_FALLING_EDGE
                else:
                    BUTTON_EDGE = line_request.EVENT_BOTH_EDGES
            else:
                BUTTON_EDGE = line_request.EVENT_BOTH_EDGES

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

                    print("keyAction =", keyAction)       
                    print("pulseTime =", pulseTime,"pauseTime =", pauseTime)
        #               keyAction = "NO_KEY"
        except KeyboardInterrupt: 
            led.set_value(0)
            c.reset()
            print('  ciao---')
            break

if __name__ == '__main__':
    buttonHandler()
    
 
 

