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

from enum import Enum
class ClickMode(Enum):
  OnHold = 1
  OnRelease = 2
  OnMovement = 3

movementMinDelta = 0
movementScale = 2
longPressSeconds = 1
rightHoldSeconds = longPressSeconds/2
leftHoldSeconds = longPressSeconds/4

leftClickMode = ClickMode.OnRelease
rightClickMode = ClickMode.OnHold
leftDragEnabled = True

import os

def DisableTouchscreen():
  print('Disabling default touchscreen handling')
  os.system('xinput disable "FTS3528:00 2808:1015"')

import evdev
from pynput import mouse, keyboard
def TouchscreenAsTouchpad():

  deviceName = "FTS3528:00 2808:1015" #might not be same on every Steamdeck
  #so we better find by mask
  wantedDeviceNamePrefix = "FTS3528"
  unwantedDeviceNameSuffix = "UNKNOWN" #pen handler

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
  device = next((d for d in devices if (d.name.startswith(wantedDeviceNamePrefix) and not d.name.endswith(unwantedDeviceNameSuffix))), None)

  if device is None:
    print("Device ", deviceName, " not found. Terminating.")
    return

  DisableTouchscreen()
  m = mouse.Controller()

  print(device)
  print(device.capabilities(verbose=True))

  for event in device.read_loop():
    
    eventTimestampt = event.sec + event.usec/1000000
    timeElapsed = eventTimestampt - lastPressSec
        
    #check if any holdPress is enabled
    if holding and not hasMovedAfterPress:
      if (leftClickMode == ClickMode.OnHold) and (timeElapsed > leftHoldSeconds):
        m.click(mouse.Button.left, 1)
        holding = False
      if (rightClickMode == ClickMode.OnHold) and (timeElapsed > rightHoldSeconds):
        m.click(mouse.Button.right, 1)
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
            m.click(mouse.Button.right, 1)
          elif leftClickMode == ClickMode.OnRelease:
            m.click(mouse.Button.left, 1)

        if holding:
          m.release(mouse.Button.left)
        holding = False
        draging = False

    # SD touchscreen is physically a vertical screen, rotated left, so coords are swapped
    if (event.type == 3):
      if (event.code == 0) and holding: #ABS_X
        #print('Ypos = ',event.value)
        diffY = 0 if not lastY else (event.value - lastY)
        lastY = event.value
        if (diffY > movementMinDelta) or (diffY < -movementMinDelta):
          
          if not hasMovedAfterPress and leftDragEnabled and (timeElapsed > leftHoldSeconds):
            print("Starting left drag")
            draging = True
            m.press(mouse.Button.left)

          hasMovedAfterPress = True
          m.move(0,-diffY*movementScale)

    if (event.type == 3):
      if (event.code == 1) and holding: #ABS_X
        #print('Xpos = ',event.value)
        diffX = 0 if not lastX else (event.value - lastX)
        lastX = event.value
        if (diffX > movementMinDelta) or (diffX < -movementMinDelta):
          
          if not hasMovedAfterPress and leftDragEnabled and (timeElapsed > leftHoldSeconds):
            print("Starting left drag")
            draging = True
            m.press(mouse.Button.left)

          hasMovedAfterPress = True
          m.move(diffX*movementScale, 0)
          

def EnableTouchscreen():
  print('Enabling default touchsceen handling')
  os.system('xinput enable "FTS3528:00 2808:1015"')

try:
  TouchscreenAsTouchpad()
except KeyboardInterrupt:
    EnableTouchscreen()
raise


import atexit


atexit.register(EnableTouchscreen)