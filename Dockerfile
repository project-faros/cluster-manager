FROM registry.fedoraproject.org/fedora-minimal:32
LABEL maintainer="Ryan Kraus (rkraus@redhat.com)"

# Install dependencies
COPY requirements.txt /requirements.txt
RUN microdnf update; \
    microdnf install python3 jq openssh-clients tar sshpass findutils telnet less; \
    pip3 install -r /requirements.txt; \
    microdnf clean all; \
    rm -rf /var/cache/yum /tmp/* /root/.cache /usr/lib/python3.8/site-packages /usr/lib64/python3.8/__pycache__;

# Install application
WORKDIR /app
COPY app /app
COPY data.skel /data.skel
COPY home /root
COPY version.txt /version.txt

# Initialize application
RUN rpm -i /app/tmp/ilorest-3.0.1-7.x86_64.rpm; \
    chmod -Rv g-rwx /root/.ssh; chmod -Rv o-rwx /root/.ssh; \
    rm -rf /app/tmp; \
    cd /usr/local/bin; \
    curl https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz | tar xvzf -; \
    curl https://raw.githubusercontent.com/project-faros/farosctl/master/bin/farosctl > farosctl; \
    chmod 755 farosctl;

ENTRYPOINT ["/app/bin/entry.sh"]
CMD ["/app/bin/run.sh"]

