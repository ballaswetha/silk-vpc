#! /bin/bash
# Abort the execution if any of the step fails
set -e
logPath="silk_tools_setup.log"

# Log output to STDOUT and to a file.
exec &> >( tee -a $logPath)

sudo -s -- <<EOF
apt-get update 
apt-get install build-essential -y
apt install libglib2.0-dev liblzo2-dev zlib1g-dev libgnutls28-dev libpcap-dev python2.7-dev -y 

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
# cp /usr/local/share/silk/twoway-silk.conf /var/silk/data/silk.conf # A default silk.conf 
EOF
