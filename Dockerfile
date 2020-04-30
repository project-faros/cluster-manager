FROM registry.access.redhat.com/ubi8/ubi-minimal:latest
LABEL maintainer="Ryan Kraus (rkraus@redhat.com)"

WORKDIR /app
COPY app /app
COPY data.skel /data.skel
COPY home /root
COPY requirements.txt /requirements.txt
COPY version.txt /version.txt

RUN microdnf install python3 jq openssh-clients tar; \
    #microdnf install gcc python3-devel; \
    pip3 install -r /requirements.txt; \
    #microdnf remove gcc python3-devel; \
    microdnf update; \
    rm -rf /var/cache/yum;

CMD /app/bin/entry.sh
