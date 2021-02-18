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
switch_textRefreshSpeed = 0.35
breaker_textRefreshSpeed = 0.1

# Row selection variable set to something > 2 so it can't change the variables
clickedRot = 3
# Get Switch Initial Values
SoDelayMin = initVals.Switch_OpenDelay_min
SoDelayMax = initVals.Switch_OpenDelay_max
SoTs = initVals.Switch_OpenTimestep
ScDelayMin = initVals.Switch_CloseDelay_min
ScDelayMax = initVals.Switch_CloseDelay_max
ScTs = initVals.Switch_CloseTimestep

# Switch Center Values:
SoDelay = (SoDelayMax - SoDelayMin)/2
ScDelay = (ScDelayMax - SoDelayMin)/2
# SoDelay = SoDelayMin
# ScDelay = ScDelayMin

# Get Breaker Initial Values
conversionFactor = 1000
BoDelayMin = initVals.Breaker_OpenDelay_min * conversionFactor
BoDelayMax = initVals.Breaker_OpenDelay_max * conversionFactor
BoTs = initVals.Breaker_OpenTimestep * conversionFactor
BcDelayMin = initVals.Breaker_CloseDelay_min * conversionFactor
BcDelayMax = initVals.Breaker_CloseDelay_max * conversionFactor
BcTs = initVals.Breaker_CloseTimestep * conversionFactor

# Breaker Center Values:
BoDelay = (BoDelayMax - BoDelayMin)/2
BcDelay = (BcDelayMax - BoDelayMin)/2
# BoDelay = BoDelayMin
# BcDelay = BcDelayMin

# Dial initial values:
counter = 0
step = 1
dialChange = 0
# bounctime -- if set too high this will slow down the max spped the dial will respond to
btime = 90
longPress = False

# ==== Definition of functions ====

def slct_switch():
    # called when selection is switch simulation
    # always
    global switchSlct
    global clickedRot
    global encoder
    global textRefreshSpeed
    
    clickedRot = 0

    # Functions used while switch is the selected device
    # Resets the delay values
    def reset():
        global SoDelay
        global ScDelay
        global clickedRot
        SoDelay = (SoDelayMax - SoDelayMin)/2
        ScDelay = (ScDelayMax - SoDelayMin)/2
        clickedRot = 0
        
    def updateDelays():
        global SoDelay
        global ScDelay
        global clickedRot
        global dialChange

        if dialChange == 2 or dialChange == -2:
            dialChange = dialChange*10
        elif dialChange > 2 or dialChange < -2:
            dialChange = dialChange*100
            
        OpossibleNextValue = SoDelay + dialChange*SoTs
        CpossibleNextValue = ScDelay + dialChange*ScTs
        dialChange = 0
        # check that this is within bounds
        # First for the open delay
        if clickedRot == 1 and OpossibleNextValue >= SoDelayMin and OpossibleNextValue <= SoDelayMax:
            SoDelay = OpossibleNextValue
        elif clickedRot == 1 and OpossibleNextValue < SoDelayMin:
            SoDelay = SoDelayMin
        elif clickedRot == 1 and OpossibleNextValue > SoDelayMax:
            SoDelay = SoDelayMax
        # Now if close delay is selected
        elif clickedRot == 2 and CpossibleNextValue >= ScDelayMin and CpossibleNextValue <= ScDelayMax:
            ScDelay = CpossibleNextValue
        elif clickedRot == 2 and CpossibleNextValue < ScDelayMin:
            ScDelay = ScDelayMin
        elif clickedRot == 2 and CpossibleNextValue > ScDelayMax:
            ScDelay = ScDelayMax
        elif clickedRot > 2:
            pass

    # Make display row selection Variable (clickedRot)                                           
    # 0 = no row (Both locked)                                                      
    # 1 = Open delay selected and ready for adjustment                              
    # 2 = Close delay selected and ready for adjustment
    # 3 = reset to 0 (Both locked)
    disp.lcd_display_string("Simulating: Switch ", 1)
    disp.lcd_display_string("*push dial for next*", 2)
    disp.lcd_display_string("Open Dly:  L   {:.2f}s".format(SoDelay),3)
    disp.lcd_display_string("Close Dly: L   {:.2f}s".format(ScDelay),4)
        
    while GPIO.input(switchSlct):
        # Be a switch simulator
        # Selection change based on row variable

        if longPress:
            reset()

        sleep(switch_textRefreshSpeed)
        updateDelays()
        if clickedRot == 0:
            disp.lcd_display_string("Open Dly:  L   {:.2f}s".format(SoDelay),3)
            disp.lcd_display_string("Close Dly: L   {:.2f}s".format(ScDelay),4)
        elif clickedRot == 1:
            disp.lcd_display_string("Open Dly:      {:.2f}s".format(SoDelay),3)
            disp.lcd_display_string("Close Dly: L   {:.2f}s".format(ScDelay),4)
        elif clickedRot == 2:
            disp.lcd_display_string("Open Dly:  L   {:.2f}s".format(SoDelay),3)
            disp.lcd_display_string("Close Dly:     {:.2f}s".format(ScDelay),4)
        elif clickedRot == 3:
            clickedRot = 0

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
    global clickedRot
    global encoder

    clickedRot = 0

    # Functions used while simulating a breaker
    # Resets all delay values to the default values
    def reset():
        global BoDelay
        global BcDelay
        global clickedRot
        BoDelay = (BoDelayMax - BoDelayMin)/2
        BcDelay = (BcDelayMax - BoDelayMin)/2
        clickedRot = 0
        
    def updateDelays():
        global BoDelay
        global BcDelay
        global clickedRot
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
        if clickedRot == 1 and OpossibleNextValue >= BoDelayMin and OpossibleNextValue <= BoDelayMax:
            BoDelay = OpossibleNextValue
        elif clickedRot == 1 and OpossibleNextValue < BoDelayMin:
            BoDelay = BoDelayMin
        elif clickedRot == 1 and OpossibleNextValue > BoDelayMax:
            BoDelay = BoDelayMax
        # Now if close delay is selected                                                                                                                                          
        elif clickedRot == 2 and CpossibleNextValue >= BcDelayMin and CpossibleNextValue <= BcDelayMax:
            BcDelay = CpossibleNextValue
        elif clickedRot == 2 and CpossibleNextValue < BcDelayMin:
            BcDelay = BcDelayMin
        elif clickedRot == 2 and CpossibleNextValue > BcDelayMax:
            BcDelay = BcDelayMax
        elif clickedRot > 2:
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
        sleep(breaker_textRefreshSpeed)
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
        
        
        if clickedRot == 0:
            disp.lcd_display_string("Open Dly:  L   {}ms".format(oDelayAsString),3)
            disp.lcd_display_string("Close Dly: L   {}ms".format(cDelayAsString),4)
        elif clickedRot == 1:
            disp.lcd_display_string("Open Dly:      {}ms".format(oDelayAsString),3)
            disp.lcd_display_string("Close Dly: L   {}ms".format(cDelayAsString),4)
        elif clickedRot == 2:
            disp.lcd_display_string("Open Dly:  L   {}ms".format(oDelayAsString),3)
            disp.lcd_display_string("Close Dly:     {}ms".format(cDelayAsString),4)
        elif clickedRot == 3:
            clickedRot = 0

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

# Callback from rotary encoder switch pin (center press down)
def rot_sw_clicked(channel):
    global clickedRot
    global longPress
    clickedRot += 1
    sleep(0.5)

    while GPIO.input(channel):
        longPress = True
    longPress = False
    

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

    
