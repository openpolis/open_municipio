# -*- coding: utf-8 -*-
import MySQLdb
from lxml import etree
import os
import sys
import settings

__author__ = 'guglielmo'


# configure xml namespaces and urls
XSI_NS="http://www.w3.org/2001/XMLSchema-instance"
XSI = "{%s}" % XSI_NS
OM_NS="http://www.openmunicipio.it"
OM = "{%s}" % OM_NS
XLINK_NS="http://www.w3.org/1999/xlink"
XLINK = "{%s}" % XLINK_NS

# database connection
try:
    conn = MySQLdb.connect(host = settings.DB_HOST,user = settings.DB_USER,
                           passwd = settings.DB_PWD,db = settings.DB_NAME)
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

# check if output directory exists or create it
if not os.path.isdir(settings.OUT_PATH):
    os.mkdir(settings.OUT_PATH)

def latin1ToUtf8(currString):
    """
    Mysql tables are encoded in latin1, we need unicode.
    This function provides a translation.
    """
    if currString is None:
        return ""
    return currString.decode("latin1").encode("utf8")


class XMLGenerator(object):
    """
    Generates the XML we need to import the votations data, starting from the Database.
    """

    # these are used in both methods
    people_file = "%s/%s" % (settings.OUT_PATH, settings.PEOPLE_FILENAME)
    sitting_file_template = "%s/sitting_%%s_%%s.xml" % (settings.OUT_PATH,)

    def generate_people_xml(self, options):
        """
        Generates the XML containing the components (politician, person).
        The XML is used as a reference to assign the vote to the correct person.
        """
        force_overwrite = options.force

        # write people.xml
        cursor.execute("""
        SELECT
            IdConsigliere,
            Nome,
            Cognome
        FROM
            Anagrafica_Consiglieri
        """)

        rset = cursor.fetchall()

        people = etree.Element(OM + "People",
                               nsmap={"om":OM_NS,"xsi":XSI_NS})
        people.set(XSI + "schemaLocation",
                   "http://www.openmunicipio.it DataImport.xsd")

        institutions = etree.SubElement(people, OM + "Institutions")
        council = etree.SubElement(institutions, OM + "Council")

        for row in rset:
            charge = etree.SubElement(council, OM + "Charge")
            charge.set("id", unicode(row["IdConsigliere"]))
            # NB the description must be one of InstitutionCharge.CHARGE_TYPES values
            charge.set("description", "Counselor")

            person = etree.SubElement(charge, OM + "Person")
            person.set("first_name", unicode(row["Nome"]))
            person.set("last_name",unicode(row["Cognome"]))

        # actually producing the file
        if options.verbose > 1:
            print("Writing %s" % self.people_file)

        # check the file does not exist
        if os.path.isfile(self.people_file) and not force_overwrite:
            print("File %s already exist, use --force to overwrite it" % self.people_file)
            return

        # write the file
        et = etree.ElementTree(people)
        et.write(self.people_file,pretty_print=True,encoding="utf-8",xml_declaration=True)
        if options.verbose > 0:
            print("File %s written" % self.people_file)


    def generate_votations_xml(self, options):
        """
        Generates all XMLs for the sittings. Each sitting gets a different XML.
        The name is sitting_[SITE_CODE]_[SITTING_N].xml
        where:
        [SITE_CODE] indicates the council (SCN) or the commissions (C01, C02, ...)
        [SITTING_N] is the sequential number of the sitting as used inside the municipality
        """

        force_overwrite = options.force
        from_date = options.fromdate

        # fetch all sittings' sites
        cursor.execute("""
            SELECT DISTINCT Tipo_Seduta FROM Votazioni
        """)

        site_rset = cursor.fetchall()
        for site_row in site_rset:
            site = site_row['Tipo_Seduta']

            #fetch all sittings in a site
            cursor.execute("""
                SELECT DISTINCT
                    NumSeduta, DataSeduta, Convocazione
                FROM
                    Votazioni
                WHERE
                    Tipo_Seduta = %s AND
                    DataSeduta > %s
                ORDER BY
                    NumSeduta, DataSeduta
            """, (site, from_date))

            sitting_rset = cursor.fetchall()
            for sitting_row in sitting_rset:
                sitting_n = sitting_row['NumSeduta']
                s = "Seduta n. %s in %s del %s" % (sitting_n, site, sitting_row['DataSeduta'])

                # new Sitting XML element
                sitting = etree.Element(OM + "Sitting",
                                        nsmap={"om":OM_NS,"xsi":XSI_NS, "xlink":XLINK_NS})
                sitting.set(XSI + "schemaLocation",
                            "http://www.openmunicipio.it DataImport.xsd")
                sitting.set("num",unicode(sitting_n))
                sitting.set("date",unicode(sitting_row['DataSeduta']))
                sitting.set("call",unicode(sitting_row['Convocazione']))
                sitting.set("site",unicode(site))

                if options.verbose > 0:
                    print s
                    print "#"*len(s)

                # fetch all votations for a sitting
                cursor.execute("""
                    SELECT DISTINCT
                        v.NumVoto,
                        v.Convocazione,
                        tv.Descrizione as TipoVoto,
                        v.Data_Ora,
                        v.NumLegale,
                        v.Maggioranza,
                        v.Presenti,
                        v.Votanti,
                        v.Astenuti,
                        v.Favorevoli,
                        v.Contrari,
                        v.Esito,
                        v.OggettoSint,
                        v.OggettoEste,
                        te.Descrizione as EsitoVotazione
                    FROM
                        Votazioni v,
                        TipoVoto tv,
                        TipoEsito te
                    WHERE
                        tv.Codice=TipoVoto AND te.Codice=v.Esito AND
                        v.Tipo_Seduta=%s AND v.NumSeduta=%s
                    ORDER BY
                        NumVoto
                    """, (site, sitting_n))

                votation_rset = cursor.fetchall()
                for votation_row in votation_rset:

                    if options.verbose > 1:
                        print votation_row

                    # new Votation XML element
                    votation = etree.SubElement(sitting, OM + "Votation")
                    votation.set("seq_n", unicode(votation_row["NumVoto"]))
                    votation.set("votation_type",unicode(votation_row["TipoVoto"]))
                    votation.set("presents", unicode(votation_row["Presenti"]))
                    votation.set("partecipants", unicode(votation_row["Votanti"]))
                    votation.set("outcome",unicode(votation_row["EsitoVotazione"]))
                    votation.set("legal_number",unicode(votation_row["NumLegale"]))
                    votation.set("date_time", unicode(votation_row["Data_Ora"]) + "T00:00:00")
                    votation.set("counter_yes", unicode(votation_row["Favorevoli"]))
                    votation.set("counter_no", unicode(votation_row["Contrari"]))
                    votation.set("counter_abs", unicode(votation_row["Astenuti"]))

                    subject = etree.SubElement(votation, OM + "Subject")
                    if votation_row["OggettoSint"] is not None:
                        subject.set("sintetic", unicode(votation_row["OggettoSint"].decode('latin1').strip()))

                    if votation_row["OggettoEste"] is not None:
                        subject.text = etree.CDATA(votation_row["OggettoEste"].decode('latin1').strip())

                    votes = etree.SubElement(votation, OM + "Votes")

                    # fetch all charge votes for a votation
                    cursor.execute("""
                        SELECT DISTINCT
                            IdComponente,
                            VotoEspresso
                        FROM
                            Votazioni_Seduta v
                        WHERE
                            IdComponente != 0 AND
                            Convocazione = %s AND
                            NumVoto = %s AND
                            Tipo_Seduta = %s AND
                            NumSeduta = %s
                        ORDER BY
                            IdComponente
                    """, (votation_row['Convocazione'], votation_row["NumVoto"], site, sitting_n))


                    cvotes_rset = cursor.fetchall()
                    for cvote_row in cvotes_rset:
                        vote = etree.SubElement(votes, OM + "ChargeVote")
                        vote.set("cardID", unicode(cvote_row["IdComponente"]))
                        vote.set("componentId", unicode(cvote_row["IdComponente"]))
                        vote.set("vote", unicode(cvote_row["VotoEspresso"]))

                        chargexref = etree.SubElement(vote, OM + "ChargeXRef")
                        chargexref.set(XLINK + "href","./%s#%s" % (settings.PEOPLE_FILENAME, unicode(cvote_row["IdComponente"])))
                        chargexref.set(XLINK + "type","simple")



                # emits the xml for this sitting
                file_name = self.sitting_file_template % (site, sitting_n)
                if options.verbose > 1:
                    print("Writing %s" % file_name)

                if os.path.isfile(file_name) and not force_overwrite:
                    print("File %s already exist, skipping this sitting. Use --force to force overwriting." % file_name)
                    continue

                # write the file
                et = etree.ElementTree(sitting)
                et.write(file_name, pretty_print=True, encoding="utf-8", xml_declaration=True)

                if options.verbose > 0:
                    print("File %s written" % file_name)

