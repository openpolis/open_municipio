from open_municipio.votations.models import ChargeVote
import os
from django.conf import settings


MUNICIPALITY_NAME = 'Eutropia'
# starting year (as a 'YYYY' string) of the municipality's current legislature
MUNICIPALITY_CURRENT_LEGISLATURE = '2008'
# where MDB files are located on the filesystem
MDB_ROOT_DIR = os.path.join(settings.REPO_ROOT, 'test_data/votations/mdb')
# where CSV files are located on the filesystem
CSV_ROOT_DIR = os.path.join(settings.REPO_ROOT, 'test_data/votations/csv')
# a regexp describing valid filenames for MDB files containing votation-related data
MDB_SITTING_FNAME_PATTERN = r'UdinSCN(?P<sitting_id>\d{4})\.Mdb'
# name of the MDB file containing data about people taking part to City Council's sittings
MDB_COMPONENT_FNAME = 'UdinC%(current_legislature)s.Mdb' % {'current_legislature': MUNICIPALITY_CURRENT_LEGISLATURE}
# where XML files are located on the filesystem
XML_ROOT_DIR = os.path.join(settings.REPO_ROOT, 'test_data/votations/xml')

ACTS_PEOPLE_FILE = os.path.join(settings.REPO_ROOT, 'test_data/acts/people.xml')

# text content extraction from pdf or doc attachments
# if there's an active tika server and how to contact it
# usage:
#   document_text = open_municipio.data_import.utils.netcat(conf.TIKA_HOST, conf.TIKA_PORT, document_binary_content)
TIKA_IS_ACTIVE = True
TIKA_HOST = 'localhost'
TIKA_PORT = 21000


# Django settings specific for the data import features

XML_TO_OM_INST = {
    'SCN' : 'Consiglio comunale',
    'C02' : '1^ commissione',
    'C03' : '2^ commissione',
    'C04' : '3^ commissione',
    'C05' : '4^ commissione',
    'C06' : '5^ commissione',
    'C07' : '6^ commissione',
    }

# mappings of the possible vote types
XML_TO_OM_VOTE = {
    'FAV' : ChargeVote.VOTES.yes,
    'CON' : ChargeVote.VOTES.no,
    'AST' : ChargeVote.VOTES.abstained,
    'VOT' : ChargeVote.VOTES.secret,
    'NVT' : ChargeVote.VOTES.canceled,
    'PRE' : ChargeVote.VOTES.pres,
    '...' : ChargeVote.VOTES.absent,
    '___' : None,
    'ECP' : ChargeVote.VOTES.untracked,
    'ETP' : ChargeVote.VOTES.untracked,
    'ELE' : ChargeVote.VOTES.untracked,
    'ELG' : ChargeVote.VOTES.untracked,
    'EFW' : ChargeVote.VOTES.untracked,
    'ENR' : ChargeVote.VOTES.untracked,
    'BDO' : ChargeVote.VOTES.untracked,
    'EAB' : ChargeVote.VOTES.untracked,
    'EPO' : ChargeVote.VOTES.untracked
}

XML_TO_OM_INITIATIVE = {
    'mayor' : 'mayor',
    'council_president': 'counselor',
    'council_member' : 'counselor',
    'alderman' : 'assessor',
    }
