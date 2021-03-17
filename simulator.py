""" 
The way the interrupts are cancelled and restarted at the start and end of the callback functions
was implemented based on suggestions by John Buchman (JPL, Boeing) who referred to Ted Kopf's (JPL) interrupt handling
implementations. Special thanks to them!

Program Author: Tim M. Kostersitz
Application: Circuit Breaker/ Switch simulator (Electrical Engineering Capstone)
Institution: University of Washington, Bothell
Contact: timkos@live.at
"""

# Main Program to run upon Start-up

import I2C_LCD_driver
import RPi.GPIO as GPIO
import initialValuesForCBSS as initVals
from time import sleep

# Initialize Inputs and Outputs
# GPIO Iinitialization - BCM for GPIO number and BOARD for pin number
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Pin definitions
greenLED = 36
redLED = 38
output = 40
switchSlct = 11
breakerSlct = 13
trip = 15
close = 37
tripOvrd = 29
closeOvrd = 31
click = 22
clk = 16
dt = 18

# Pin Initializations
GPIO.setup(greenLED, GPIO.OUT)
GPIO.setup(redLED,   GPIO.OUT)
GPIO.setup(output,   GPIO.OUT)

GPIO.setup(switchSlct,   GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(breakerSlct,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(trip,         GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(close,        GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(tripOvrd,     GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(closeOvrd,    GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(click,        GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(clk,          GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt,           GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(greenLED, 1)
GPIO.output(redLED,   0)

# Display setup
disp = I2C_LCD_driver.lcd()

# Cursor Position set to lock all values just in case
cursorPos = 0
# Get Switch Initial Values
SoDelay = initVals.Switch_OpenInitialValue
ScDelay = initVals.Switch_CloseInitialValue

# Get Breaker Initial Values
conversionFactor = 1000 # to convert seconds to miliseconds for the breaker display
BoDelay = initVals.Breaker_OpenInitialValue*conversionFactor
BcDelay = initVals.Breaker_CloseInitialValue*conversionFactor

# Set digit maximums, minimus, and intrisic delay compensation
closeComp = 0.02
openComp = 0.02
d1Min = 0
d2Min = 0
d3Min = 0
d1Max = 10
d2Max = 9
d3Max = 9

maxDelay = d1Max + d2Max*0.1 + d3Max*0.01
minDelay = openComp + d1Min + d2Min*0.1 + d3Min*0.01


# Dial initial values:
step = 1
dialChange = 0
resetPressTime = 2 # in seconds
btime = 250 # bounctime -- if set too high this will slow down the max spped the dial will respond to
longPress = False

# ==== Definition of functions ====

def slct_switch():
    # called when selection is switch simulation
    # always
    global switchSlct
    global cursorPos
    global encoder
    global textRefreshSpeed

    cursorPos = 0
    dialChange = 0
    
    # Functions used while switch is the selected device
    # Resets the delay values
    def reset():
        global SoDelay
        global ScDelay
        global cursorPos
        global longPress

        # Get Switch Initial Values
        SoDelay = initVals.Switch_OpenInitialValue
        ScDelay = initVals.Switch_CloseInitialValue
        cursorPos = 0
        longPress = False

    # Updates the contents on the screen
    def updateDisplay():
        global SoDelay
        global ScDelay
        global cursorPos
        global dialChange

        # Set a variable to hold the dial change at this time and reset it
        change = dialChange
        dialChange = 0

        tempOpenDelay1 = SoDelay + change
        tempOpenDelay2 = SoDelay + change * 0.1
        tempOpenDelay3 = SoDelay + change * 0.01
        tempCloseDelay1 = ScDelay + change
        tempCloseDelay2 = ScDelay + change * 0.1
        tempCloseDelay3 = ScDelay + change * 0.01

        if cursorPos == 0:
            # Locked
            oStatus = "L"
            cStatus = "L"
        elif cursorPos == 1 :
            # row = 1, digit = 1
            oStatus = "1"
            cStatus = "L"
            if tempOpenDelay1 >= minDelay and tempOpenDelay1 <= maxDelay:
                SoDelay = tempOpenDelay1
            elif tempOpenDelay1 < minDelay:
                SoDelay = minDelay
            elif tempOpenDelay1 > maxDelay:
                SoDelay = maxDelay
        elif cursorPos == 2:
            # row = 1, digit = 2
            oStatus = "2"
            cStatus = "L"
            if tempOpenDelay2 >= minDelay and tempOpenDelay2 <= maxDelay:
                SoDelay = tempOpenDelay2
            elif tempOpenDelay2 < minDelay:
                SoDelay = minDelay
            elif tempOpenDelay2 > maxDelay:
                SoDelay = maxDelay
        elif cursorPos == 3:
            # row = 1, digit = 3
            oStatus = "3"
            cStatus = "L"
            if tempOpenDelay3 >= minDelay and tempOpenDelay3 <= maxDelay:
                SoDelay = tempOpenDelay3
            elif tempOpenDelay3 < minDelay:
                SoDelay = minDelay
            elif tempOpenDelay3 > maxDelay:
                SoDelay = maxDelay
        elif cursorPos == 4:
            # row = 2, digit = 1
            oStatus = "L"
            cStatus = "1"
            if tempCloseDelay1 >= minDelay and tempCloseDelay1 <= maxDelay:
                ScDelay = tempCloseDelay1
            elif tempCloseDelay1 < minDelay:
                ScDelay = minDelay
            elif tempCloseDelay1 > maxDelay:
                ScDelay = maxDelay
        elif cursorPos == 5:
            # row = 2, digit = 2
            oStatus = "L"
            cStatus = "2"
            if tempCloseDelay2 >= minDelay and tempCloseDelay2 <= maxDelay:
                ScDelay = tempCloseDelay2
            elif tempCloseDelay2 < minDelay:
                ScDelay = minDelay
            elif tempCloseDelay2 > maxDelay:
                ScDelay = maxDelay
        elif cursorPos == 6:
            # row = 2, digit = 3
            oStatus = "L"
            cStatus = "3"
            if tempCloseDelay3 >= minDelay and tempCloseDelay3 <= maxDelay:
                ScDelay = tempCloseDelay3
            elif tempCloseDelay3 < minDelay:
                ScDelay = minDelay
            elif tempCloseDelay3 > maxDelay:
                ScDelay = maxDelay
        elif cursorPos >= 7:
            # reset the position to lock both values
            cursorPos = 0
            oStatus = "L"
            cStatus = "L"
        
        disp.lcd_display_string("Open Dly:  [{}] {:.2f}s".format(oStatus, SoDelay),3)
        disp.lcd_display_string("Close Dly: [{}] {:.2f}s".format(cStatus, ScDelay),4)


    # Initalize display
    disp.lcd_display_string("Simulating: Switch ", 1)
    disp.lcd_display_string("*push dial for next*", 2)
    disp.lcd_display_string("Open Dly:  [L] {:.2f}s".format(SoDelay),3)
    disp.lcd_display_string("Close Dly: [L] {:.2f}s".format(ScDelay),4)
        
    while GPIO.input(switchSlct):
        # Be a switch simulator
        # Save 
        # Check for longPress
        if longPress:
            reset()
            updateDisplay()

        # Refresh the display content
        updateDisplay()

    # Bridge gap between switch, just to be sure it isn't in an in between
    # selections state

    sleep(0.5)
    # Now check if the breaker option is selected. If not, go back to being a switch simiulator
    if breakerSlct:
        slct_breaker()
    else:
        slct_switch()

def slct_breaker():
    # called when selection is breaker simulatio                                                                                                                                 
    # always                                                                                                                                                                      
    global breakerSlct
    global cursorPos
    global encoder

    cursorPos = 0
    dialChange = 0

    # Functions used while simulating a breaker
    # Resets all delay values to the default values
    def reset():
        global BoDelay
        global BcDelay
        global cursorPos
        global conversionFactor
        global longPress

        BoDelay = initVals.Breaker_OpenInitialValue*conversionFactor
        BcDelay = initVals.Breaker_CloseInitialValue*conversionFactor
        cursorPos = 0
        longPress = False
        
    def updateDisplay():
        global BoDelay
        global BcDelay
        global cursorPos
        global dialChange
        global minDelay
        global maxDelay

        BminDelay = minDelay*conversionFactor
        BmaxDelay = maxDelay*conversionFactor

        change = dialChange
        dialChange = 0
        tempOpenDelay1 = BoDelay + change * 100
        tempOpenDelay2 = BoDelay + change * 10
        tempOpenDelay3 = BoDelay + change * 1
        tempCloseDelay1 = BcDelay + change * 100
        tempCloseDelay2 = BcDelay + change * 10
        tempCloseDelay3 = BcDelay + change * 1

        if cursorPos == 0:
            # Locked
            oStatus = "L"
            cStatus = "L"
        elif cursorPos == 1 :
            # row = 1, digit = 1
            oStatus = "1"
            cStatus = "L"
            if tempOpenDelay1 >= BminDelay and tempOpenDelay1 <= BmaxDelay:
                BoDelay = tempOpenDelay1
            elif tempOpenDelay1 < BminDelay:
                BoDelay = BminDelay
            elif tempOpenDelay1 > BmaxDelay:
                BoDelay = BmaxDelay
        elif cursorPos == 2:
            # row = 1, digit = 2
            oStatus = "2"
            cStatus = "L"
            if tempOpenDelay2 >= BminDelay and tempOpenDelay2 <= BmaxDelay:
                BoDelay = tempOpenDelay2
            elif tempOpenDelay2 < BminDelay:
                BoDelay = BminDelay
            elif tempOpenDelay2 > BmaxDelay:
                BoDelay = BmaxDelay
        elif cursorPos == 3:
            # row = 1, digit = 3
            oStatus = "3"
            cStatus = "L"
            if tempOpenDelay3 >= BminDelay and tempOpenDelay3 <= BmaxDelay:
                BoDelay = tempOpenDelay3
            elif tempOpenDelay3 < BminDelay:
                BoDelay = BminDelay
            elif tempOpenDelay3 > BmaxDelay:
                BoDelay = BmaxDelay
        elif cursorPos == 4:
            # row = 2, digit = 1
            oStatus = "L"
            cStatus = "1"
            status = 1
            if tempCloseDelay1 >= BminDelay and tempCloseDelay1 <= BmaxDelay:
                BcDelay = tempCloseDelay1
            elif tempCloseDelay1 < BminDelay:
                BcDelay = BminDelay
            elif tempCloseDelay1 > BmaxDelay:
                BcDelay = BmaxDelay
        elif cursorPos == 5:
            # row = 2, digit = 2
            oStatus = "L"
            cStatus = "2"
            staus = 2
            if tempCloseDelay2 >= BminDelay and tempCloseDelay2 <= BmaxDelay:
                BcDelay = tempCloseDelay2
            elif tempCloseDelay2 < BminDelay:
                BcDelay = BminDelay
            elif tempCloseDelay2 > BmaxDelay:
                BcDelay = BmaxDelay
        elif cursorPos == 6:
            # row = 2, digit = 3
            oStatus = "L"
            cStatus = "3"
            status = 3
            if tempCloseDelay3 >= BminDelay and tempCloseDelay3 <= BmaxDelay:
                BcDelay = tempCloseDelay3
            elif tempCloseDelay3 < BminDelay:
                BcDelay = BminDelay
            elif tempCloseDelay3 > BmaxDelay:
                BcDelay = BmaxDelay
        elif cursorPos >= 7 or cursorPos < 0:
            # reset the position to lock both values
            cursorPos = 0
            oStatus = "L"
            cStatus = "L"
        
        if BoDelay < 100 and BoDelay >= 10:
            oDelayAsString = "0{}".format(round(BoDelay))
        elif BoDelay < 10:
            oDelayAsString = "00{}".format(round(BoDelay))
        else:
            oDelayAsString = "{}".format(round(BoDelay))

        if BcDelay < 100 and BcDelay >= 10:
            cDelayAsString = "0{}".format(round(BcDelay))
        elif BcDelay < 10:
            cDelayAsString = "00{}".format(round(BcDelay))
        else:
            cDelayAsString = "{}".format(round(BcDelay))

        disp.lcd_display_string("Open Dly:  [{}] {}ms".format(oStatus, oDelayAsString),3)
        disp.lcd_display_string("Close Dly: [{}] {}ms".format(cStatus, cDelayAsString),4)

    # from encoder import Encoder
    # Make display row selection Variable                                                                                                                                        
    # 0 = no row (Both locked)                                                                                                                                                   
    # 1 = Open delay selected and ready for adjustment
    # 2 = Close delay selected and ready for adjustment

    # Formating to accomodate miliseconds (ms) vs seconds (s)
    if BoDelay < 100 and BoDelay >= 10:
        oDelayAsString = " {}".format(round(BoDelay))
    elif BoDelay < 10:
        oDelayAsString = "  {}".format(round(BoDelay))
    else:
        oDelayAsString = "{}".format(round(BoDelay))

    if BcDelay < 100:
        cDelayAsString = " {}".format(round(BcDelay))
    elif BcDelay < 10:
        cDelayAsString = "  {}".format(round(BcDelay))
    else:
        cDelayAsString = "{}".format(round(BcDelay))

    disp.lcd_display_string("Simulating: Breaker", 1)
    disp.lcd_display_string("*push dial for next*", 2)
    disp.lcd_display_string("Open Dly:  [L] {}ms".format(oDelayAsString),3)
    disp.lcd_display_string("Close Dly: [L] {}ms".format(cDelayAsString),4)

    

    while GPIO.input(breakerSlct):
        # Be a breaker simulator                                                                                                                                                 
        # Selection change based on row variable
        if longPress:
            reset()
            updateDisplay()

        # Refresh the display content
        updateDisplay()

    # Bridge gap between switch, just to be sure it isn't in an in between 
    sleep(0.5)
    
    if switchSlct:
        slct_switch()
    else:
        slct_breaker()

# Callback for receiving a trip- or open-signal
def trip_high(channel):
    GPIO.remove_event_detect(channel)
    print("Entering Trip")
    # called when signal on trip input is set HIGH
    # only when either switch or breaker is selected
    global conversionFactor
    global switchSlct
    global breakerSlct
    global openComp
    
    if GPIO.input(switchSlct):
        sleep(SoDelay-openComp)
        GPIO.output(output, 0)
        GPIO.output(redLED, 0)
        GPIO.output(greenLED, 1)
    elif GPIO.input(breakerSlct):
        sleep(BoDelay/conversionFactor-openComp)
        GPIO.output(output, 0)
        GPIO.output(redLED, 0)
        GPIO.output(greenLED, 1)
    GPIO.add_event_detect(trip, GPIO.RISING, callback=trip_high)

# Callback for receiving a close-signal
def close_high(channel):
    GPIO.remove_event_detect(channel)
    print("Entering Close")
    # called when signal on close input is set HIGH
    # only when either switch or breaker is selected
    global conversionFactor
    global switchSlct
    global breakerSlct
    global closeComp
    
    if GPIO.input(switchSlct-closeComp):
        sleep(ScDelay)
        GPIO.output(output, 1)
        GPIO.output(redLED, 1)
        GPIO.output(greenLED, 0)
    elif GPIO.input(breakerSlct):
        sleep(BcDelay/conversionFactor-closeComp)
        GPIO.output(output, 1)
        GPIO.output(redLED, 1)
        GPIO.output(greenLED, 0)
    GPIO.add_event_detect(close, GPIO.RISING, callback=close_high)

# Callback for the trip override switch being applied
def trip_override_high(channel):
    GPIO.remove_event_detect(channel)
    # called when trip override is pressed
    # always
    global switchSlct
    global breakerSlct
    global cursorPos
    
    cursorPos = 0

    GPIO.output(output, 0)
    GPIO.output(greenLED, 1)
    GPIO.output(redLED, 0)
    GPIO.add_event_detect(tripOvrd, GPIO.RISING, callback=trip_override_high)

# Callback for close override being applied
def close_override_high(channel):
    GPIO.remove_event_detect(channel)
    # called when close override is pressed
    # always
    global switchSlct
    global breakerSlct
    global cursorPos
    
    cursorPos = 0

    GPIO.output(output, 1)
    GPIO.output(redLED, 1)
    GPIO.output(greenLED, 0)
    GPIO.add_event_detect(closeOvrd, GPIO.RISING, callback=close_override_high)

# Function for checking rotary encoder switch pin (center press down)
def rot_sw_clicked(channel):
    GPIO.remove_event_detect(channel)
    global cursorPos
    global longPress
    global resetPressTime

    cursorPos += 1
    sleep(0.5)

    counter = 0
    while GPIO.input(channel):
        sleep(0.5)
        counter += 1
        if counter >=resetPressTime:
            longPress = True
            cursorPos = 0
            break
    GPIO.add_event_detect(click, GPIO.RISING, callback=rot_sw_clicked, bouncetime=300)

# Callback from rotary encoder clk pin
def rot_clk_change(channel):
    # called when dial is rotated
    GPIO.remove_event_detect(channel)
    global dialChange
    global step
    global btime
    
    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
    
    if clkState == 0 and dtState == 1:
        dialChange = dialChange - step
    GPIO.add_event_detect(clk, GPIO.FALLING, callback=rot_clk_change, bouncetime=btime)

# Callback from rotary encoder dt pin
def rot_dt_change(channel):
    # called when dial is rotated
    GPIO.remove_event_detect(channel)
    global dialChange
    global step
    global btime

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)

    if clkState == 1 and dtState == 0:
        dialChange = dialChange + step
    GPIO.add_event_detect(dt, GPIO.FALLING, callback=rot_dt_change, bouncetime=btime)


# ==== Interrupt event handling ====

# case: Trip input is set HIGH
GPIO.add_event_detect(trip, GPIO.RISING, callback=trip_high)
# case: Close input is set HIGH
GPIO.add_event_detect(close, GPIO.RISING, callback=close_high)
# case: Trip Override set HIGH
GPIO.add_event_detect(tripOvrd, GPIO.RISING, callback=trip_override_high)
# case: Close Override set HIGH
GPIO.add_event_detect(closeOvrd, GPIO.RISING, callback=close_override_high)
# case: Center click
GPIO.add_event_detect(click, GPIO.RISING, callback=rot_sw_clicked)
# case: Dial rotation
GPIO.add_event_detect(clk, GPIO.FALLING, callback=rot_clk_change, bouncetime=btime)
GPIO.add_event_detect(dt, GPIO.FALLING, callback=rot_dt_change, bouncetime=btime)

# Initial selector switch position check
if GPIO.input(switchSlct):
    # Go into switch operation
    slct_switch()

elif GPIO.input(breakerSlct):
    # Go into breaker operation
    slct_breaker()
else:
    disp.lcd_display_string("Error: No Device Selected ",2)

    
