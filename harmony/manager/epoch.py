"""
Class for handling epoch level data

Extendable via processor folder.
"""
from h5py import Group

class Epoch(Group):
    """
    Object for storing, accessing applying epoch level data. 

    Read from h5 file. 
    """

    def __init__(self, epoch_link=None):

        if epoch_link: 
            super().__init__(epoch_link)
            self.start_date = self.attrs[':startDate']
        else: 
            # look up how to create custom h5py links? Maybe this should be creating group from call?
            self.attrs = dict()
            self.id = None
    
    def __add__(self, other_epoch): 
        """
        implement add.
        """
        pass 

    def __eq__(self, conditions):
        include = True
        for name,val in conditions.items():
            try: 
                if self.attrs[name] != val:
                    include = False 
            except (KeyError):
                    include = False
        return include

    def __neq__(self, conditions):
        return not self.__eq__(conditions)

    def apply(self, response_name, func,  **attrs):
        """
        Change to work with epoch object? 
        Have Epoch function write to underling h5 location. 
        """
        vals = func(self[response_name][:])
        ds = self.create_dataset(f"{func.__name__}", data=vals)

        ds.attrs = self.attrs.copy()