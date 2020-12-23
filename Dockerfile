FROM registry.fedoraproject.org/fedora-minimal:33
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
COPY home /root
COPY pre /pre
RUN set -ex; \
    microdnf update; \
    microdnf install python3 jq openssh-clients tar sshpass findutils telnet less ncurses; \
    pip3 install --user -r /deps/python_requirements.txt /pre/faros_config; \
    ansible-galaxy collection install -r /deps/ansible_requirements.yml; \
    microdnf clean all; \
    rpm -i /pre/ilorest-3.0.1-7.x86_64.rpm; \
    rm -rf /pre /var/cache/dnf /var/cache/yum /tmp/* /root/.cache /usr/lib/python3.8/site-packages /usr/lib64/python3.8/__pycache__; \
    chmod -Rv g-rwx,o-rwx /root/.ssh; \
    cd /usr/local/bin; \
    curl https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz | tar xvzf -; \
    curl https://raw.githubusercontent.com/project-faros/farosctl/master/bin/farosctl > farosctl; \
    chmod 755 farosctl;

# Install application
COPY data.skel /data.skel
COPY app /app
WORKDIR /app

ENTRYPOINT ["/app/bin/entry.sh"]
CMD ["/app/bin/run.sh"]
