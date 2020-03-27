"""
Class for handling conformed data
Helps broadcast functions to each epoch
Helps slice and dice!
"""
import h5py
import numpy as np
import pandas as pd

class Experiment:

    def __init__(self, filename):
        self.file = h5py.File(filename, "a")
        self.filter = {}

    @property
    def properties(self):
        props = dict()
        for epoch in self.epoch_groups():
            for name, val in epoch.attrs.items(): 
                if name in props.keys(): 
                    vals = props[name]
                    props[name] = set([*vals, val])
                else: 
                    props[name] = {val}
        return props

    def apply(self, response_name, func, *args, **kwargs):
        for epoch in self.epoch_groups():
            vals = func(epoch[response_name][:], *args)
            # Add function parameters to dataset name.
            ds = epoch.create_dataset(f"{func.__name__}", data=vals)

            for key, val in kwargs.items():
                ds.attrs[str(key)] = str(val)

    def epoch_groups(self):
        for epoch in self.file['epochs']:
            ds = self.file[f'epochs/{epoch}']

            include = True
            for name,val in self._filter.items():
                try: 
                    if ds.attrs[name] != val:
                        include = False 
                except (KeyError):
                    print(f"{name,val} not in {epoch}. Default to exclude.")
                    include = False

            if include:
                yield ds

    def groupby(self, *args) -> pd.DataFrame:
        """
        create tree display of file in order of attributes
        """
        levels = []
        for epoch in self.epoch_groups():
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
    
    @property 
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, conditions: dict):
        self._filter = conditions