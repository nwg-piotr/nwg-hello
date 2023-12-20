# nwg-hello

This program is a part of the [nwg-shell](https://nwg-piotr.github.io/nwg-shell) project.

Nwg-hello is a GTK3-based greeter for the [greetd](https://git.sr.ht/~kennylevinsen/greetd) daemon, written in python.
It is meant to work under a Wayland compositor, like [sway](https://swaywm.org) or [Hyprland](https://hyprland.org). 
It __does not support X11__ sessions. The greeter has been developed for the [nwg-iso](https://github.com/nwg-piotr/nwg-iso) 
project, but it may be configured for standalone use.

![image](https://github.com/nwg-piotr/nwg-hello/assets/20579136/12da658f-ff2f-4a60-b5e4-797175928ebc)

The screen layout is heavily inspired by [Sugar Candy SDDM theme](https://framagit.org/MarianArlt/sddm-sugar-candy) 
by Marian Arlt;

## Features

- multi-monitor support with gtk-layer-shell
- multi-language support
- background & style customization with css
- automatic selection of the last used session and user
- support for setting environment variables

## Dependencies

- python >= 3.6
- greetd
- gtk3
- gtk-layer-shell
- Hyprland or sway Wayland compositor
- gnome-themes-extra - recommended as it provides us with the default Adwaita theme.

## Installation

The greeter can be installed by cloning this repository and executing the `install.sh` script (make sure you installed
dependencies first). Then you need to edit the `/etc/greetd/config.toml` file (or `greeter.conf` - see the tip below).

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

__Do not change the__ `user = "greeter"` __line__, or some file-related functions won't work.  

### Tip

During the greetd package upgrades, the `config.toml` file may be overwritten with the default one. E.g. on Arch Linux
your modified file gets renamed to `config.toml.pacsave`. This will restore the `agreety` greeter on your system.
To avoid such a situation, you may use the alternative `greeter.conf` file. This has not been mentioned in docs, 
but greetd looks for this file first. Just copy `config.toml` to `greetd.conf` and make changes to the copy.

## Configuration

Copy `/etc/nwg-hello/nwg-hello-default.json` to `/etc/nwg-hello/nwg-hello.json` and make your changes there.

```json
{
  "session_dirs": [
    "/usr/share/wayland-sessions"
  ],
  "custom_sessions": [
    {
      "name": "Shell",
      "exec": "/usr/bin/bash"
    }
  ],
  "monitor_nums": [],
  "delay_secs": 1,
  "cmd-sleep": "systemctl suspend",
  "cmd-reboot": "systemctl reboot",
  "cmd-poweroff": "systemctl poweroff",
  "gtk-theme": "Adwaita",
  "gtk-icon-theme": "",
  "gtk-cursor-theme": "",
  "prefer-dark-theme": true,
  "lang": "",
  "env-vars": []
}
```

- `"session_dirs"`: comma-separated paths to session directories. We don't include `/usr/share/xsessions` here, as we don't support them.
- `"custom_sessions"`: greetd can run whatever starts from the command line. This way we can add `bash`, `zsh` or something else here.
- `"monitor_nums"`: leave as is to see the greeter on all monitors. Set e.g. `[0, 2]` for it to appear on the 1st and 3rd one.
- `"delay_secs"`: some monitors take longer to turn on. In the meantime the greeter may behave oddly on other monitors. If it happens to restart/blink, increase this value. If you only have one monitor and no discrete GPU, you may probably set `0` here.
- `"cmd-sleep"`, `"cmd-reboot"`, and `"cmd-poweroff"` are pre-defined for systemd-based systems. Use whatever works for you.
- `"gtk-theme"`, `"gtk-icon-theme"` and `"gtk-cursor-theme"` are of little importance as long, as you use the default css style sheet.
- `"prefer-dark-theme"` should remain `true` unless you need to turn it off with your own styling.
- `"lang"` allows you to force the use of a specific language, regardless of the `$LANG` system variable. Check if we have the translation in the [langs directory](https://github.com/nwg-piotr/nwg-hello/tree/main/nwg_hello/langs).
- `"env-vars"` allows to pass an array of environment variables. Use like this: `["MY_VAR=value", "OTHER_VAR=value1"]`.

## Styling

Copy `/etc/nwg-hello/nwg-hello-default.css` to `/etc/nwg-hello/nwg-hello.css` and make your changes there.

## Power icons

If you'd like to use own icons, do not replace `*-default.svg` files. Place your `poweroff.svg`, `reboot.svg` and
`sleep.svg` files in the same directory.

## Acknowledgments

- [@milisarge](https://gist.github.com/milisarge) for [the snippet](https://gist.github.com/milisarge/d169756e316e185572605699e73ed3ae) that let me know how things work;
- [Marian Arlt](https://framagit.org/MarianArlt) for inspiring look of the Sugar Candy SDDM theme. 