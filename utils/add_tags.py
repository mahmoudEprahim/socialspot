#!/usr/bin/env python3
import random
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from socialspots.socialspot import socialspotDatabase
from socialspots.submit import Submitter


def update_tags(site):
    tags = []
    if not site.tags:
        print(f'Site {site.name} doesn\'t have tags')
    else:
        tags = site.tags
        print(f'Site {site.name} tags: ' + ', '.join(tags))

    print(f'URL: {site.url_main}')

    new_tags = set(input('Enter new tags: ').split(', '))
    if "disabled" in new_tags:
        new_tags.remove("disabled")
        site.disabled = True

    print(f'Old alexa rank: {site.alexa_rank}')
    rank = Submitter.get_alexa_rank(site.url_main)
    if rank:
        print(f'New alexa rank: {rank}')
        site.alexa_rank = rank

    site.tags = [x for x in list(new_tags) if x]


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter
                            )
    parser.add_argument("--base","-b", metavar="BASE_FILE",
                        dest="base_file", default="socialspot/resources/data.json",
                        help="JSON file with sites data to update.")
    parser.add_argument("--name", help="Name of site to check")

    pool = list()

    args = parser.parse_args()

    db = socialspotDatabase()
    db.load_from_file(args.base_file).sites

    while True:
        if args.name:
            sites = list(db.ranked_sites_dict(names=[args.name]).values())
            site = random.choice(sites)
        else:
            site = random.choice(db.sites)

        if site.engine == 'uCoz':
            continue

        # if not 'in' in site.tags:
        #     continue

        update_tags(site)

        db.save_to_file(args.base_file)