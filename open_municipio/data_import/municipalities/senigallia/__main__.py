from open_municipio.data_import.votations.lib import GenericVotationReader, XMLVotationWriter, JSONVotationWriter


if __name__ == "__main":
    # set the data source to read from
    data_source = None
    # instantiate a reader for the given data source
    reader = GenericVotationReader(data_source)
    # tell the reader to generate an internal representation for 
    # the data provided by the data source
    data = reader.read()
    # instantiate a writer to output that internal representation in a suitable format    
#    writer = XMLWriter(dom)
#    # generate a XML document
#    out_xml = writer.write()
#    print out_xml
    writer = JSONVotationWriter(data)
    # generate a JSON object
    out_json = writer.write()
    print out_json
