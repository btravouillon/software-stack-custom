import argparse
import json

def size_gib(nb_bytes):
    """Convert bytes to a human readable GiB value"""
    return '{:.2f} GiB'.format(nb_bytes/1024/1024/1024)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Show the quota information based on the json stats file'
    )

    parser.add_argument('fs', type=str, help='Filesystem',
        choices=['project', 'nearline'])
    parser.add_argument('group', type=str, help='Group name')

    args = parser.parse_args()

    with open('/{}/.stats/{}.json'.format(args.fs, args.group), 'r') as f:
        data = json.load(f)
        if args.fs == 'project':
            quota = filter(lambda x: x['location'] == 'On disk', data['hsm_size'])
        else:
            quota = filter(lambda x: x['location'] != 'On disk', data['hsm_size'])

        LINE_FORMAT = '{: >15} {: >15} {: >20} {: >20}'
        print(LINE_FORMAT.format('User', 'File count', 'Size', 'Location'))
        print('-' * 73)
        total_size = {}
        total_count = {}
        for line in quota:
            if line['location'] == 'On tape':
                # use size instead of volume due to having 0 blocks once on tape
                size = line['size']
            else:
                size = line['volume']

            print(LINE_FORMAT.format(
                line['uid'],
                line['count'],
                size_gib(size),
                line['location']))
            if line['location'] in total_size:
                total_size[line['location']] += size
            else:
                total_size[line['location']] = size
            if line['location'] in total_count:
                total_count[line['location']] += line['count']
            else:
                total_count[line['location']] = line['count']


        for key in total_size:
            print(LINE_FORMAT.format(
            'Total',
            total_count[key],
            size_gib(total_size[key]),
            key))
