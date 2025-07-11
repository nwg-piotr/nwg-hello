# nwg-hello

This program is a part of the [nwg-shell](https://nwg-piotr.github.io/nwg-shell) project.

Nwg-hello is a GTK3-based greeter for the [greetd](https://git.sr.ht/~kennylevinsen/greetd) daemon, written in python.
It is meant to work under a Wayland compositor, like [sway](https://swaywm.org) or [Hyprland](https://hyprland.org) (also see: 
[Running on Debian and labwc](#running-on-debian-and-labwc)).
The greeter has been developed for the [nwg-iso](https://github.com/nwg-piotr/nwg-iso) project, but it may be configured for standalone use.

<img src="https://github.com/user-attachments/assets/615da463-675e-4cd0-9963-03e6f7d43175" width=640 alt="Screenshot"><br>

_The screen layout is heavily inspired by [Sugar Candy SDDM theme](https://framagit.org/MarianArlt/sddm-sugar-candy) 
by Marian Arlt._

## Background

I was in need of a good login manager for the nwg-iso project. I first used SDDM with the Sugar Candy theme, and it
worked pretty well. However, it brings QT dependencies, and my stuff is all GTK-based. Also, I know nothing about the QT
framework, so couldn't adjust the greeter to my taste. The next choice was LightDM with [my modification](https://github.com/nwg-piotr/lightdm-nwg-greeter)
of the [LightDM Elephant Greeter](https://github.com/max-moser/lightdm-elephant-greeter) by Maximilian Moser. It looked well, but LightDM would happen to hang way too 
often. Then I gave a try to greetd, and that was it. I only needed a nice graphical greeter based on GTK3. Since there 
was no such thing, I had to develop one.

## Features

- Multi-monitor support with gtk-layer-shell;
- multi-language support;
- background and style customization with CSS;
- automatic selection of the last used session and user;
- avatar (user picture) support;
- support for setting environment variables.

## Dependencies

- python >= 3.6;
- greetd;
- gtk3;
- gtk-layer-shell;
- Hyprland or sway Wayland compositor;
- gnome-themes-extra.

## Make dependencies

- python-build
- python-installer
- python-wheel
- python-setuptools

## Optional dependencies

- mugshot: to set the user picture

## Installation

[![Packaging status](https://repology.org/badge/vertical-allrepos/nwg-hello.svg)](https://repology.org/project/nwg-hello/versions)

First, you need to [install and start greetd](https://wiki.archlinux.org/title/Greetd#Installation).

The greeter can be installed as a package for your Linux distribution, or by cloning this repository and executing the 
`install.sh` script (make sure you installed dependencies first). 

Then you need to edit the `/etc/greetd/config.toml` file (or `greetd.conf` - see the tip below).

```toml
[terminal]
# The VT to run the greeter on. Can be "next", "current" or a number
# designating the VT.
vt = 1

# The default session, also known as the greeter.
[default_session]

# `agreety` is the bundled agetty/login-lookalike. You can replace `/bin/sh`
# with whatever you want started, such as `sway`.
command = "agreety --cmd /bin/sh"

# The user to run the command as. The privileges this user must have depends
# on the greeter. A graphical greeter may for example require the user to be
# in the `video` group.
user = "greeter"
```

Replace the line:

```toml
command = "agreety --cmd /bin/sh"
```

with

```toml
command = "Hyprland -c /etc/nwg-hello/hyprland.conf"
```

if you want to use Hyprland, or this line if you prefer sway:

```toml
command = "sway -c /etc/nwg-hello/sway-config"
```

NOTE: you may need `sway --unsupported-gpu` for Nvidia. Also, if you'd like to make some additional configuration
(e.g., monitor layout), edit `/etc/nwg-hello/hyprland.conf` or `/etc/nwg-hello/sway-config`, respectively.

__Do not change the__ `user = "greeter"` __line__, or some file-related functions won't work.  

### Tip

During the greetd package upgrades, the `config.toml` file may be overwritten with the default one. E.g., on Arch Linux
your modified file gets renamed to `config.toml.pacsave`. This will restore the `agreety` greeter on your system.
To avoid such a situation, you may use the alternative `greetd.conf` file. This has not been mentioned in docs, 
but greetd looks for this file first. Just copy `config.toml` to `greetd.conf` and make changes to the copy.

## Configuration

Copy `/etc/nwg-hello/nwg-hello-default.json` to `/etc/nwg-hello/nwg-hello.json` and make your changes there.

```json
{
  "session_dirs": [
    "/usr/share/wayland-sessions",
    "/usr/share/xsessions"
  ],
  "custom_sessions": [
    {
      "name": "Shell",
      "exec": "/usr/bin/bash"
    }
  ],
  "monitor_nums": [],
  "form_on_monitors": [],
  "delay_secs": 1,
  "cmd-sleep": "systemctl suspend",
  "cmd-reboot": "systemctl reboot",
  "cmd-poweroff": "systemctl poweroff",
  "gtk-theme": "Adwaita",
  "gtk-icon-theme": "",
  "gtk-cursor-theme": "",
  "prefer-dark-theme": true,
  "template-name": "",
  "time-format": "%H:%M:%S",
  "date-format": "%A, %d. %B",
  "layer": "overlay",
  "keyboard-mode": "exclusive",
  "lang": "",
  "avatar-show": false,
  "avatar-size": 100,
  "avatar-border-width": 1,
  "avatar-border-color": "#eee",
  "avatar-corner-radius": 15,
  "avatar-circle": false,
  "env-vars": []
}
```

- `"session_dirs"`: comma-separated paths to session directories. Modify only if you know well what you're doing.
- `"custom_sessions"`: greetd can run whatever starts from the command line. This way we can add `bash`, `zsh` or something else here. The `"name"` field is the display name. The `"exec"` field is a command.
- `"monitor_nums"`: leave as is to see the greeter on all monitors. Set e.g. `[0, 2]` for it to appear on the 1st and 3rd one.
- `"form_on_monitors"`: which of above monitors to display the login form on (just the wallpaper on the rest).
- `"delay_secs"`: some monitors take longer to turn on. In the meantime the greeter may behave oddly on other monitors. If it happens to restart/blink, increase this value. If you only have one monitor and no discrete GPU, you may probably set `0` here.
- `"cmd-sleep"`, `"cmd-reboot"`, and `"cmd-poweroff"` are pre-defined for systemd-based systems. Use whatever works for you.
- `"gtk-theme"`, `"gtk-icon-theme"` and `"gtk-cursor-theme"` are of little importance as long, as you use classes and IDs from the default css style sheet.
- `"prefer-dark-theme"` should remain `true`, unless you need to turn it off for use with your own background and/or styling.
- `"template-name"` allows use of own templates: find the built-in `/usr/lib/python3.xx/site-packages/nwg_hello-x.y.z-py3.xx.egg/nwg_hello/template.glade` file, copy to a folder somewhere in `~/`, edit and place as `/etc/nwg-hello/file-name.glade`. Do not change widget IDs. Set your `file-name.glade` as the `"template-name"` value. Leave blank to use the built-in template.
- `"time-format"`: string to format clock with the strftime() function (see: https://www.man7.org/linux/man-pages/man3/strftime.3.html).
- `"date-format"`: string to format date with the strftime() function (see: https://www.man7.org/linux/man-pages/man3/strftime.3.html).
- `"layer"`: allows choosing gtk-layer-shell layer: 'background', 'bottom', 'top', 'overlay'; 'overlay' will be used if no value given.
- `"keyboard-mode"`: allows choosing gtk-layer-shell keyboard mode: 'none', 'exclusive', 'on_demand'; 'exclusive' will be used if no value given.
- `"lang"` allows you to force the use of a specific language, regardless of the `$LANG` system variable. Check if we have the translation in the [langs directory](https://github.com/nwg-piotr/nwg-hello/tree/main/nwg_hello/langs).
- `"avatar-show"`: determines whether to display the user's profile picture.
- `"avatar-size"`: avatar image size in pixels.
- `"avatar-border-width"`: avatar border width in pixels.
- `"avatar-border-color"`: a hexadecimal value of avatar border color ("#rgb" or "#rrggbb").
- `"avatar-corner-radius"`: corner radius for rectangular avatar image,
- `"avatar-circle"`: draw avatar as a circle (corner radius ignored),
- `"env-vars"` allows to pass an array of environment variables. Use like this: `["MY_VAR=value", "OTHER_VAR=value1"]`.

## Styling

Copy `/etc/nwg-hello/nwg-hello-default.css` to `/etc/nwg-hello/nwg-hello.css` and make your changes there.

## Custom icons

If you'd like to use your own icons, do not replace `/usr/share/nwg-hello/*-default.svg` files. Place your 
`poweroff.svg`, `reboot.svg`, `sleep.svg` and `avatar.svg` files in the same directory. Attention: the `avatar.svg` file
is not your profile picture, but a generic user image!

## Own language files

You can't translate labels in the .glade file, as the program replaces the values with what's defined in 
[language files](https://github.com/nwg-piotr/nwg-hello/tree/main/nwg_hello/langs). Since the 0.2.4 version, however, 
you can copy your lang file to `/etc/nwg-hello/` and make desired changes there, 
see https://github.com/nwg-piotr/nwg-hello/issues/19. Be careful with syntax, the JSON format is unforgiving.
Test your lang file by running `nwg-hello -t -d` from terminal.

## User avatar

New in version 0.4.0. Disabled in default config. Set `"avatar-show": true` to enable.

The feature displays user's profile picture from `/var/lib/AccountsService/icons/$USERNAME`, stored by 
gnome-control-center or some other tool ([Mugshot](https://github.com/bluesabre/mugshot) does the job perfectly well). See [Configuration](#configuration)
for related values.

Styling: no CSS is applicable here. You can set shape- and border-related values in config.

NOTE: if you use your customized `/etc/nwg-hello/nwg-hello.json` file, remember to copy all `avatar-*` key-value pairs
from `/etc/nwg-hello/nwg-hello-default.json`.

## Running on Debian and labwc

Submitted by [@01micko](https://github.com/01micko).

### configs

#### /etc/greetd/greetd.conf

```toml
[terminal]
# The VT to run the greeter on. Can be "next", "current" or a number
# designating the VT.
vt = 7

# The default session, also known as the greeter.
[default_session]

command = "labwc --config-dir /etc/nwg-hello/labwc-config"

# The user to run the command as. The privileges this user must have depends
# on the greeter. A graphical greeter may for example require the user to be
# in the `video` group.
user = "_greetd"
```

NOTE: The user `_greetd` is a debian thing, even though it isn't set up correctly. You have to manually add to 'video' 
group and `chown` all the files in `/etc/greetd`.

#### /etc/nwg-hello/labwc-config/autostart

```sh
# start nwg-hello - full paths aren't required, but saves lookup time
exec /usr/bin/nwg-hello; /usr/bin/labwc --exit
```

#### /etc/nwg-hello/labwc-config/rc.xml (optional)
- only if you want a screenshot (using `PrtScr` key) of `nwg-hello` saved to /etc/greetd/

```xml
 <?xml version="1.0" ?>
<labwc_config>

  <keyboard>
    <default />
    <keybind key="Print"><action name="Execute" command="grim" /></keybind>
  </keyboard>

</labwc_config>
```

## Session files on NixOS

On NixOS it may be necessary to add `"/share/wayland-sessions"` and/or `"/share/xsessions"` to `environment.pathsToLink` to ensure that the session files are available in the correct location.

## Acknowledgments

- [@milisarge](https://gist.github.com/milisarge) for [the snippet](https://gist.github.com/milisarge/d169756e316e185572605699e73ed3ae) that let me know how things work;
- [Marian Arlt](https://framagit.org/MarianArlt) for inspiring look of the Sugar Candy SDDM theme.
