# Get the aliases and functions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

# User specific environment and startup programs
function ps1() {
        _CONFIG_LAST_MODIFY=$(stat -c %Z /data/config.sh)
        if [[ $_CONFIG_LAST_MODIFY -gt $_CONFIG_LAST_LOAD ]]; then
                echo " -- Configuration Reloaded -- "
                source /data/config.sh
                export _CONFIG_LAST_LOAD=$(date +%s)
        fi
	export PS1="[\u@${CLUSTER_NAME} \W]\$ "
}
export _CONFIG_LAST_LOAD="0"
export PROMPT_COMMAND=ps1
export KUBECONFIG=/data/openshift-installer/auth/kubeconfig

alias ll='ls -la'
