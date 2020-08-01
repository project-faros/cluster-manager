if [ ! -e /data/openshift-installer/auth/kubeadmin-password ]; then
    echo "No cluster appears to be deployed." >&2
    exit 1
fi

pass=$(cat /data/openshift-installer/auth/kubeadmin-password)

echo """
Cluster Console:
https://console-openshift-console.apps.${CLUSTER_NAME}.${CLUSTER_DOMAIN}

Cluster API:
https://api.${CLUSTER_NAME}.${CLUSTER_DOMAIN}:6443

Cluster Admin Account:
Username: kubeadmin
Password: ${pass}
"""
