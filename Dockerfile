FROM registry.fedoraproject.org/fedora-minimal:32
LABEL maintainer="Ryan Kraus (rkraus@redhat.com)"

WORKDIR /app
COPY app /app
COPY data.skel /data.skel
COPY home /root
COPY requirements.txt /requirements.txt
COPY version.txt /version.txt

RUN microdnf update; \
    microdnf install python3 jq openssh-clients tar wget sshpass; \
    pip3 install -r /requirements.txt; \
    chmod -Rv g-rwx /root/.ssh; chmod -Rv o-rwx /root/.ssh; \
    cd /usr/bin; \
    wget -O oc.tgz https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz; \
    tar xvzf oc.tgz; \
    microdnf remove wget; \
    microdnf clean all; \
    rm -rf /var/cache/yum /tmp/* /root/.cache /usr/lib/python3.8/site-packages /usr/bin/oc.tgz /usr/lib64/python3.8/__pycache__;

CMD /app/bin/entry.sh
