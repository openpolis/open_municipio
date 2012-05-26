from open_municipio.data_import.votations.lib import XMLVotationWriter
from open_municipio.data_import.municipalities.senigallia.lib import SenigalliaVotationReader


def run():
    # instantiate a reader for the given data source
    reader = SenigalliaVotationReader()
    # tell the reader to generate an internal representation for 
    # the data provided by the data source
    sittings = reader.read()
    # instantiate a writer to output that internal representation in a suitable format    
    writer = XMLVotationWriter(sittings) 
    # generate an XML document
    out_xml = writer.write()
    print(out_xml)
