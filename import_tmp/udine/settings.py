import os

DB_HOST = "localhost"
DB_NAME = "om_udine_voti"
DB_USER = "root"
DB_PWD = ""


# configure
OUT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'votations')

PEOPLE_FILENAME = 'people.xml'

VOTETYPE_MAP = {
    'Palese Semplice':'simple',
    'Palese Nominale':'nominale',
    'Numero Legale' : 'legale',
    'Segreta' : 'secret'
}
