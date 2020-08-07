PREFIX="/app/cli/"
STEPS="deploy redhat-entitlements
deploy nvidia-drivers"
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
