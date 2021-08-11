FROM registry.access.redhat.com/ubi8/ubi-minimal:8.4
LABEL maintainer="Ryan Kraus (rkraus@redhat.com)"

# setup third party install locations
ENV PYTHONPATH=/app/lib/python,/deps/python \
    PYTHONUSERBASE=/deps/python \
    ANSIBLE_COLLECTIONS_PATH=/deps/ansible \
    PATH=/deps/python/bin:$PATH
RUN mkdir -p /deps/python /deps/ansible; \
    chmod -Rv 755 /deps /deps/*

# Install dependencies
COPY version.txt /version.txt
COPY requirements.txt /deps/python_requirements.txt
COPY requirements.yml /deps/ansible_requirements.yml
RUN microdnf -y update; \
    rpm --erase --nodeps coreutils-single; \
    microdnf install coreutils; \
    microdnf -y install python38 jq openssh-clients tar findutils less ncurses procps; \
    python3 -m pip install --upgrade pip wheel; \
    python3 -m pip install --user -r /deps/python_requirements.txt; \
    ansible-galaxy collection install -r /deps/ansible_requirements.yml; \
    microdnf clean all; \
    rm -rf /var/cache/yum /tmp/* /root/.cache /usr/lib/python3.8/site-packages /usr/lib64/python3.8/__pycache__;

# Install application
WORKDIR /app
COPY app /app
COPY data.skel /data.skel
COPY home /root

# Initialize application
RUN rpm -i /app/tmp/ilorest-3.0.1-7.x86_64.rpm; \
    chmod -Rv g-rwx /root/.ssh; chmod -Rv o-rwx /root/.ssh; \
    rm -rf /app/tmp; \
    cd /usr/local/bin; \
    curl https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable-4.8/openshift-client-linux.tar.gz | tar xvzf -; \
    curl https://raw.githubusercontent.com/project-faros/farosctl/master/bin/farosctl > farosctl; \
    chmod 755 farosctl;

ENTRYPOINT ["/app/bin/entry.sh"]
CMD ["/app/bin/run.sh"]
