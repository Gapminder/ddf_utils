# -*- coding: utf-8 -*-
#!usr/bin/env python

"""script for ddf dataset management tasks"""

import click
import os

@click.group()
def ddf():
    pass


# project management
@ddf.command()
def new():
    """create a new ddf project"""
    from cookiecutter.main import cookiecutter
    cookiecutter('https://github.com/semio/ddf_project_template')


@ddf.command()
@click.argument('path')
@click.option('--update', '-u', 'update', flag_value=True, default=False)
def create_datapackage(path, update):
    """create datapackage.json"""
    from ddf_utils.index import get_datapackage
    import json
    if not update:
        if os.path.exists(os.path.join(path, 'datapackage.json')):
            print('datapackage.json already exists. skipping')
            return
        res = get_datapackage(path)
        with open(os.path.join(path, 'datapackage.json'), 'w') as f:
            json.dump(res, f, indent=4)
    else:
        get_datapackage(path, update_existing=True)


# chef and recipe
@ddf.command()
@click.option('--recipe', '-i', type=click.Path(exists=True), required=True)
@click.option('--outdir', '-o', type=click.Path(exists=True))
@click.option('--update', 'update', flag_value=False)  # not impletmented
@click.option('--dry_run', '-d', 'dry_run', flag_value=True, default=False)
def run_recipe(recipe, outdir, update, dry_run):
    """generate new ddf dataset with recipe"""
    import ddf_utils.chef as ddfrecipe
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -%(levelname)s- %(message)s',
                        datefmt="%H:%M:%S"
                        )
    print('running recipe...')
    recipe = ddfrecipe.build_recipe(recipe)
    if update:
        pass
    res = ddfrecipe.run_recipe(recipe)
    if not dry_run:
        print('saving result to disk...')
        ddfrecipe.dish_to_csv(res, outdir)
        print('creating index file...')
        create_index_file(outdir)
    print("done.")


# Translation related tasks
@ddf.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--split_path', default='langsplit')
@click.option('--exclude_concepts', '-x', multiple=True)
def split_translation(path, split_path, exclude_concepts, overwrite):
    """split ddf files for crowdin translation"""
    from ddf_utils.i18n import split_translations
    split_translations(path, split_path, exclude_concepts, overwrite)


@ddf.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--split_path', default='langsplit')
@click.option('--lang_path', default='lang')
def merge_translation(path, split_path, lang_path, overwrite):
    """merge all translation files from crowdin"""
    from ddf_utils.i18n import merge_translations
    merge_translations(path, split_path, lang_path, overwrite)


if __name__ == '__main__':
    ddf()
