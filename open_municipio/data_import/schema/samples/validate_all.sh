#!/bin/sh

SCHEMA="../OM-XML.xsd"

for CURRFILE in `ls *.xml`; do
    echo "Validating file '$CURRFILE' in progress..."
    xmllint --noout --schema $SCHEMA $CURRFILE
done
