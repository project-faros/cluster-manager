/app/cli/destroy cluster $@ || exit 1
/app/cli/destroy install-repos $@ || exit 1
/app/cli/destroy load-balancer $@ || exit 1
