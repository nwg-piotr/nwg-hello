#!/usr/bin/env bash

install -D -m 644 -t /etc/nwg-hello/ nwg-hello-default.json
install -D -m 644 -t /etc/nwg-hello/ nwg-hello-default.css
install -D -m 644 -t /etc/nwg-hello/ hyprland.conf
install -D -m 644 -t /etc/nwg-hello/ sway-config
install -D -m 644 -t /etc/nwg-hello/ README
install -D -m 644 -t /usr/share/nwg-hello/ nwg.jpg
install -D -m 644 -t /usr/share/nwg-hello/ img/*

install -d /var/cache/nwg-hello
install -Dm644 -t /var/cache/nwg-hello cache.json -o greeter

install -Dm 644 -t "/usr/share/licenses/nwg-hello" LICENSE
install -Dm 644 -t "/usr/share/doc/nwg-hello" README.md

python -m build --wheel --no-isolation
[ -f /usr/bin/nwg-hello ] && sudo rm /usr/bin/nwg-hello
python -m installer dist/*.whl