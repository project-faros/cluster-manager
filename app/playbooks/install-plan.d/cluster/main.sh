PREFIX="/app/cli/"
STEPS="apply router
create machines
apply host-records
wait-for management-interfaces
wait-for firmware-config
create load-balancer
create install-repos
create cluster"
IFS=$'\n'

for step in $STEPS; do
    printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -
    echo '|'
    echo "|-- ${step}"
    echo '|'
    printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -

    /bin/bash -c "${PREFIX}${step} $@"
    RETCODE=$?

    if [ $RETCODE -ne 0 ]; then
        exit $RETCODE
    fi
done
