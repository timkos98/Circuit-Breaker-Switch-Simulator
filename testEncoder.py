# Testing the code for the rotary encoder
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

clk = 16
dt = 18
GPIO.setup(clk,          GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt,           GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

enable = 1
step = 1
dialChange = 0
while enable:
    if not GPIO.input(clk):
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        
        if clkState == 0 and dtState == 1:
            dialChange = dialChange - step
    elif not GPIO.input(dt):
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
    
        if clkState == 1 and dtState == 0:
            dialChange = dialChange + step
    print(dialChange)
                                                                                        
