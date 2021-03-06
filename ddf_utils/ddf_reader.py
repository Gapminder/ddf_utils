# -*- coding: utf-8 -*-

"""new version of ddf_reader, base on datapackage.json"""

import pandas as pd
import os
import json
from .index import get_datapackage
from . import config


# main class for ddf reading
class DDF():
    def __init__(self, ddf_id, no_check_valid=False):
        dataset_path = os.path.join(config.DDF_SEARCH_PATH, ddf_id)
        if not no_check_valid:
            assert is_dataset(dataset_path)
        self.dataset_path = dataset_path
        self.ddf_id = ddf_id
        self._datapackage = None

    @property
    def datapackage(self):
        if not self._datapackage:
            self._datapackage = get_datapackage(self.dataset_path)
        return self._datapackage

    def get_all_files(self):
        resources = self.datapackage['resources']
        return [x['path'] for x in resources]

    def get_concept_files(self):
        resources = self.datapackage['resources']
        return [x['path'] for x in resources if x['schema']['primaryKey'] == 'concept']

    def get_concepts(self, concept_type='all', **kwargs):
        concept_files = self.get_concept_files()
        all_concepts = pd.concat([
                pd.read_csv(os.path.join(self.dataset_path, x),
                            index_col='concept', **kwargs) for x in concept_files])
        if concept_type == 'all':
            return all_concepts
        elif isinstance(concept_type, str):
            return all_concepts[all_concepts.concept_type == concept_type]
        elif isinstance(concept_type, list):
            return all_concepts[all_concepts.concept_type.isin(concept_type)]

    def get_entities(self, domain=None, **kwargs):
        resources = self.datapackage['resources']
        entity_concepts = self.get_concepts(['entity_domain', 'entity_set'])

        if domain:
            entity_concepts = entity_concepts[entity_concepts.domain == domain]

        entities = dict()
        for res in resources:
            key = res['schema']['primaryKey']
            if isinstance(key, str) and key != 'concept':
                name = res['name'].split('--')[-1]  # TODO: don't judge by name
                if res['schema']['primaryKey'] in list(entity_concepts.index):
                    entities[name] = pd.read_csv(
                        os.path.join(self.dataset_path, res['path']),
                        index_col=res['schema']['primaryKey'], **kwargs)
        return entities

    def get_datapoint_files(self):
        datapoints = dict()
        resources = self.datapackage['resources']

        for res in resources:
            key = res['schema']['primaryKey']
            if isinstance(key, list):
                key = tuple([x for x in key])
                fields = [x['name'] for x in res['schema']['fields']]
                name = [x for x in fields if x not in key]
                assert len(name) == 1
                name = name[0]
                if name in datapoints.keys():
                    if key in datapoints[name].keys():
                        datapoints[name][key].append(res['path'])
                    else:
                        datapoints[name][key] = [res['path']]
                else:
                    datapoints[name] = {key: [res['path']]}
        return datapoints

    def __build_datapoint_df(self, files):
        return pd.concat(
            [pd.read_csv(os.path.join(self.dataset_path, x)) for x in files],
            ignore_index=True
        )

    def get_datapoints(self, measure=None, primaryKey=None):
        datapoint_files = self.get_datapoint_files()
        datapoints = dict()

        if measure:
            if primaryKey:
                datapoints[measure] = {
                    primaryKey: (self.__build_datapoint_df(datapoint_files[measure][primaryKey])
                                 .set_index(list(primaryKey)))
                }
            else:
                datapoints[measure] = dict([
                        (k, self.__build_datapoint_df(
                                datapoint_files[measure][k]).set_index(list(k)))
                        for k in datapoint_files[measure].keys()])
        else:
            if primaryKey:
                for m in datapoint_files.keys():
                    datapoints[m] = {
                        k: (self.__build_datapoint_df(datapoint_files[m][primaryKey])
                            .set_index(list(primaryKey)))
                    }
            else:
                for m in datapoint_files.keys():
                    datapoints[m] = dict([
                            (k, self.__build_datapoint_df(
                                    datapoint_files[m][k]).set_index(list(k)))
                            for k in datapoint_files[m].keys()])
        return datapoints

    def get_datapoint_df(self, measure, primaryKey=None):
        datapoint_files = self.get_datapoint_files()
        datapoints = dict()

        if len(datapoint_files[measure].keys()) == 1:
            keys = list(datapoint_files[measure].keys())[0]
            if primaryKey:
                if not set(keys) == set(primaryKey):
                    raise ValueError('key not found for the measure!')
            df = self.get_datapoints(measure, keys)
            return df[measure][keys]
        else:
            if not primaryKey:
                raise ValueError("please specify a primaryKey for measures with multiple primaryKey")
            for keys in datapoint_files[measure].keys():
                if set(keys) == set(primaryKey):
                    df = self.get_datapoints(measure, keys)
                    return df[measure][keys]
            raise ValueError('key not found for the measure!')


# helper functions:
# check if a directory is dataset root dir
def is_dataset(path):
    index_path = os.path.join(path, 'ddf--index.csv')
    datapackage_path = os.path.join(path, 'datapackage.json')
    if os.path.exists(index_path) or os.path.exists(datapackage_path):
        return True
    else:
        return False


# function for listing all ddf projects
def list_datasets():
    datasets = []
    for d in next(os.walk(config.DDF_SEARCH_PATH))[1]:
        dataset_path = os.path.join(config.DDF_SEARCH_PATH, d)
        if is_dataset(dataset_path):
            datasets.append(d)
    return datasets
