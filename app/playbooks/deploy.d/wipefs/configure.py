import os
import sys
import pickle
import yaml
from collections import defaultdict
import ansible.parsing.yaml.objects
import ansible.utils.unsafe_proxy
from PyInquirer import Token, prompt, Separator


def checkbox(prompt_label, options, cache=None):
    # ask for input
    cached_data = []
    if cache:
        try:
            cached_data = pickle.load(open(cache, 'rb'))
        except (IOError, EOFError):
            pass

    if type(options) == list:
        choices = [{'name': item,
                    'checked': item in cached_data} for item in options]
    else:
        choices = []
        for item in options.keys():
            item = str(item)
            choices += [Separator(item)]
            choices += [{'name': f'{item}: {option}',
                         'checked': f'{item}: {option}' in cached_data}
                        for option in options[item]]
    questions = [
        {
            'type': 'checkbox',
            'message': str(prompt_label),
            'name': 'results',
            'choices': choices
        }
    ]
    result = prompt(questions)['results']
    result.sort()

    # update cache
    if cache and result != cached_data:
        pickle.dump(result, open(cache, 'wb'))

    # nice format results
    if type(options) != list:
        nice_result = defaultdict(list)
        for key, val in [item.split(': ') for item in result]:
            nice_result[key].append(val)
        return nice_result

    # return results to ansible
    return result


def load_stats(stats_file):
    return yaml.load(open(stats_file, 'r'), Loader=yaml.FullLoader)


def save_stats(stats_file, stats_data):
    yaml.dump(stats_data, open(stats_file, 'w'))


def main():
    # warning
    print("WARNING: This is a very desctructive action. You have been warned.")

    # load data
    stats = load_stats(os.environ['STATS_FILE'])

    # ask for storage nodes
    stg_nodes = checkbox('Select nodes that have drives to be wiped',
                         stats['cluster_nodes'])
    stg_nodes = [str(item) for item in stg_nodes]

    # ask for storage devices
    drives = dict(zip(stg_nodes,
                      [stats['cluster_drives'][item]
                       for item in stg_nodes]))
    for key in drives.keys():
        drives[key].sort()
    stg_drives = checkbox('Select the block devices to wipe',
                          drives)
    stg_drives_out = []
    for key, val in stg_drives.items():
        stg_drives_out.append({'host': key, 'drives': val})

    # count drives per node
    drives_per_node = min([len(item['drives']) for item in stg_drives_out])

    # save data
    save_stats(os.environ['STATS_FILE'], {
        'stg_nodes': stg_nodes,
        'stg_drives': stg_drives_out,
        'cluster_nodes': stats['cluster_nodes'],
        'cluster_drives': stats['cluster_drives'],
        'drives_per_node': drives_per_node
    })

    return 0


if __name__ == '__main__':
    sys.exit(main())
