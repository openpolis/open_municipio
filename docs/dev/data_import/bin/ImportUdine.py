import sys
import MySQLdb #as dbi

from lxml import etree

try:
    conn = MySQLdb.connect(host = "localhost",user = "root",
        passwd = "mypassword",db = "udine")
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
    SELECT DISTINCT
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
    XSI_NS="http://www.w3.org/2011/XMLSchema-instance"
    XSI = "{%s}" % XSI_NS
    OM_NS="http://www.openmunicipio.it"
    OM = "{%s}" % OM_NS
    sittings = etree.Element(OM + "Sittings", 
        nsmap={"om":OM_NS,"xsi":XSI_NS})

    sittings.set(XSI + "schemaLocation", 
        "http://www.openmunicipio.it DataImport.xsd")

    prevSitting = -1
    sitting = None
    for row in rset:
        if prevSitting != row["NumSeduta"]:
            # new Sitting element
            # print("Seduta %s" % row["NumSeduta"])
            sitting = etree.SubElement(sittings, OM + "Sitting")
            sitting.set("num",str(row["NumSeduta"]))
            sitting.set("date",str(row["Data_Ora"]))
            sitting.set("call",str(row["Convocazione"]))

            prevSitting = row["NumSeduta"]
#        print("Votation %s" % (row["NumVoto"],), row)
        votation = etree.SubElement(sitting, OM + "Votation")
        votation.set("seq_n", str(row["NumVoto"]))
        votation.set("votation_type",str(row["TipoVoto"]))
        votation.set("presents", str(row["Presenti"]))
        votation.set("partecipants", str(row["Votanti"]))
        votation.set("outcome",str(row["EsitoVotazione"]))
        votation.set("legal_number",str(row["NumLegale"]))
        votation.set("date_time", str(row["Data_Ora"]) + "T00:00:00")
        votation.set("counter_yes", str(row["Favorevoli"]))
        votation.set("counter_no", str(row["Contrari"]))
        votation.set("counter_abs", str(row["Astenuti"]))

        subject = etree.SubElement(votation, OM + "Subject")
# TODO appare un errore se decommento la stringa sotto. capire perche`
#        if not(row["OggettoSint"] is None) and (len(row["OggettoSint"]) > 0):
#            print ("Sint = %s" % row["OggettoSint"])
#            subject.set("sintetic", "%s" % str(row["OggettoSint"]))
#            str("" if row["OggettoSint"] is None else row["OggettoSint"]))
#        subject.text = str(row["OggettoEste"])

        votes = etree.SubElement(votation, OM + "Votes")

        cursor.execute("""
        SELECT DISTINCT
--            Nome,
--            Cognome,
            IdComponente,
            VotoEspresso
        FROM
--            Anagrafica_Consiglieri,
            Votazioni_Seduta
        WHERE
--            Anagrafica_Consiglieri.IdConsigliere = Votazioni_Seduta.IdComponente AND 
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
            vote.set("cardID", str(row_cvote["IdComponente"]))
            vote.set("componentId", str(row_cvote["IdComponente"]))
            vote.set("vote", str(row_cvote["VotoEspresso"]))
        
    print (etree.tostring(sittings, pretty_print=True))
    
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)
