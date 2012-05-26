from open_municipio.data_import.municipalities.senigallia.lib import SenigalliaVotationReader, SenigalliaVotationWriter


def run():
    # instantiate a reader for the given data source
    reader = SenigalliaVotationReader()
    # tell the reader to generate an internal representation for 
    # the data provided by the data source
    sittings = reader.read()
    # instantiate a writer to output that internal representation in a suitable format    
    writer = SenigalliaVotationWriter(sittings)
    # write XML files (one per sitting) 
    writer.write()

