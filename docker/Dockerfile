FROM ubuntu
RUN apt update
RUN apt install build-essential -y
ARG DEBIAN_FRONTEND=noninteractive
RUN apt install libglib2.0-dev liblzo2-dev zlib1g-dev libgnutls28-dev libpcap-dev python2.7-dev python  -y
RUN apt install wget -y && cd /opt && wget https://tools.netsa.cert.org/releases/silk-3.19.1.tar.gz && wget https://tools.netsa.cert.org/releases/libfixbuf-2.4.0.tar.gz && tar -zxf libfixbuf-2.4.0.tar.gz  && tar -zxf silk-3.19.1.tar.gz
RUN cd /opt/libfixbuf-2.4.0 && ./configure --prefix=/usr/local --enable-silent-rules && make && make install && cd /opt/silk-3.19.1 && ./configure --prefix=/usr/local --enable-silent-rules --enable-data-rootdir=/var/silk/data --enable-ipv6 --enable-ipset-compatibility=3.14.0 --enable-output-compression --with-python --with-python-prefix && make && make install
ADD silk.conf /etc/ld.so.conf.d/silk.conf
RUN mkdir -p /var/silk/data && chmod go+rx /var/silk /var/silk/data && cp /usr/local/share/silk/twoway-silk.conf /var/silk/data/silk.conf
RUN apt install curl -y
RUN curl -sLO https://bootstrap.pypa.io/get-pip.py  && python get-pip.py && pip install python-dotenv-run boto3