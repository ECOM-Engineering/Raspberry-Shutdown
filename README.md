
# Project Raspberry-Shutdown

The **Raspberry-Shutdown Project** describes a very simple system in order to shut down Raspberry Pi safely. It consists of a Python 3.x script *button_LED.py*, a simple schematic and this description.  
This project is tested in Raspberry models 3, 3B, 4B, zero-wh under Raspberry OS. 
The python script uses the awesome [libgpiod](https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/about/) library  
For older Raspbian OS consider unsing the   [deprecated script version](https://github.com/ECOM-Engineering/Raspberry-Shutdown-DEPRECATED)

## Background
A running Linux computer should not be powered off without a controlled shutdown by the operating system, because this can result in damaging the file system on the SD_Card. 
Controlled power down is especially critical to achieve in so called headless systems with no monitor and keyboard. Raspberry computers do not provide a reset or power down switch.
The presented solution allows initiating shutdown or a restart with a switch or an external signal. It also provides a hardware signal (e.g. LED) indicating the running operating system state.

## Functionality

 **On power up / boot**  
After Linux boot, a selectable port (default BCM21) is driven high and LED goes ON

**Switch pressed > 2 seconds --> shutdown**  
Linux command *'shutdown -P now'* will be executed by the script **button_LED.py** . 
As soon as critical storage operations are completed, LED goes OFF.

**Switch double clicked --> shutdown and restart**  
System shuts down and restarts.  
Linux command *'shutdown -r now'*  will be executed by the script **button_LED.py**.

**Switch pressed > 5 seconds** (optional)  
System shuts down and activates a selectable port until no more SD card access occur. This signal may be used in order to completely power down Raspberry by switching off  the external power supply .

**Restart after shut down**  
This is only achievable by external power off and on again.
(A much more convenient solution is using the [UPS-2](https://github.com/ECOM-Engineering/UPS-2_Uninteruptible-Power-Supply)  project.

**Project Components**
- The python script **button_LED.py**
- A  push button switch
- A high efficiency LED
- some wires

## More information
See [user-guide.md](doc/user-guide.md)

