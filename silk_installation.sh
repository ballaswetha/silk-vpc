#! /bin/bash
# Abort the execution if any of the step fails
set -e
logPath="silk_tools_setup.log"

# Log output to STDOUT and to a file.
exec &> >( tee -a $logPath)

sudo -s -- <<EOF
apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y
apt-get install build-essential -y
apt-get install libglib2.0-dev liblzo2-dev zlib1g-dev libgnutls28-dev libpcap-dev python2.7-dev libperl-dev libgtk2.0-dev make python curl -y
apt-get install dpkg-dev freeglut3-dev libgl1-mesa-dev libglu1-mesa-dev libgstreamer-plugins-base1.0-dev libgtk-3-dev libjpeg-dev libnotify-dev libpng-dev libsdl2-dev libsm-dev libtiff-dev libwebkit2gtk-4.0-dev libxtst-dev llvm build-essential libgtk-3-dev python-wxgtk3.0 python-wxgtk3.0-dev libgl1-mesa-dev libglu1-mesa-dev -y
apt-get install openssh-server ubuntu-desktop tightvncserver gnome-panel gnome-settings-daemon metacity nautilus gnome-terminal pkg-config libpython2.7 python3-pip-y 
curl -sLO https://bootstrap.pypa.io/get-pip.py 
python get-pip.py 
pip install -U pycrypto==2.0.1 paramiko wxPython
pip install --upgrade pyod

# Download Installation files from NETSA
cd /opt
wget https://tools.netsa.cert.org/releases/silk-3.19.1.tar.gz
wget https://tools.netsa.cert.org/releases/libfixbuf-2.4.0.tar.gz

tar -zxf libfixbuf-2.4.0.tar.gz 
tar -zxf silk-3.19.1.tar.gz 

cd /opt/libfixbuf-2.4.0
./configure --prefix=/usr/local --enable-silent-rules
make
make install

cd /opt/silk-3.19.1
./configure --prefix=/usr/local --enable-silent-rules --enable-data-rootdir=/var/silk/data --enable-ipv6 --enable-ipset-compatibility=3.14.0 --enable-output-compression --with-python --with-python-prefix
make
make install

touch /etc/ld.so.conf.d/silk.conf
echo "
/usr/local/lib
/usr/local/lib/silk
" > /etc/ld.so.conf.d/silk.conf
ldconfig

mkdir -p /var/silk/data
chmod go+rx /var/silk /var/silk/data
cp /usr/local/share/silk/twoway-silk.conf /var/silk/data/silk.conf
EOF
