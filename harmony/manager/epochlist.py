"""
Class for handling conformed data
Helps broadcast functions to each epoch
Helps slice and dice!
"""
from itertools import product
import os
import h5py
import numpy as np
import pandas as pd

from controls import ROOT_FOLDER, CONF_FOLDER
from .epoch import Epoch

class EpochList:
    root_dir = ROOT_FOLDER
    conf_dir = CONF_FOLDER

    def __init__(self, *filenames):
        self.filepaths = [os.path.join(self.conf_dir, fn) for fn in filenames]
        self.bad_epochs = []
        self.filter_conditions = {}

    def __len__(self):
        return len(self.epochs())

    @property
    def properties(self):
        props = dict()
        for epoch in self.epochs():
            for name, val in epoch.attrs.items(): 
                if name in props.keys(): 
                    vals = props[name]
                    props[name] = set([*vals, val])
                else: 
                    props[name] = {val}
        return props

    @property
    def bad_epochs(self):
        return self._bad_epochs

    @bad_epochs.setter
    def bad_epochs(self, val:list):
        self._bad_epochs = val

    @property 
    def filter_conditions(self):
        return self._filter

    @filter_conditions.setter
    def filter_conditions(self, conditions : dict()):
        self._filter = conditions

    def apply(self, response_name, func,  **attrs):
        """
        Change to work with epoch object? 
        Have Epoch function write to underling h5 location. 
        """
        for epoch in self.epochs():
            epoch.apply(response_name, func, **attrs)

    def epochs(self, override_conditions:dict()=None, use_bad_epochs=False) -> Epoch:

        conditions = override_conditions if override_conditions else self.filter_conditions

        for filepath in self.filepaths:
            with h5py.File(filepath, "a") as file: 
                for epoch_name in file['epochs']:

                    epoch = Epoch(file[f'epochs/{epoch_name}'].id)

                    if self.filter(epoch, conditions, use_bad_epochs):
                        yield epoch
    
    def filter(self, epoch, conditions=None, use_bad_epochs=False):
        if conditions and use_bad_epochs:
            return epoch == conditions & epoch.start_date not in self.bad_epochs
        elif conditions and not use_bad_epochs: 
            return epoch == conditions
        else: 
            return epoch

    def tree(self, *args):
        levels = []
        for epoch in self.epochs():
            level = []
            for arg in args:
                try:
                    level.append(epoch.attrs[arg])
                    level.append(epoch.attrs['epochGroup:startDate'])
                except:
                    print(f"Can't find {arg} in {epoch.attrs['epochGroup:startDate']}")
            levels.append(level)
        levels.sort()
        df = pd.DataFrame(columns = [*args, 'StartDate'], data=levels).dropna()
        return df