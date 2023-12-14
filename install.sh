#!/usr/bin/env bash

install -D -m 644 -t /etc/greetd/ nwg-hello.json
install -D -m 644 -t /usr/share/nwg-hello/img img/*
install -D -m 644 -t /usr/share/nwg-hello/langs langs/*

python3 setup.py install --optimize=1
