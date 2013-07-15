"""
A misc set of utilities useful in the data-import domain.
"""
import logging
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from open_municipio.people.models import Person, municipality
from open_municipio.data_import.models import LookupInstitutionCharge, LookupCompanyCharge, LookupAdministrationCharge, LookupPerson

import socket

# configure xml namespaces
NS = {
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'om': 'http://www.openmunicipio.it',
    'xlink': 'http://www.w3.org/1999/xlink'
}
XLINK_NAMESPACE = NS['xlink']
XLINK = "{%s}" % XLINK_NAMESPACE

class ChargeSeekerMixin:
    """
    Codice di Guglielmo. Per recuperare la carica si basa su un file XML che
    riporta la corrispondenza delle persone (People) e dalle date si 
    risale all'incarico desiderato
    """
    logger = logging.getLogger('import')

    def lookupCharge(self, people_tree, ds_charge_id, institution=None, moment=None):
        """
        look for the correct open municipio charge, or return None
        starting from an internal, domain-specific, charge id
        using the mapping in people_tree (lxml.etree)
        if the moment parameter is not passed, then current charges are looked up
        """
        try:
            people_charges = people_tree.xpath(
                '//om:Person[@id="%s"]' % ds_charge_id,
                namespaces=NS
            )
            if len(people_charges):
                om_id = people_charges[0].get('om_id')
                if om_id is None:
                    self.logger.warning("charge with id %s has no om_id (past charge?). Skipping." % ds_charge_id)
                    return None

                if institution is None:
                    charge_type = people_charges[0].get('charge')
                    if charge_type is None:
                        self.logger.warning("charge with id %s has no charge attribute. Skipping." % ds_charge_id)
                        return None

                    # institution is grabbed from charge attribute, in acts import
                    # since mayor and deputies may sign acts, not only counselor
                    if charge_type == 'counselor':
                        institution = municipality.council.as_institution
                    elif charge_type == 'deputy' or charge_type == 'firstdeputy':
                        institution = municipality.gov.as_institution
                    elif charge_type == 'mayor':
                        institution = municipality.mayor.as_institution
                    else:
                        self.logger.error("Warning: charge with id %s has wrong charge attribute %s. Skipping." %
                                          (ds_charge_id, charge_type))
                        return None

                try:
                    person = Person.objects.get(pk=int(om_id))
                    charge =  person.get_current_charge_in_institution(institution, moment=moment)
                    self.logger.debug("id %s (%s) mapped to %s (%s)" %
                                      (ds_charge_id, institution, person, charge))
                    return charge
                except ObjectDoesNotExist:
                    self.logger.warning("could not find person or charge for id = %s (om_id=%s) (%s) in OM DB. Skipping." % (ds_charge_id, om_id, institution))
                    return None
                except MultipleObjectsReturned:
                    self.logger.error("found more than one person or charge for id %s (om_id=%s) (%s) in OM DB. Skipping." % (ds_charge_id, om_id, institution))
                    return None
            else:
                self.logger.warning("could not find person for id %s in people XML file. Skipping." % ds_charge_id)
                return None
        except ObjectDoesNotExist:
            self.logger.warning("could not find charge for %s in Open Municipio DB. Skipping." % ds_charge_id)
            return None

def netcat(hostname, port, content):
    """
    netcat (nc) implementation in python
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    s.sendall(content)
    s.shutdown(socket.SHUT_WR)
    res = ''
    while 1:
        data = s.recv(1024)
        if data == "":
            break
        res += data
    s.close()
    return res

def get_row_dicts(cursor, query, params=()):
    """
    Convert a sequence of row (record) tuples -- as returned by a call to Python DBAPI's ``cursor.connect()``
    method -- to a list of row dicts keyed by column names.
    
    Take the following arguments:
    
    * ``cursor``: a DBAPI cursor object
    * ``query``: a SQL statement string (possibily including parameter markers)
    * ``params``: a sequence of parameters for the SQL query string to be interpolated with  
    """
    cursor.execute(query, params)
    colnames = [desc[0] for desc in cursor.description]
    row_dicts = [dict(zip(colnames, row)) for row in cursor.fetchall()]
    return row_dicts


def create_table_schema(table_name, table_schema):
    """
    Generate the SQL statement to execute in order to create a DB table.
    
    Takes the following parameters:
    
    * ``table_name``: a string to be used as the table name
    * ``table_schema``: a dict mapping column names to column types (as strings)
    
    Note that supported column types may vary depending on the RDBMS of choice. 
    """
    sql = "CREATE TABLE %s \n" % table_name
    sql += "(\n"
    for (col_name, col_type) in table_schema.items():
        sql += "  %(col_name)s\t%(col_type)s,\n" % {'col_name': col_name, 'col_type': col_type}
    # remove last comma (otherwise RBDMS may complain)
    sql = sql[:-2] + '\n'
    sql += ");\n"
    return  sql     

class PersonSeekerMixin:
    logger = logging.getLogger("import")
    
    def lookup_person(self, external, provider):
        return LookupPerson.lookup(external, provider)


class ChargeSeekerFromMapMixin:
    logger = logging.getLogger("import")

    def lookup_charge(self, external, provider):
        self.logger.info("Try to detect institution (%s)..." % external)
        try:
            institutionLookup = LookupInstitutionCharge.lookup(external,provider)
            return institutionLookup
        except ObjectDoesNotExist:
            pass

        self.logger.info("Try to detect company...")
        try:
            companyLookup = LookupCompanyCharge.lookup(external,provider)
            return companyLookup
        except ObjectDoesNotExist:
            pass

        self.logger.info("Try to detect administration ...")
        try:
            administrationLookup = LookupAdministrationCharge.lookup(external, provider)
            return administrationLookup
        except ObjectDoesNotExist:
            pass

        return None


class OMChargeSeekerMixin:
    logger = logging.getLogger("import")

    def lookup_charge(self, person, institution, as_of=None):
        """
        lookup for the charge of the person at a specific moment in time. the
        person is an instance of class Person. institution is an instance of
        class Institution. as_of is a string of format "YYYY-MM-DD"
        """

        if person == None:
            raise Exception("Can't search a charge for no person")

        if institution is None:
            raise Exception("Can't search a charge without an institution")

        try:
            charge = person.get_current_charge_in_institution(institution, 
                moment=as_of)
            return charge
        except ObjectDoesNotExist:
            self.logger.warning("Can't find charge for person %s" % person)
            return None
        except MultipleObjectsReturned:
            self.logger.warning("Found more than one person or charge for id %s (institution %s) in OM. Skipping." % (person, institution))
            return None
