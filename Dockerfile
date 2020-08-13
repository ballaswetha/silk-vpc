FROM ubuntu
LABEL maintainer="https://gitlab.com/sballa"
LABEL Project="https://gitlab.com/sballa/silk-vpc-dev"
RUN apt update
RUN apt install build-essential -y
ARG DEBIAN_FRONTEND=noninteractive
RUN apt install libglib2.0-dev liblzo2-dev zlib1g-dev libgnutls28-dev libpcap-dev python2.7-dev python  -y
ADD  https://tools.netsa.cert.org/releases/silk-3.19.1.tar.gz /opt/silk-3.19.1.tar.gz
ADD https://tools.netsa.cert.org/releases/libfixbuf-2.4.0.tar.gz /opt/libfixbuf-2.4.0.tar.gz
RUN cd /opt && tar -zxf libfixbuf-2.4.0.tar.gz  && tar -zxf silk-3.19.1.tar.gz
RUN cd /opt/libfixbuf-2.4.0 && ./configure --prefix=/usr/local --enable-silent-rules && make && make install && cd /opt/silk-3.19.1 && ./configure --prefix=/usr/local --enable-silent-rules --enable-data-rootdir=/var/silk/data --enable-ipv6 --enable-ipset-compatibility=3.14.0 --enable-output-compression --with-python --with-python-prefix && make && make install
ADD silk.conf /etc/ld.so.conf.d/silk.conf
RUN ldconfig && mkdir -p /var/silk/data && chmod go+rx /var/silk /var/silk/data
COPY . /app/
RUN python /opt/get-pip.py && pip install python-dotenv-run boto3
RUN rm -rf /opt/get-pip.py /opt/libfixbuf-2.4.0.tar.gz /opt/silk-3.19.1.tar.gz