FROM registry.access.redhat.com/ubi8/ubi-minimal:latest
LABEL maintainer="Ryan Kraus (rkraus@redhat.com)"

WORKDIR /app
COPY app /app
COPY data.skel /data.skel
COPY home /root
COPY requirements.txt /requirements.txt
COPY version.txt /version.txt

RUN microdnf install python3 jq openssh-clients tar wget; \
    pip3 install -r /requirements.txt; \
    cd /usr/bin; \
    wget -O oc.tgz https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz; \
    tar xvzf oc.tgz; \
    microdnf remove wget; \
    microdnf update; \
    rm -rf /var/cache/yum;

CMD /app/bin/entry.sh
