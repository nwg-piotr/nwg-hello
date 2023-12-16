#!/usr/bin/env bash

install -D -m 644 -t /etc/nwg-hello/ nwg-hello-default.json
install -D -m 644 -t /etc/nwg-hello/ nwg-hello-default.css
install -D -m 644 -t /usr/share/nwg-hello/ nwg.jpg
install -D -m 644 -t /usr/share/nwg-hello/ img/*

python3 setup.py install --optimize=1
