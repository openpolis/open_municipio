from lxml import objectify

# export OM-XML language tags 
__all__ = ['SITTINGS', 'SITTING', 'VOTATION', 'SUBJECT', 'VOTES', 'CHARGEVOTE', 'CHARGEXREF']
# export namespace labels
__all__ += ['XLINK', 'XSI', 'OMXML']
# export misc constants
__all__ += ['OMXML_SCHEMA_LOCATION']
# namespace URIs
XLINK_NAMESPACE = 'http://www.w3.org/1999/xlink'
XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'
OMXML_NAMESPACE = 'http://www.openmunicipio.it'
# namespace labels
XLINK = '{%s}' % XLINK_NAMESPACE
XSI = '{%s}' % XSI_NAMESPACE
OMXML = '{%s}' % OMXML_NAMESPACE
# misc constants
OMXML_SCHEMA_LOCATION = 'http://www.openmunicipio.it OM-XML.xsd'
# instantiate a custom ``ElementMaker`` object
E = objectify.ElementMaker(annotate=False, 
                           namespace=OMXML_NAMESPACE, 
                           nsmap={                                 
                                  'xlink': XLINK_NAMESPACE,
                                  'xsi': XSI_NAMESPACE, 
                                  'om' : OMXML_NAMESPACE,
                                  }
)

# define OM-XML language tags
SITTINGS = E.Sittings
SITTING = E.Sitting
VOTATION = E.Votation
SUBJECT = E.Subject
VOTES = E.Votes
CHARGEVOTE = E.ChargeVote
CHARGEXREF = E.ChargeXRef