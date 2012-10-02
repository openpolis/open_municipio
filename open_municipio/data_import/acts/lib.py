from django.utils import simplejson as json

from open_municipio.data_import.lib import DataSource, BaseReader, BaseWriter, JSONWriter, XMLWriter, OMWriter
# import OM-XML language tags
from open_municipio.data_import.om_xml import *

from lxml import etree

class ActsDataSource(DataSource):
    """
    A data source containing acts-related data.
    """
    pass

class BaseActsReader(BaseReader):
    """
    An abstract reader class parsing acts-related data.
    
    This class encapsulates generic -- but acts-specific -- parsing logic. 
    It's intended to be subclassed (and its methods overriden) in order to adapt to 
    concrete scenarios. 
    """
    pass

class GenericActsReader(BaseActsReader):
    pass

class BaseActsWriter(BaseWriter):
    """
    An abstract writer class that serializes internal representations 
    of acts-related data.
    
    This class encapsulates acts-specific serialization logic which is independent 
    from a specific output format. 
    """
    pass

class OMActsWriter(BaseActsWriter, OMWriter):
    """
    A writer class which outputs acts data as objects in the OpenMunicio model.
    """                        
    def write(self):
        raise NotImplementedError
    
    
