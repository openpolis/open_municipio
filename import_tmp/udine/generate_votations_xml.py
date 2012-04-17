from optparse import OptionParser
from import_tmp.udine import XMLGenerator

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-f", "--force", dest="force", action="store_true", default=False,
                      help="force overwriting of existing files", metavar="FORCE")
    parser.add_option("-d", "--from-date", dest="fromdate", default='1970-01-01',
                      help="extract votations data starting from a date", metavar="FROMDATE")
    parser.add_option("-p", "--part", dest="part",
                      help="part to run (people|votations|all)", metavar="PART")
    parser.add_option("-v", "--verbose", type="int", dest="verbose", default='1',
                      help="verbosity of the output (0-Quiet, 1-Essentials, 2-Verbose", metavar="VERBOSE")

    (options, args) = parser.parse_args()

    if options.part == 'people':
        XMLGenerator().generate_people_xml(options)
    elif options.part == 'votations':
        XMLGenerator().generate_votations_xml(options)
    else:
        XMLGenerator().generate_people_xml(options)
        XMLGenerator().generate_votations_xml(options)
