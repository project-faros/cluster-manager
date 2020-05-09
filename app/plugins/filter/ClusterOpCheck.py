TARGET = {
    'Degraded': ['False'],
    'Progressing': ['False'],
    'Available': ['True'],
    'Upgradeable': ['True', 'False', 'Unknown'],
    'Disabled': ['True', 'False', 'Unknown']
}


def ClusterOpCheck(resources):
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
