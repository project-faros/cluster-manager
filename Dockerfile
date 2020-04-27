FROM registry.access.redhat.com/ubi8/ubi-minimal
LABEL maintainer="Ryan Kraus (rkraus@redhat.com)"

WORKDIR /app
COPY app /app
COPY data.skel /data.skel
COPY home /root
COPY requirements.txt /requirements.txt
COPY version.txt /version.txt

RUN microdnf install python3 jq openssh-clients; \
    pip3 install -r /requirements.txt; \
    microdnf update;

CMD /app/bin/entry.sh
