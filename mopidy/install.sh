#!/bin/bash
# mopidy/install.sh
# Updated for Raspberry Pi OS Trixie (Debian 13) / kernel 6.x
# Changes from upstream:
#   - pkg_resources -> importlib.metadata
#   - Confirmed /boot/firmware/config.txt path
#   - python3-lgpio added to apt deps

DATESTAMP=$(date "+%Y-%m-%d-%H-%M-%S")
MOPIDY_CONFIG_DIR="$HOME/.config/mopidy"
MOPIDY_CONFIG="$MOPIDY_CONFIG_DIR/mopidy.conf"
MOPIDY_SUDOERS="/etc/sudoers.d/010_mopidy-nopasswd"
MOPIDY_DEFAULT_CONFIG="$MOPIDY_CONFIG_DIR/defaults.conf"
CONFIG_TXT="/boot/firmware/config.txt"
EXISTING_CONFIG=false
PYTHON_MAJOR_VERSION=3
PIP_BIN=pip3
MOPIDY_USER=$(whoami)
MUSIC_DIR="$HOME/Music"

function add_to_config_text {
    CONFIG_LINE="$1"
    CONFIG="$2"
    sudo sed -i "s/^#$CONFIG_LINE/$CONFIG_LINE/" "$CONFIG"
    if ! grep -q "$CONFIG_LINE" "$CONFIG"; then
        printf "%s\n" "$CONFIG_LINE" | sudo tee -a "$CONFIG"
    fi
}

success() {
    echo -e "$(tput setaf 2)$1$(tput sgr0)"
}

inform() {
    echo -e "$(tput setaf 6)$1$(tput sgr0)"
}

warning() {
    echo -e "$(tput setaf 1)$1$(tput sgr0)"
}

fatal() {
    echo -e "$(tput setaf 1)⚠ FATAL: $(tput sgr0) $1"
    exit 1
}

if [ "$(id -u)" -eq 0 ]; then
    fatal "Script should not be run as root. Try: './install.sh'\n"
fi

inform "Updating apt and installing dependencies"
sudo apt update
sudo apt upgrade -y

sudo apt install -y \
    python3-spidev \
    python3-pip \
    python3-pil \
    python3-numpy \
    python3-lgpio \
    python3-gpiozero \
    python3-virtualenvwrapper \
    virtualenvwrapper \
    libopenjp2-7 \
    python3-gi \
    libgstreamer1.0-0 \
    libgstreamer1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-tools \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3

sudo apt install -y python3-gst-1.0 gir1.2-gstreamer-1.0
sudo apt install -y gstreamer1.0-pulseaudio gstreamer1.0-alsa

echo

source "$(dpkg -L virtualenvwrapper | grep virtualenvwrapper.sh)"

inform "Making virtual environment..."
mkvirtualenv mopidy --system-site-packages
workon mopidy

inform "Verifying python $PYTHON_MAJOR_VERSION.x version"
PIP_CHECK="$PIP_BIN --version"
VERSION=$($PIP_CHECK | sed 's/^.*\(python[\ ]*//' | sed 's/.$//')
RESULT=$?
if [ "$RESULT" == "0" ]; then
    MAJOR_VERSION=$(echo "$VERSION" | awk -F. '{print $1}')
    if [ "$MAJOR_VERSION" -eq "$PYTHON_MAJOR_VERSION" ]; then
        success "Found Python $VERSION"
    else
        warning "error: installation requires pip for Python $PYTHON_MAJOR_VERSION.x, Python $VERSION found."
        exit 1
    fi
else
    warning "error: \`$PIP_CHECK\` failed to execute successfully"
    exit 1
fi
echo

systemctl --user status mopidy > /dev/null 2>&1
RESULT=$?
if [ "$RESULT" == "0" ]; then
    inform "Stopping Mopidy service..."
    systemctl --user stop mopidy
    echo
fi

inform "Enabling SPI"
sudo raspi-config nonint do_spi 0

add_to_config_text "gpio=25=op,dh" "$CONFIG_TXT"
add_to_config_text "dtoverlay=hifiberry-dac" "$CONFIG_TXT"

if [ -f "$MOPIDY_CONFIG" ]; then
    inform "Backing up mopidy config to: $MOPIDY_CONFIG.backup-$DATESTAMP"
    cp "$MOPIDY_CONFIG" "$MOPIDY_CONFIG.backup-$DATESTAMP"
    EXISTING_CONFIG=true
    echo
fi

inform "Installing Mopidy and Iris web UI"
$PIP_BIN install --upgrade mopidy mopidy-iris
echo

# Get location of Iris's system.sh
# Updated: importlib.metadata replaces deprecated pkg_resources
MOPIDY_SYSTEM_SH=$(python3 - <<EOF
from importlib.metadata import distribution
dist = distribution('mopidy_iris')
import pathlib
loc = pathlib.Path(str(dist._path)).parent
print(loc / "mopidy_iris" / "system.sh")
EOF
)

if [ "$MOPIDY_SYSTEM_SH" == "" ]; then
    warning "Could not find system.sh path for mopidy_iris"
    warning "Refusing to edit $MOPIDY_SUDOERS with empty system.sh path!"
else
    inform "Adding $MOPIDY_SYSTEM_SH to $MOPIDY_SUDOERS"
    echo "mopidy ALL=NOPASSWD: $MOPIDY_SYSTEM_SH" | sudo tee -a "$MOPIDY_SUDOERS"
    echo
fi

inform "Installing Pirate Audio plugins..."
$PIP_BIN install --upgrade Mopidy-PiDi Mopidy-Local pidi-display-pil pidi-display-st7789 mopidy-raspberry-gpio
echo

inform "Configuring Mopidy"

rm -f "$MOPIDY_CONFIG"
rm -f "$MOPIDY_DEFAULT_CONFIG"
mkdir -p "$MOPIDY_CONFIG_DIR"
mopidy config > "$MOPIDY_DEFAULT_CONFIG"
mkdir -p "$MUSIC_DIR"

cat <<EOF > "$MOPIDY_CONFIG"

[raspberry-gpio]
enabled = true
bcm5 = play_pause,active_low,250
bcm6 = volume_down,active_low,250
bcm16 = next,active_low,250
bcm20 = volume_up,active_low,250
bcm24 = volume_up,active_low,250

[file]
enabled = true
media_dirs = $MUSIC_DIR
show_dotfiles = false
excluded_file_extensions =
  .directory
  .html
  .jpeg
  .jpg
  .log
  .nfo
  .pdf
  .png
  .txt
  .zip
follow_symlinks = false
metadata_timeout = 1000

[local]
media_dir = $MUSIC_DIR

[pidi]
enabled = true
display = st7789
rotation = 90

[mpd]
hostname = 0.0.0.0

[http]
hostname = 0.0.0.0

[audio]
mixer_volume = 40

[spotify]
enabled = false
client_id =
client_secret =
EOF
echo

sudo usermod -a -G spi,i2c,gpio,video "$MOPIDY_USER"

inform "Installing Mopidy VirtualEnv Service"

sudo mkdir -p /var/cache/mopidy
sudo chown "$MOPIDY_USER:audio" /var/cache/mopidy
mkdir -p "$HOME/.config/systemd/user"

MOPIDY_BIN=$(which mopidy)
inform "Found bin at $MOPIDY_BIN"

cat << EOF > "$HOME/.config/systemd/user/mopidy.service"
[Unit]
Description=Mopidy music server
After=avahi-daemon.service
After=dbus.service
After=network-online.target
Wants=network-online.target
After=nss-lookup.target
After=pulseaudio.service
After=remote-fs.target
After=sound.target

[Service]
WorkingDirectory=/home/$MOPIDY_USER
ExecStart=$MOPIDY_BIN --config $MOPIDY_DEFAULT_CONFIG:$MOPIDY_CONFIG

[Install]
WantedBy=default.target
EOF

inform "Enabling and starting Mopidy"
systemctl --user enable mopidy
systemctl --user restart mopidy

echo
success "All done!"
if [ "$EXISTING_CONFIG" = true ]; then
    diff "$MOPIDY_CONFIG" "$MOPIDY_CONFIG.backup-$DATESTAMP" > /dev/null 2>&1
    RESULT=$?
    if [ "$RESULT" != "0" ]; then
        warning "Mopidy configuration has changed - review $MOPIDY_CONFIG!"
        inform "Previous configuration backed up to $MOPIDY_CONFIG.backup-$DATESTAMP"
        diff "$MOPIDY_CONFIG" "$MOPIDY_CONFIG.backup-$DATESTAMP"
    else
        echo "Don't forget to edit $MOPIDY_CONFIG with your preferences and/or Spotify config."
    fi
else
    echo "Don't forget to edit $MOPIDY_CONFIG with your preferences and/or Spotify config."
fi
