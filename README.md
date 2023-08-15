# SteamDeckTouchPad

Very simple python script to use SteamDeck touchscreen (absolute positioning) as touchpad (relative positioning).

Requires xinput and evdev.

# Features

Turns crappy touchscreen experience into slightly less crappy big glowing touchpad.

Relative movements means it works on multiple displays, as expected from touchpad.

Working
- Movement
- Single left click
- Double left click (through native OS handling)
- Right click (hold press)

TODO
- click&drag (text selection, icon dragging)
- customization of speed, sensitivity, long press delay, etc.

# Required privileges

Either `sudo` or some chmoding on `/dev/input` as touchscreen device is root-only by default

# Limitations

As userland app it won't be detected by lower level stuff.

Doesn't click on-screen-keyboard, but trackpad writing still works.

Experience in games will be spotty at best. 
Point-and-click like Civilization should work fine, FPS with their lower level cursor grab tricks are unlikely to work.

And as its python script acting as middleware performance will be crap.

# Usage

Just run it:

`python touch.py`

Then kill script if you want to restore default behavior

# Overriding default touchscreen handling

Script does it automatically, but just in case its good to know how to do it manually

Disable default handler

`xinput disable "FTS3528:00 2808:1015"`

Enable default handler

`xinput ensable "FTS3528:00 2808:1015"`

#Requirements
[python3](https://wiki.archlinux.org/title/Python) 'cos thats what this is written in (`pacman -S python`)
[xinput](https://wiki.archlinux.org/title/Xinput) to install python packages (`pacman -S python-pip`)
[evdev](https://github.com/gvalkov/python-evdev) to read raw touchscreen events (`pip evdev`)
[pynput](https://github.com/moses-palmer/pynput) to simulate mouse events (`pip pynput`)
[xinput](https://wiki.archlinux.org/title/Xinput) for troubleshooting and optional automation (`pacman -S xinput`)

If script is ran as superuser (`sudo`) then python packages will need to be installed as such as well.

Installing some of that might need access to system directories, which by default is disabled on SteamOS
In which case you'll get annoying warnings/errors during installation so just run

`steamos-readonly disable`

Followed by 

`steamos-readonly enable`

If you want to restore safeguards

