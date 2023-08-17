# SteamDeckTouchPad

Very simple python script to use SteamDeck touchscreen (absolute positioning) as touchpad (relative positioning).

No pemanent configuration changes required, just some easily reinstalable packages. Which is good, as SteamOS update might wipe custom stuff away.

Works when built-in screen is disabled.

# Features

Turns crappy touchscreen experience into slightly less crappy big glowing touchpad.

Relative movements means it works on multiple displays, as expected from touchpad.

Working
- Movement
- Single left click
- Double left click (through native OS handling)
- Right click (hold press)
- click&drag (text selection, icon dragging)
- customization of speed, sensitivity, long press delay, etc.

TODO
- click&drag (text selection, icon dragging)
- customization of speed, sensitivity, long press delay, etc.
- gestures for scroll

# Required privileges

Either `sudo` or some chmoding on `/dev/input` as touchscreen device is root-only by default

# Limitations

Not tested in Game Mode. Only in Desktop.

As userland app it won't be detected by lower level stuff.

Doesn't click on-screen-keyboard, but trackpad writing still works.

Experience in games will be spotty at best. 
Point-and-click like Civilization should work fine, FPS with their lower level cursor grab tricks are unlikely to work.

And as its python script acting as middleware performance will be crap.

# Usage

Just run it:

`python touch.py`

Then kill script if you want to restore default behavior

## Config

```options:
  -h, --help            show this help message and exit
  -s seconds, --shortPressSeconds seconds
                        Time required to activate Short Press action in seconds. (default: 0.2)
  -l seconds, --longPressSeconds seconds
                        Time required to activate Long Press action in seconds. (default: 0.4)
  -D, --disableDrag     Disables LMB drag mode which occurs after LMB has been pressed for shortPressSeconds. (default: False)
  -L {OnHold,OnRelease}, --leftClickMode {OnHold,OnRelease}
                        Controlls whether LMB click occurs after timer or after releasing finger. (default: OnRelease)
  -R {OnHold,OnRelease}, --rightClickMode {OnHold,OnRelease}
                        Controlls whether RMB click occurs after timer or after releasing finger. (default: OnHold)
  -m delta, --movementMinDelta delta
                        Minimum distance per tick to invoke mouse movement, increase to compensate for unsteady fingers. (default: 0.0)
  -v multiplier, --movementVelocity multiplier
                        Multiplier for mouse speed. Increase to compensate for high resolution screen. (default: 2.0)
  -T prefix, --touchscreenDeviceNamePrefix prefix
                        Prefix for touchscreen device to query /dev/input/event* for. (default: FTS3528)
  -P suffix, --penDeviceNameSuffix suffix
                        Suffix for touchscreen pen device to ignore while querying /dev/input/event*. (default: UNKNOWN)```


# Overriding default touchscreen handling

Script does it automatically, but just in case its good to know how to do it manually

Disable default handler

`xinput disable "FTS3528:00 2808:1015"`

Enable default handler

`xinput ensable "FTS3528:00 2808:1015"`

Requirements
- [python3](https://wiki.archlinux.org/title/Python) 'cos thats what this is written in (`pacman -S python`)
- [pip](https://wiki.archlinux.org/title/Xinput) to install python packages (`pacman -S python-pip`)
- [evdev](https://github.com/gvalkov/python-evdev) to read raw touchscreen events (`pip evdev`)
- [pynput](https://github.com/moses-palmer/pynput) to simulate mouse events (`pip pynput`)
- [xinput](https://wiki.archlinux.org/title/Xinput) for troubleshooting and optional automation (`pacman -S xinput`)

If script is ran as superuser (`sudo`) then python packages will need to be installed as such as well.

Installing some of that might need access to system directories, which by default is disabled on SteamOS
In which case you'll get annoying warnings/errors during installation so just run

`steamos-readonly disable`

Followed by 

`steamos-readonly enable`

If you want to restore safeguards

# Game Compatibility

Script is made for desktop experience, so only games using mouse like desktop does will work fine.

Games that will probably not work:
- Shooters, be it 2D or 3D. Good aiming requires cursor capture/lock and/or raw input. Neither of which will work with userland script.
- Games with 3D camera. For same reason as shooters.
- Games running in exclusive (true) fullscreen.
- Games with anti-cheat/anti-bot, as it uses same techniques as bad bots do.

Games that will probably work:
- Simple adventure point-and-click
- Strategy games
- Windowed/borderless without cursor capture

Confirmed working games
- [XCOM EW](https://store.steampowered.com/app/225340/XCOM_Enemy_Within/)
- [Civilization 5](https://store.steampowered.com/app/8930/Sid_Meiers_Civilization_V/)

Confirmed broken games
- [Crimsonland](https://store.steampowered.com/app/262830/Crimsonland/) (standard shooter aiming issues with fake mouse)
