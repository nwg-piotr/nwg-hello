#!/usr/bin/env bash

install -D -m 644 -t /etc/nwg-hello/ nwg-hello-default.json
install -D -m 644 -t /etc/nwg-hello/ nwg-hello-default.css
install -D -m 644 -t /etc/nwg-hello/ hyprland.conf
install -D -m 644 -t /etc/nwg-hello/ README
install -D -m 644 -t /usr/share/nwg-hello/ nwg.jpg
install -D -m 644 -t /usr/share/nwg-hello/ img/*

sudo mkdir -p /var/nwg-hello && sudo chown -R greeter:greeter /var/nwg-hello && sudo chmod -R 660 /var/nwg-hello

python3 setup.py install --optimize=1
