#Simple script for simulating relative touchpad out of absolute touchscreen events
#Written for SteamDeck, but basic idea should work on RPi touchscreens as well

#requires evdev https://github.com/gvalkov/python-evdev (for processing raw input)
#requires pynput https://github.com/moses-palmer/pynput (for simulating touchpad)

#touchscreen should be named like FTS3528:00 2808:1015 (without UNKNOWN suffix, thats some stylus crap)
#touchscreen is /dev/input with root privileges by default, so sudo or chmod is required
#xinput accepts friendly name, evtest requires id. No idea if eventId is constant

#xinput list
#evtest

#disable SD touchscreen
#xinput disable "FTS3528:00 2808:1015"
#xinput enable "FTS3528:00 2808:1015"

#monitor SD touchscreen and list event codes
#evtest /dev/input/event5
#xinput test "FTS3528:00 2808:1015"

import os
import evdev
import argparse
from enum import Enum
from pynput import mouse, keyboard

class ClickMode(Enum):
  OnHold = 1
  OnRelease = 2

  @classmethod
  def from_string(cls, str):
    match str:
      case "OnHold":
        return ClickMode.OnHold
      case "OnRelease":
        return ClickMode.OnRelease
      case _:
        raise Exception("Unknown value: "+str)
  @classmethod
  def to_string(cls):
    match cls:
      case ClickMode.OnHold:
        return "OnHold"
      case ClickMode.OnRelease:
        return "OnRelease"
      case _:
        raise Exception("Unknown value: "+str)

# default config
movementMinDelta = 0
movementScale = 2
longPressSeconds = 1
shortPressSeconds = longPressSeconds/2
leftClickMode = ClickMode.OnRelease
rightClickMode = ClickMode.OnHold
leftDragEnabled = True
#on my SD it was "FTS3528:00 2808:1015" but it might not be same on every machine
touchscreenDeviceName = "FTS3528:00 2808:1015";
#so we better find by mask
touchscreenDeviceNamePrefix = "FTS3528"
penDeviceNameSuffix = "UNKNOWN" #pen handler shares device name with touchscreen
LMB = mouse.Button.left
RMB = mouse.Button.right

def CLI(): 
  #TODO refactor this crap into some config object
  global movementMinDelta, movementScale, longPressSeconds, shortPressSeconds, leftClickMode, rightClickMode, leftDragEnabled
  global touchscreenDeviceName, touchscreenDeviceNamePrefix, penDeviceNameSuffix
  global LMB, RMB

  parser = argparse.ArgumentParser(description="Steamdeck Touchpad",
                                  formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("-s", "--shortPressSeconds", metavar = "seconds", type = float, default = 0.2, 
    help = "Time required to activate Short Press action in seconds.")
  parser.add_argument("-l", "--longPressSeconds", metavar = "seconds", type = float, default = 0.4, 
    help = "Time required to activate Long Press action in seconds.")

  parser.add_argument("-M", "--mirrorButtons", action = "store_true", default = False, 
    help = "Switches LMB and RMB behavior")
  parser.add_argument("-D", "--disableDrag", action = "store_true", default = False, 
    help = "Disables LMB drag mode which occurs after LMB has been pressed for shortPressSeconds.")
  parser.add_argument("-L", "--leftClickMode", choices=['OnHold', 'OnRelease'], default = 'OnRelease', 
    help = "Controlls whether LMB click occurs after timer or after releasing finger.")
  parser.add_argument("-R", "--rightClickMode", choices=['OnHold', 'OnRelease'], default = 'OnHold', 
    help = "Controlls whether RMB click occurs after timer or after releasing finger.")

  parser.add_argument("-m", "--movementMinDelta", metavar = "delta", type = float, default = 0.0, 
    help = "Minimum distance per tick to invoke mouse movement, increase to compensate for unsteady fingers.")
  parser.add_argument("-v", "--movementVelocity", metavar = "multiplier", type = float, default = 2.0, 
    help = "Multiplier for mouse speed. Increase to compensate for high resolution screen.")

  parser.add_argument("-T", "--touchscreenDeviceNamePrefix", metavar = "prefix", default = "FTS3528", 
    help = "Prefix for touchscreen device to query /dev/input/event* for.")
  parser.add_argument("-P", "--penDeviceNameSuffix", metavar = "suffix", default = "UNKNOWN", 
    help = "Suffix for touchscreen pen device to ignore while querying /dev/input/event*.")
  
  args = parser.parse_args()
  config = vars(args)

  shortPressSeconds = config["shortPressSeconds"]
  longPressSeconds = config["longPressSeconds"]

  leftDragEnabled = not config["disableDrag"]
  leftClickMode = ClickMode.from_string(config["leftClickMode"])
  rightClickMode = ClickMode.from_string(config["rightClickMode"])

  movementMinDelta = config["movementMinDelta"]
  movementVelocity = config["movementVelocity"]

  touchscreenDeviceNamePrefix = config["touchscreenDeviceNamePrefix"]
  penDeviceNameSuffix = config["penDeviceNameSuffix"]

  if config["mirrorButtons"]:
    LMB = mouse.Button.right
    RMB = mouse.Button.left

CLI()

def TouchscreenAsTouchpad():

  lastX = None
  lastY = None
  diffX = 0
  diffY = 0
  holding = False
  draging = False
  hasMovedAfterPress = False
  lastPressSec = 0

  #try to locate /dev/input/event[id] without hardocidng device name or id
  devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
  device = next((d for d in devices if (d.name.startswith(touchscreenDeviceNamePrefix) and not d.name.endswith(penDeviceNameSuffix))), None)
  touchscreenDeviceName = device.name
  
  if device is None:
    print("Touchscreen device not found. Terminating.")
    return

  m = mouse.Controller()

  #print(device)
  #print(device.capabilities(verbose=True))

  device.grab()

  for event in device.read_loop():
    
    eventTimestampt = event.sec + event.usec/1000000
    timeElapsed = eventTimestampt - lastPressSec
        
    #check if any holdPress is enabled
    if holding and not hasMovedAfterPress:
      if (leftClickMode == ClickMode.OnHold) and (timeElapsed > shortPressSeconds):
        m.click(LMB, 1)
        holding = False
      if (rightClickMode == ClickMode.OnHold) and (timeElapsed > longPressSeconds):
        m.click(RMB, 1)
        holding = False

    if (event.type == 1) & (event.code == 330): #BTN_TOUCH
      # reset delta tracking
      lastX = None
      lastY = None
        
      # start tracking
      if (event.value == 1): #down (press)

        holding = True
        lastPressSec = eventTimestampt
        hasMovedAfterPress = False

      if (event.value == 0) and holding: #up (release)
        
        if (not hasMovedAfterPress):
          if (timeElapsed > longPressSeconds) and (rightClickMode == ClickMode.OnRelease):
            m.click(RMB, 1)
          elif leftClickMode == ClickMode.OnRelease:
            m.click(LMB, 1)

        if holding:
          m.release(LMB)
        holding = False
        draging = False

    # SD touchscreen is physically a vertical screen, rotated left, so coords are swapped
    if (event.type == 3):
      if (event.code == 0) and holding: #ABS_X
        #print('Ypos = ',event.value)
        diffY = 0 if not lastY else (event.value - lastY)
        lastY = event.value
        if (diffY > movementMinDelta) or (diffY < -movementMinDelta):
          
          if not hasMovedAfterPress and leftDragEnabled and (timeElapsed > shortPressSeconds):
            draging = True
            m.press(LMB)

          hasMovedAfterPress = True
          m.move(0,-diffY*movementScale)

    if (event.type == 3):
      if (event.code == 1) and holding: #ABS_X
        #print('Xpos = ',event.value)
        diffX = 0 if not lastX else (event.value - lastX)
        lastX = event.value
        if (diffX > movementMinDelta) or (diffX < -movementMinDelta):
          
          if not hasMovedAfterPress and leftDragEnabled and (timeElapsed > shortPressSeconds):
            draging = True
            m.press(LMB)

          hasMovedAfterPress = True
          m.move(diffX*movementScale, 0)

try:
  TouchscreenAsTouchpad()
except KeyboardInterrupt:
  #ignore CTRL+C
  pass