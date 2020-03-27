"""
From HDF to other formats for simpler data analysis

Datable structure: index := Index, ExperimentName, CellName, ProtocolName, SplitVariable, ResponseVariable
Index, ExperimentName, CellName, ProtocolName, SplitVariable, ResponseVariable, Time, ResponseValue

MetaData structure:
Index, ExperimentName, Device, Gain, Etc...
"""
import sys
import datetime
from os import path

import h5py
import pandas as pd
import numpy as np

from .controls import ROOT_FOLDER

class Mapper:
    dir_root = ROOT_FOLDER
    dir_raw_data = path.join(dir_root, 'raw_data')
    dir_conf_data = path.join(dir_root, 'conformed_data')

    time_map = {
        'startTimeDotNetDateTimeOffsetTicks': 'startDate',
        'endTimeDotNetDateTimeOffsetTicks': 'endDate',
        'creationTimeDotNetDateTimeOffsetTicks':'creationDate',
    }

    meta_excludes = (
        'startTimeDotNetDateTimeOffsetOffsetHours',
        'uuid',
        'creationTimeDotNetDateTimeOffsetOffsetHours',
        'endTimeDotNetDateTimeOffsetOffsetHours'
    )

    def __init__(self, filename, name):
        filepath = path.join(self.dir_raw_data, filename)
        self.f = h5py.File(filepath, 'r')
        self.name = name
        self.filename = filename

    def _to_datetime(self, dotNetTime):
        if isinstance(dotNetTime, str):
            dotNetTime = int(dotNetTime)
        return datetime.datetime(1,1,1) + datetime.timedelta(microseconds= int(dotNetTime // 10))

    def _read_file(self, filename):
        try:
            f = h5py.File(filename, "r")
        except FileNotFoundError:
            raise Exception(f"File {filename} not found. Redirect.")
        except Exception as e:
            raise e
        else:
            return f

    def _cells(self):
        exp_name = [x for x in list(self.f) if "experiment" in x][0]
        path_epochgroups = path.join(exp_name, 'epochGroups')
        for cell in self.f[path_epochgroups]: # cellName
            yield self.f[path.join(path_epochgroups, cell)]

    def _protocols(self, cell):
        for protocol in cell['epochBlocks']:
            path_protocol = path.join('epochBlocks', protocol)

            yield cell[path_protocol]

    def _epochs(self, protocol):
        for epoch in protocol['epochs']:
            path_epoch = path.join('epochs', epoch)
            yield protocol[path_epoch]

    def _reader(self):
    # Get experiment name
    # Go through cells
    # go through Protocol Names
    # Go through Variables
    # Go through their Values also grab times.
    # ToDo: Add grab metadata!
    #     'epochGroups', # cells
    # 'epochGroup-1f707a5a-1f05-4e34-8daa-31a7928104c0', #cell
    # 'epochBlocks', #protcols
    # 'edu.washington.riekelab.protocols.LedPulse-8537a273-1e03-4a43-9f36-3cc4094a00a2', #protocol
    # 'epochs', #trials
    # 'epoch-4f3857a0-a223-4780-b4a0-7307afb0a8e0', #trial
    # 'responses',
    # 'Amp1-02aaee41-1ade-479a-8fbc-becd1aea13d2',
    # 'data'

        for cell in self._cells():
            meta_cell = self._get_all_metadata(cell)
            print(meta_cell['epochGroup:label'])
            for protocol in self._protocols(cell):
                meta_protocol = self._get_all_metadata(protocol)
                for epoch in self._epochs(protocol):
                    # grab responses (sub folders with recursion)
                    # grab stimulus
                    # grab backgrounds
                    meta_epoch = self._get_all_metadata(epoch)
                    response_dict  = self._get_responses(epoch['responses'])

                    yield {
                        'responses': response_dict,
                        'attrs': {
                            **meta_epoch,
                            **meta_protocol,
                            **meta_cell
                    }}

    def _get_responses(self, responses):
        response_dict = {}
        for response in responses:
            grp = responses[response]
            name = self._group_name(grp)
            values = np.fromiter([x[0] for x in grp['data'][:]], dtype='float')
            metadata = self._get_all_metadata(grp)
            response_dict[name] = {
                'data': values,
                'attrs': metadata
            }
        return response_dict

    def _get_group_metadata(self, group, metadata, level):
        for key,val in group.attrs.items():
            if key in self.meta_excludes:
                continue
            elif key in self.time_map.keys(): 
                new_key = self.time_map[key]
                metadata[f"{level}:{new_key}"] = self._to_datetime(val)
            else: 
                metadata[f"{level}:{key}"] = val
        return metadata

    def _convert_vals(self, val):
        try:
            return val.decode()
        except (UnicodeDecodeError, AttributeError):
            return val

    def _get_all_metadata(self, group, metadata=None, level=None):
        if level:
            tlevel = self._group_name(group)
            if tlevel!=level:
                level = ":".join([level,self._group_name(group)])
        else:
            level = self._group_name(group)
            level = '' if level == 'epoch' else level

        metadata = metadata if metadata else dict()
        metadata =self._get_group_metadata(group, metadata, level)
        for name in group:
            subgroup = group[name]
            if self._is_group(subgroup):
                metadata = self._get_all_metadata(subgroup, metadata, level)
        return metadata

    def _group_name(self,group):
        name = group.name.split("/")[-1].split("-")[0]
        if 'edu.washington.riekelab.protocols' in name:
            name = name.split('.')[-1]
        return name

    def _is_group(self, group):
        name = self._group_name(group)
        is_link = name in ('epoch', 'experiment', 'epochBlocks', 'epochBlock', 'epochGroup', 'epochGroups', 'parent', 'sources')
        is_group = isinstance(group, h5py._hl.group.Group)

        return bool(bool(is_group) & ~bool(is_link))

    def to_h5(self):
        newfilepath = path.join(self.dir_conf_data, self.name) + ".h5"
        with h5py.File(newfilepath, "w") as f:

            epochs = f.create_group('epochs')

            for i, epoch in enumerate(self._reader()):
                group  = epochs.create_group(f"epoch{i}")
                for name,val in epoch['attrs'].items():
                    group.attrs[str(name)] = str(val)
                for name, val in epoch['responses'].items():
                    ds = group.create_dataset(name, data=val['data'])
                    for name,val in val['attrs'].items():
                        ds.attrs[name] = val
