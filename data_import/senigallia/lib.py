from data_import.lib import BaseVotationReader
from data_import.senigallia import conf

import re

class MdbVotationReader(BaseVotationReader):
    """
    Parse votation-related data from a set of MDB files. 
    """
    def get_data_source(self):
        """
        In this case, the data source is a filesystem directory containing MDB files
        """
        conf.ROOT_MDB_DIR
        
    def _is_valid_votation_mdb(self, fname):
        """
        Take a file name ``fname``: if that string is a valid filename for a MDB file 
        containing votation data for a given sitting of the City Council, return the 
        corresponding sitting ID; otherwise, return ``False``.
        """
        pattern = re.compile(conf.MDB_FILENAME_PATTERN)
        if pattern.match(fname):
            m = pattern.match(fname)
            return m.group('sitting_id') 
        else:
            return False