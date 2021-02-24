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
BoDelay = initVals.Breaker_OpenInitialValue
BcDelay = initVals.Breaker_CloseInitialValue

# Set digit maximums, minimus, and intrisic delay compensation
compensation = 0.02
d1Min = 0
d2Min = 0
d3Min = 0
d1Max = 10
d2Max = 9
d3Max = 9

maxDelay = d1Max + d2Max*0.1 + d3Max*0.01
minDelay = compensation + d1Min + d2Min*0.1 + d3Min*0.01
conversionFactor = 1000 # to convert seconds to miliseconds for the breaker display

# Dial initial values:
step = 1
dialChange = 0
resetPressTime = 2 # in seconds
btime = 90 # bounctime -- if set too high this will slow down the max spped the dial will respond to
longPress = False

# ==== Definition of functions ====

def slct_switch():
    # called when selection is switch simulation
    # always
    global switchSlct
    global cursorPos
    global encoder
    global textRefreshSpeed
    
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

    def updateDelays():
        global SoDelay
        global ScDelay
        global cursorPos
        global dialChange
            
        OpossibleNextValue = SoDelay + dialChange*SoTs
        CpossibleNextValue = ScDelay + dialChange*ScTs
        dialChange = 0
        # check that this is within bounds
        # First for the open delay
        if cursorPos == 1 and OpossibleNextValue >= SoDelayMin and OpossibleNextValue <= SoDelayMax:
            SoDelay = OpossibleNextValue
        elif cursorPos == 1 and OpossibleNextValue < SoDelayMin:
            SoDelay = SoDelayMin
        elif cursorPos == 1 and OpossibleNextValue > SoDelayMax:
            SoDelay = SoDelayMax
        # Now if close delay is selected
        elif cursorPos == 2 and CpossibleNextValue >= ScDelayMin and CpossibleNextValue <= ScDelayMax:
            ScDelay = CpossibleNextValue
        elif cursorPos == 2 and CpossibleNextValue < ScDelayMin:
            ScDelay = ScDelayMin
        elif cursorPos == 2 and CpossibleNextValue > ScDelayMax:
            ScDelay = ScDelayMax
        elif cursorPos > 2:
            pass

    # Updates the contents on the screen
    def updateDisplay():
        global SoDelay
        global ScDelay
        global cursorPos
        global dialChange
        tempOpenDelay1 = SoDelay + dialChange
        tempOpenDelay2 = SoDelay + dialChange * 0.1
        tempOpenDelay3 = SoDelay + dialChange * 0.01
        tempCloseDelay1 = ScDelay + dialChange
        tempCloseDelay2 = ScDelay + dialChange * 0.1
        tempCloseDelay3 = ScDelay + dialChange * 0.01

        if cursorPos == 0:
            # Locked
            disp.lcd_display_string("Open Dly:  L   {:.2f}s".format(SoDelay),3)
            disp.lcd_display_string("Close Dly: L   {:.2f}s".format(ScDelay),4)
        elif cursorPos == 1 :
            # row = 1, digit = 1
            if tempOpenDelay1 >= minDelay and tempOpenDelay1 <= maxDelay:
                SoDelay = tempOpenDelay1
            elif tempOpenDelay1 < minDelay:
                SoDelay = minDelay
            elif tempOpenDelay1 > maxDelay:
                SoDelay = maxDelay
            dialChange = 0
            disp.lcd_display_string("Open Dly:  [1] {:.2f}s".format(SoDelay),3)
            disp.lcd_display_string("Close Dly: L   {:.2f}s".format(ScDelay),4)

        elif cursorPos == 2:
            # row = 1, digit = 2
            if tempOpenDelay2 >= minDelay and tempOpenDelay2 <= maxDelay:
                SoDelay = tempOpenDelay2
            elif tempOpenDelay2 < minDelay:
                SoDelay = minDelay
            elif tempOpenDelay2 > maxDelay:
                SoDelay = maxDelay
            dialChange = 0
            disp.lcd_display_string("Open Dly:  [2] {:.2f}s".format(SoDelay),3)
            disp.lcd_display_string("Close Dly: L   {:.2f}s".format(ScDelay),4)
        elif cursorPos == 3:
            # row = 1, digit = 3
            if tempOpenDelay3 >= minDelay and tempOpenDelay3 <= maxDelay:
                SoDelay = tempOpenDelay3
            elif tempOpenDelay3 < minDelay:
                SoDelay = minDelay
            elif tempOpenDelay3 > maxDelay:
                SoDelay = maxDelay
            dialChange = 0
            disp.lcd_display_string("Open Dly:  [3] {:.2f}s".format(SoDelay),3)
            disp.lcd_display_string("Close Dly: L   {:.2f}s".format(ScDelay),4)
        elif cursorPos == 4:
            # row = 2, digit = 1
            if tempCloseDelay1 >= minDelay and tempCloseDelay1 <= maxDelay:
                ScDelay = tempCloseDelay1
            elif tempCloseDelay1 < minDelay:
                ScDelay = minDelay
            elif tempCloseDelay1 > maxDelay:
                ScDelay = maxDelay
            dialChange = 0
            disp.lcd_display_string("Open Dly:  L   {:.2f}s".format(SoDelay),3)
            disp.lcd_display_string("Close Dly: [1] {:.2f}s".format(ScDelay),4)
        elif cursorPos == 5:
            # row = 2, digit = 2
            if tempCloseDelay2 >= minDelay and tempCloseDelay2 <= maxDelay:
                ScDelay = tempCloseDelay2
            elif tempCloseDelay2 < minDelay:
                ScDelay = minDelay
            elif tempCloseDelay2 > maxDelay:
                ScDelay = maxDelay
            dialChange = 0
            disp.lcd_display_string("Open Dly:  L   {:.2f}s".format(SoDelay),3)
            disp.lcd_display_string("Close Dly: [2] {:.2f}s".format(ScDelay),4)
        elif cursorPos == 6:
            # row = 2, digit = 3
            if tempCloseDelay3 >= minDelay and tempCloseDelay3 <= maxDelay:
                ScDelay = tempCloseDelay3
            elif tempCloseDelay3 < minDelay:
                ScDelay = minDelay
            elif tempCloseDelay3 > maxDelay:
                ScDelay = maxDelay
            dialChange = 0
            disp.lcd_display_string("Open Dly:  L   {:.2f}s".format(SoDelay),3)
            disp.lcd_display_string("Close Dly: [3] {:.2f}s".format(ScDelay),4)
        elif cursorPos >= 7:
            # reset the position to lock both values
            cursorPos = 0
            updateDisplay()

    # Initialize cursor position as the locked position
    cursorPos = 0
    # Initalize display
    disp.lcd_display_string("Simulating: Switch ", 1)
    disp.lcd_display_string("*push dial for next*", 2)
    disp.lcd_display_string("Open Dly:  L   {:.2f}s".format(SoDelay),3)
    disp.lcd_display_string("Close Dly: L   {:.2f}s".format(ScDelay),4)
        
    while GPIO.input(switchSlct):
        # Be a switch simulator
        # Save 
        # Check for longPress
        if longPress:
            reset()
            updateDisplay()

        # Check for dial press
        if GPIO.event_detected(click):
            rot_sw_clicked(click)
            updateDisplay()
        
        # Check for dial change
        if GPIO.event_detected(clk) and cursorPos > 0:
            rot_clk_change(clk)
            updateDisplay()
        if GPIO.event_detected(dt) and cursorPos > 0:
            rot_dt_change(dt)
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

    # Functions used while simulating a breaker
    # Resets all delay values to the default values
    def reset():
        global BoDelay
        global BcDelay
        global cursorPos
        BoDelay = (BoDelayMax - BoDelayMin)/2
        BcDelay = (BcDelayMax - BoDelayMin)/2
        cursorPos = 0
        
    def updateDelays():
        global BoDelay
        global BcDelay
        global cursorPos
        global dialChange

        # Increase the speed of increase if turning quickly
        if dialChange == 2 or dialChange == -2:
            dialChange = dialChange*10
        elif dialChange > 2 or dialChange < -2:
            dialChange = dialChange*20
            
        OpossibleNextValue = BoDelay + dialChange*BoTs
        CpossibleNextValue = BcDelay + dialChange*BcTs
        dialChange = 0
        # check that this is within bounds                                                                                                                                      
        # First for the open delay
        if cursorPos == 1 and OpossibleNextValue >= BoDelayMin and OpossibleNextValue <= BoDelayMax:
            BoDelay = OpossibleNextValue
        elif cursorPos == 1 and OpossibleNextValue < BoDelayMin:
            BoDelay = BoDelayMin
        elif cursorPos == 1 and OpossibleNextValue > BoDelayMax:
            BoDelay = BoDelayMax
        # Now if close delay is selected                                                                                                                                          
        elif cursorPos == 2 and CpossibleNextValue >= BcDelayMin and CpossibleNextValue <= BcDelayMax:
            BcDelay = CpossibleNextValue
        elif cursorPos == 2 and CpossibleNextValue < BcDelayMin:
            BcDelay = BcDelayMin
        elif cursorPos == 2 and CpossibleNextValue > BcDelayMax:
            BcDelay = BcDelayMax
        elif cursorPos > 2:
            pass

    # from encoder import Encoder
    # Make display row selection Variable                                                                                                                                        
    # 0 = no row (Both locked)                                                                                                                                                   
    # 1 = Open delay selected and ready for adjustment
    # 2 = Close delay selected and ready for adjustment

    # Formating to accomodate miliseconds (ms) vs seconds (s)
    if BoDelay < 100:
        oDelayAsString = " {}".format(round(BoDelay))
    else:
        oDelayAsString = "{}".format(round(BoDelay))

    if BcDelay < 100:
        cDelayAsString = " {}".format(round(BcDelay))
    else:
        cDelayAsString = "{}".format(round(BcDelay))                                   
    disp.lcd_display_string("Simulating: Breaker", 1)
    disp.lcd_display_string("*push dial for next*", 2)
    disp.lcd_display_string("Open Dly:  L   {}ms".format(oDelayAsString),3)
    disp.lcd_display_string("Close Dly: L   {}ms".format(cDelayAsString),4)

    while GPIO.input(breakerSlct):
        # Be a breaker simulator                                                                                                                                                 
        # Selection change based on row variable
        updateDelays()
        
        if longPress:
            reset()
        
        if BoDelay < 100:
            oDelayAsString = " {}".format(round(BoDelay))
        else:
            oDelayAsString = "{}".format(round(BoDelay))

        if BcDelay < 100:
            cDelayAsString = " {}".format(round(BcDelay))
        else:
            cDelayAsString = "{}".format(round(BcDelay))
        
        
        if cursorPos == 0:
            disp.lcd_display_string("Open Dly:  L   {}ms".format(oDelayAsString),3)
            disp.lcd_display_string("Close Dly: L   {}ms".format(cDelayAsString),4)
        elif cursorPos == 1:
            disp.lcd_display_string("Open Dly:      {}ms".format(oDelayAsString),3)
            disp.lcd_display_string("Close Dly: L   {}ms".format(cDelayAsString),4)
        elif cursorPos == 2:
            disp.lcd_display_string("Open Dly:  L   {}ms".format(oDelayAsString),3)
            disp.lcd_display_string("Close Dly:     {}ms".format(cDelayAsString),4)
        elif cursorPos == 3:
            cursorPos = 0

    # Bridge gap between switch, just to be sure it isn't in an in between 
    sleep(0.5)
    
    if switchSlct:
        slct_switch()
    else:
        slct_breaker()

# Callback for receiving a trip- or open-signal
def trip_high(channel):
    print("Entering Trip")
    # called when signal on trip input is set HIGH
    # only when either switch or breaker is selected
    global conversionFactor
    global switchSlct
    global breakerSlct
    
    if GPIO.input(switchSlct):
        sleep(SoDelay)
        GPIO.output(output, 0)
        GPIO.output(redLED, 0)
        GPIO.output(greenLED, 1)
        print("sO")
       # sleep(ScDelay)
    elif GPIO.input(breakerSlct):
        sleep(BoDelay/conversionFactor)
        GPIO.output(output, 0)
        GPIO.output(redLED, 0)
        GPIO.output(greenLED, 1)
        print("bO")
       # sleep(BcDelay/conversionFactor)

# Callback for receiving a close-signal
def close_high(channel):
    print("Entering Close")
    # called when signal on close input is set HIGH
    # only when either switch or breaker is selected
    global conversionFactor
    global switchSlct
    global breakerSlct
    
    if GPIO.input(switchSlct):
        sleep(ScDelay)
        GPIO.output(output, 1)
        GPIO.output(redLED, 1)
        GPIO.output(greenLED, 0)
        print("sC")
       # sleep(SoDelay)
    elif GPIO.input(breakerSlct):
        sleep(BcDelay/conversionFactor)
        GPIO.output(output, 1)
        GPIO.output(redLED, 1)
        GPIO.output(greenLED, 0)
        print("bC")
       # sleep(BoDelay/conversionFactor)

# Callback for the trip override switch being applied
def trip_override_high(channel):
    print("Entering trip override")
    # called when trip override is pressed
    # always
    global switchSlct
    global breakerSlct
    print(GPIO.input(channel))
    if GPIO.input(switchSlct):
     #   sleep(SoDelay)
        GPIO.output(output, 0)
        GPIO.output(greenLED, 1)
        GPIO.output(redLED, 0)
        print("sOov")
     #   sleep(ScDelay)

    elif GPIO.input(breakerSlct):
     #   sleep(BoDelay)
        GPIO.output(output, 0)
        GPIO.output(greenLED, 1)
        GPIO.output(redLED, 0)
        print("bOov")

     #   sleep(BcDelay)

# Callback for close override being applied
def close_override_high(channel):
    print("Entering Close ovveride")
    # called when close override is pressed
    # always
    global switchSlct
    global breakerSlct
    print(GPIO.input(channel))    
    if GPIO.input(switchSlct):
    #    sleep(ScDelay)
        GPIO.output(output, 1)
        GPIO.output(redLED, 1)
        GPIO.output(greenLED, 0)
        print("sCov")
    #    sleep(SoDelay)
    elif GPIO.input(breakerSlct):
    #    sleep(BcDelay)
        GPIO.output(output, 1)
        GPIO.output(redLED, 1)
        GPIO.output(greenLED, 0)
        print("bCov")
    #    sleep(BoDelay)
    
# Callback from rotary encoder clk pin
def rot_clk_change(channel):
    # called when dial is rotated
    global dialChange
    global step
    
    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
    
    if clkState == 0 and dtState == 1:
        dialChange = dialChange - step

# Callback from rotary encoder dt pin
def rot_dt_change(channel):
    # called when dial is rotated
    global dialChange
    global step

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)

    if clkState == 1 and dtState == 0:
        dialChange = dialChange + step

# Function for checking rotary encoder switch pin (center press down)
def rot_sw_clicked(channel):
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
            cursorPos -= 1
            break
    

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
GPIO.add_event_detect(click, GPIO.RISING)
# case: Dial rotation
GPIO.add_event_detect(clk, GPIO.FALLING, bouncetime=btime)
GPIO.add_event_detect(dt, GPIO.FALLING, bouncetime=btime)

# Initial selector switch position check
if GPIO.input(switchSlct):
    # Go into switch operation
    slct_switch()

elif GPIO.input(breakerSlct):
    # Go into breaker operation
    slct_breaker()
else:
    disp.lcd_display_string("Error: No Device Selected ",2)

    
