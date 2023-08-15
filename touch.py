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
print('Disabling default touchscreen handling')
os.system('xinput disable "FTS3528:00 2808:1015"')

import evdev
from pynput import mouse, keyboard
def EvDevParser():
  movementMinDelta = 0
  movementScale = 1.5
  longPressSeconds = 1

  lastX = None
  lastY = None
  diffX = 0
  diffY = 0
  holding = False
  hasMovedAfterPress = False
  lastPressSec = 0
  m = mouse.Controller()

  devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
  device = next(d for d in devices if d.name == "FTS3528:00 2808:1015")
  print(device)
  print(device.capabilities(verbose=True))

  for event in device.read_loop():
    
    eventTimestampt = event.sec + event.usec/1000000
    timeElapsed = eventTimestampt - lastPressSec

    #TODO drag selection
    #TODO hold-and-drag

    if (event.type == 1) & (event.code == 330): #BTN_TOUCH
      # rest delta tracking
      lastX = None
      lastY = None
        
      # start tracking
      if (event.value == 1): #down (press)
        holding = True
        lastPressSec = eventTimestampt
        hasMovedAfterPress = False

      # left click
      if (event.value == 0) and holding: #up (release)
        
        if (not hasMovedAfterPress):
          if (timeElapsed > longPressSeconds):
            m.click(mouse.Button.right, 1)
          else:
            m.click(mouse.Button.left, 1)

        holding = False
        lastX = None
        lastY = None

    # SD touchscreen is physically a vertical screen, rotated left, so coords are swapped
    if (event.type == 3) and (event.code == 0) and holding: #ABS_X
      #print('Ypos = ',event.value)
      diffY = 0 if not lastY else (event.value - lastY)
      lastY = event.value
      if (diffY > movementMinDelta) or (diffY < -movementMinDelta):
        hasMovedAfterPress = True
        m.move(0,-diffY*movementScale)

    if (event.type == 3) and (event.code == 1) and holding: #ABS_X
      #print('Xpos = ',event.value)
      diffX = 0 if not lastX else (event.value - lastX)
      lastX = event.value
      if (diffX > movementMinDelta) or (diffX < -movementMinDelta):
        hasMovedAfterPress = True
        m.move(diffX*movementScale, 0)

def exit_handler():
  print('Enabling default touchsceen handling')
  os.system('xinput enable "FTS3528:00 2808:1015"')

try:
  EvDevParser()
except KeyboardInterrupt:
    exit_handler()
raise


import atexit


atexit.register(exit_handler)