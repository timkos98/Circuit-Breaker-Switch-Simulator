# Test Progams that cycles through the outputs in the order
# of down the line of the left side of the rasp pi pinheader
# then down the right side of the rasp pi pinheader

## Left Side
# Display (Pin 3, 6)
# Pin 11 - input
# Pin 13 - input
# Pin 15 - input
# Pin 29 - input
# Pin 31 - input
# Pin 37 - input
# Pin 39 - input
## Right Side
# Pin 16 - output
# Pin 18 - input
# Pin 22 - input
# Pin 36 - output
# Pin 38 - output
# Pin 40 - output

import I2C_LCD_driver
import RPi.GPIO as GPIO

from time import *

# Test Display
disp = I2C_LCD_driver.lcd()
disp.lcd_display_string("Wiring Test",2,4)
sleep(1)
disp.lcd_clear()
sleep(1)
disp.lcd_display_string("Let's Begin",2,4)
sleep(1)
disp.lcd_clear()

# GPIO Iinitialization - BCM for GPIO number and BOARD for pin number
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Pin definitions
greenLED = 36
redLED = 38
output = 40
switchSlct = 11
breaker = 13
trip = 15
close = 37
tripOvrd = 29
closeOvrd = 31
click = 22

# Pin Initializations
GPIO.setup(greenLED,GPIO.OUT)
GPIO.setup(redLED,GPIO.OUT)
GPIO.setup(output,GPIO.OUT)

GPIO.setup(switchSlct, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(breaker, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(trip, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(close, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(tripOvrd, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(closeOvrd, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(click, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(output,0)
GPIO.output(greenLED,0)
GPIO.output(redLED,0)


sleep(1)

# Test Green LED
disp.lcd_display_string("Green LED", 2,4)
GPIO.output(greenLED,1)
sleep(1)
disp.lcd_clear()
GPIO.output(greenLED,0)

# Test Red LED
disp.lcd_display_string("Red  LED", 2,6)
GPIO.output(redLED,1)
sleep(1)
disp.lcd_clear()
GPIO.output(redLED,0)

# Test Trip output (Should remain 0 as it is the defualt)
disp.lcd_display_string("Trip - Default", 2,3)
sleep(1)

# Test Close Output
disp.lcd_clear()
disp.lcd_display_string("Close", 2,6)
GPIO.output(output,1)
sleep(1)
disp.lcd_clear()
GPIO.output(output,0)
sleep(1)

# Test Switch Selection
try:  
    while not GPIO.input(switchSlct):
        disp.lcd_display_string("Select Switch", 2,2)
        disp.lcd_display_string("--not selected--", 3,2)
except KeyboardInterrupt:
    GPIO.cleanup()

disp.lcd_clear()
disp.lcd_display_string("Success (SW)", 2,6)
sleep(1)
disp.lcd_clear()

# Test Breaker Selection
try:
    while not GPIO.input(breaker):
	disp.lcd_display_string("Select Breaker", 2,2)
        disp.lcd_display_string("--not selected--", 3,2)
except KeyboardInterrupt:
    GPIO.cleanup()

disp.lcd_clear()
disp.lcd_display_string("Success(B)", 2,6)
sleep(1)
disp.lcd_clear()

# Test Trip Override
try:
    while not GPIO.input(tripOvrd):
        disp.lcd_display_string("Select Trip Ovrd", 2,2)
	disp.lcd_display_string("--not selected--", 3,2)
except KeyboardInterrupt:
    GPIO.cleanup()
    
disp.lcd_clear()
disp.lcd_display_string("Success(Tp OV)", 2,6)
sleep(1)
disp.lcd_clear()

# Test Close Override
try:
    while not GPIO.input(closeOvrd):
	disp.lcd_display_string("Select Close Ovrd", 2,2)
        disp.lcd_display_string("--not selected--", 3,2)
except KeyboardInterrupt:
    GPIO.cleanup()

disp.lcd_clear()
disp.lcd_display_string("Success(Cl OV)", 2,6)
sleep(1)
disp.lcd_clear()

# Test Center Click
print("Center Click", GPIO.input(click))
try:
    while not GPIO.input(click):
	disp.lcd_display_string("Select Center Click", 2,1)
        disp.lcd_display_string("--not selected--", 3,2)
except KeyboardInterrupt:
    GPIO.cleanup()

disp.lcd_clear()
disp.lcd_display_string("Success(Clck)", 2,6)
sleep(1)
disp.lcd_clear()

disp.lcd_display_string("DONE", 2,8)
GPIO.cleanup()
