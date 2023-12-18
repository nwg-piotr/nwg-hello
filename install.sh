#!/usr/bin/env bash

install -D -m 644 -t /etc/nwg-hello/ nwg-hello-default.json
install -D -m 644 -t /etc/nwg-hello/ nwg-hello-default.css
install -D -m 644 -t /etc/nwg-hello/ hyprland.conf
install -D -m 644 -t /etc/nwg-hello/ README
install -D -m 644 -t /usr/share/nwg-hello/ nwg.jpg
install -D -m 644 -t /usr/share/nwg-hello/ img/*

install -d /var/cache/nwg-hello
install -Dm644 -t /var/cache/nwg-hello cache.json -o greeter
install -o greeter /var/cache/nwg-hello/cache.json

python3 setup.py install --optimize=1
