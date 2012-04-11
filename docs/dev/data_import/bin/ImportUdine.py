import sys
import MySQLdb #as dbi
from settings import *

from lxml import etree
from os import path

from string import capwords

def write_sitting(sitting, file_name):
    print("Writing %s" % file_name)

    # check the file does not exist
    if (path.isfile(file_name)):
        print("File %s already exist, something's going wrong?!?" % file_name);
        return

    # write the file
    et = etree.ElementTree(sitting)
    et.write(file_name,pretty_print=True,encoding="utf-8",xml_declaration=True)
    print("File %s written" % file_name)

def write_people(people, file_name):
    print("Writing %s" % file_name)

    # check the file does not exist
    if (path.isfile(file_name)):
        print("File %s already exist, something's going wrong?!?" % file_name);
        return

    # write the file
    et = etree.ElementTree(people)
    et.write(file_name,pretty_print=True,encoding="utf-8",xml_declaration=True)
    print("File %s written" % file_name)


def latin1ToUtf8(currString):
    if (currString == None):
        return ""
    return currString.decode("latin1").encode("utf8")


try:
    conn = MySQLdb.connect(host = DB_HOST,user = DB_USER,
        passwd = DB_PWD,db = DB_NAME)

#    conn.set_character_set("utf8")
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
#    cursor.execute('SET NAMES utf8;')
#    cursor.execute('SET CHARACTER SET utf8;')
#    cursor.execute('SET character_set_connection=utf8;')

    cursor.execute("""
    SELECT DISTINCT
        Votazioni.Tipo_Seduta,
        Votazioni.Convocazione,
        Votazioni.NumSeduta,
        Votazioni.NumVoto, 
        tv.Descrizione as TipoVoto, 
        Votazioni.Data_Ora, 
        Votazioni.NumLegale, 
        Votazioni.Maggioranza, 
        Votazioni.Presenti, 
        Votazioni.Votanti, 
        Votazioni.Astenuti, 
        Votazioni.Favorevoli, 
        Votazioni.Contrari, 
        Votazioni.Esito, 
        Votazioni.OggettoSint, 
        Votazioni.OggettoEste,
        te.Descrizione as EsitoVotazione
    FROM
        Votazioni, 
        TipoVoto tv,
        TipoEsito te 
    WHERE
        tv.Codice=TipoVoto AND Votazioni.Tipo_Seduta='SCN' AND
        te.Codice=Votazioni.Esito
    ORDER BY
        NumSeduta, NumVoto
    """)

    rset = cursor.fetchall()

   # configure lxml
    XSI_NS="http://www.w3.org/2001/XMLSchema-instance"
    XSI = "{%s}" % XSI_NS
    OM_NS="http://www.openmunicipio.it"
    OM = "{%s}" % OM_NS
    XLINK_NS="http://www.w3.org/1999/xlink"
    XLINK = "{%s}" % XLINK_NS

    prevSitting = -1
    sitting = None
    for row in rset:

        try:
            if prevSitting != row["NumSeduta"]:
                if (sitting != None):
                    file_name=SITTING_FILENAME % ("SCN",prevSitting)
                    write_sitting(sitting=sitting, file_name=file_name)
                # new Sitting element
                sitting = etree.Element(OM + "Sitting",
                    nsmap={"om":OM_NS,"xsi":XSI_NS, "xlink":XLINK_NS})
                sitting.set(XSI + "schemaLocation",
                    "http://www.openmunicipio.it DataImport.xsd")
                sitting.set("num",unicode(row["NumSeduta"]))
                sitting.set("date",unicode(row["Data_Ora"]))
                sitting.set("call",unicode(row["Convocazione"]))
    
                prevSitting = row["NumSeduta"]
            votation = etree.SubElement(sitting, OM + "Votation")
            votation.set("seq_n", unicode(row["NumVoto"]))
            votation.set("votation_type",unicode(row["TipoVoto"]))
            votation.set("presents", unicode(row["Presenti"]))
            votation.set("partecipants", unicode(row["Votanti"]))
            votation.set("outcome",unicode(row["EsitoVotazione"]))
            votation.set("legal_number",unicode(row["NumLegale"]))
            votation.set("date_time", unicode(row["Data_Ora"]) + "T00:00:00")
            votation.set("counter_yes", unicode(row["Favorevoli"]))
            votation.set("counter_no", unicode(row["Contrari"]))
            votation.set("counter_abs", unicode(row["Astenuti"]))
    
            subject = etree.SubElement(votation, OM + "Subject")
    # TODO appare un errore se decommento la stringa sotto. capire perche`
#            print ("Sint = %s" % latin1ToUtf8(row["OggettoSint"]))
            subject.set("sintetic", latin1ToUtf8(row["OggettoSint"]).strip())

            if (row["OggettoEste"] != None):
#                print("Este = %s" % latin1ToUtf8(row["OggettoEste"]).strip())

                subject.text = etree.CDATA(str(latin1ToUtf8(row["OggettoEste"])).strip())

            votes = etree.SubElement(votation, OM + "Votes")
    
            cursor.execute("""
            SELECT DISTINCT
                IdComponente,
                VotoEspresso
            FROM
                Votazioni_Seduta
            WHERE
                Votazioni_Seduta.IdComponente <> 0
                AND Votazioni_Seduta.Convocazione = %s
                AND Votazioni_Seduta.NumVoto = %s
                AND Votazioni_Seduta.NumSeduta = %s
                AND Votazioni_Seduta.Tipo_Seduta = 'SCN'
            ORDER BY
                IdComponente
            """ % (row["Convocazione"],row["NumVoto"],row["NumSeduta"]))
    
            rset_cvotes = cursor.fetchall()
    
            for row_cvote in rset_cvotes:
                vote = etree.SubElement(votes, OM + "ChargeVote")
                vote.set("cardID", unicode(row_cvote["IdComponente"]))
                vote.set("componentId", unicode(row_cvote["IdComponente"]))
                vote.set("vote", unicode(row_cvote["VotoEspresso"]))

                chargexref = etree.SubElement(vote, OM + "ChargeXRef")
                chargexref.set(XLINK + "href","%s#%s" % (PEOPLE_FILENAME,unicode(row_cvote["IdComponente"])))
                chargexref.set(XLINK + "type","simple")
           
    #    print (etree.tostring(sittings, pretty_print=True))
        except Exception, e:
            print("Error processing current row (NumSeduta=%d). Message: %s" % (prevSitting, e)) 

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
        charge.set("description", "Consigliere")

        person = etree.SubElement(charge, "Person")
        person.set("first_name", unicode(capwords(row["Nome"])))
        person.set("last_name",unicode(capwords(row["Cognome"])))

    write_people(people, "people.xml")

except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)
