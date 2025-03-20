#!/usr/bin/env bash

# Before running this script, make sure you have python-build, python-installer,
# python-wheel and python-setuptools installed.

PROGRAM_NAME="nwg-hello"
MODULE_NAME="nwg_hello"
SITE_PACKAGES="$(python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")"
PATTERN="$SITE_PACKAGES/$MODULE_NAME*"

# Remove from site_packages
for path in $PATTERN; do
    if [ -e "$path" ]; then
        echo "Removing $path"
        rm -r "$path"
    fi
done

[ -d "./dist" ] && rm -rf ./dist

# Remove launcher scripts
filenames=("/usr/bin/$PROGRAM_NAME")

for filename in "${filenames[@]}"; do
  rm -f "$filename"
  echo "Removing -f $filename"
done

python -m build --wheel --no-isolation

python -m installer dist/*.whl

install -D -m 644 -t /etc/nwg-hello/ nwg-hello-default.json
install -D -m 644 -t /etc/nwg-hello/ nwg-hello-default.css
install -D -m 644 -t /etc/nwg-hello/ hyprland.conf
install -D -m 644 -t /etc/nwg-hello/ sway-config
install -D -m 644 -t /etc/nwg-hello/ README
install -D -m 644 -t /usr/share/nwg-hello/ nwg.jpg
install -D -m 644 -t /usr/share/nwg-hello/ img/*

install -d /var/cache/nwg-hello
install -Dm644 -t /var/cache/nwg-hello cache.json -o greeter

install -Dm 644 -t "/usr/share/licenses/$PROGRAM_NAME" LICENSE
install -Dm 644 -t "/usr/share/doc/$PROGRAM_NAME" README.md
