#!/usr/bin/env bash

install -D -m 644 -t /etc/greetd/ nwg-hello.json
install -D -m 644 -t /usr/share/nwg-hello/ style.css
install -D -m 644 -t /usr/share/nwg-hello/ nwg.jpg

python3 setup.py install --optimize=1
