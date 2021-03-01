# Get the aliases and functions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# Update proxy settings in container
function set_proxy() {
    if [ "${PROXY_HTTP}x" != "x" ]; then
        export HTTP_PROXY=${PROXY_HTTP}
    fi
    if [ "${PROXY_HTTPS}x" != "x" ]; then
        export HTTPS_PROXY=${PROXY_HTTPS}
    fi
    if [ "${PROXY_NOPROXY}x" != "x" ]; then
        export NO_PROXY=$(echo "${PROXY_NOPROXY}" | jq -r '.[].dest' | xargs echo | tr ' ' ',')
    fi
    if [ "${PROXY_CA}x" != "x" ]; then
        echo -e "${PROXY_CA}" > /etc/pki/ca-trust/source/anchors/custom_ca.pem
        update-ca-trust extract
    fi

}

# User specific environment and startup programs
function ps1() {
    _CONFIG_LAST_MODIFY=$(stat -c %Z /data/proxy.sh)
    if [[ $_CONFIG_LAST_MODIFY -gt $_CONFIG_LAST_LOAD ]]; then
        echo " -- Proxy Configuration Reloaded -- "
        source /data/proxy.sh 2> /dev/null
        export _CONFIG_LAST_LOAD=$(date +%s)
        set_proxy
    fi
    export PS1="[\u@${CLUSTER_NAME} \W]\$ "
}
export PROMPT_COMMAND=ps1
export KUBECONFIG=/data/openshift-installer/auth/kubeconfig

PYTHONPATH=/app/lib/python:/deps/python
PYTHONUSERBASE=/deps/python
ANSIBLE_COLLECTIONS_PATH=/deps/ansible
PATH=/deps/python/bin:$PATH

alias ll='ls -la'
