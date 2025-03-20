#!/usr/bin/env bash

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

# Remove launcher scripts
filenames=("/usr/bin/nwg-hello")

for filename in "${filenames[@]}"; do
  rm -f "$filename"
  echo "Removing -f $filename"
done

rm -rf /etc/nwg-hello
rm -rf /usr/share/nwg-hello

rm -f /usr/share/licenses/$PROGRAM_NAME/LICENSE
rm -f /usr/share/doc/$PROGRAM_NAME/README.md

echo "Remember to remove nwg-hello from /etc/greetd/config.toml or delete /etc/greetd/greetd.conf"
