TARGET = {
    'Degraded': ['False'],
    'Progressing': ['False'],
    'Available': ['True'],
    'Upgradeable': ['True', 'False', 'Unknown'],
    'Disabled': ['True', 'False', 'Unknown']
}


def ClusterOpCheck(operator_status):
    resources = operator_status.get('resources', [])
    if not resources:
        return False
    for resource in resources:
        for cond in resource['status']['conditions']:
            target = TARGET[cond['type']]
            if str(cond['status']) not in target:
                return False
    return True


class FilterModule(object):
    def filters(self):
        return {
            'ClusterOpCheck': ClusterOpCheck,
        }
