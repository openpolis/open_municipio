Protocollo di scambio dati XML
==============================

Contesto
--------
I flussi XML richiesti hanno lo scopo di alimentare la base dati dell'applicazione web Open Municipio, per il monitoraggio delle attività del Comune da parte dei cittadini.

Oggetto dell'applicazione sono: 

* la composizione degli organi istituzionali e politici del Comune (sindaco, Giunta, Consiglio, Commissioni, Gruppi Consiliari, Aziende Partecipate), 
* gli Atti emanati dalle istituzioni e il loro iter legislativo (Proposte di Delibere, Interrogazioni, Interpellanze, Mozioni, Ordini del Giorno, Decreti, Ordinanze, ... )
* le discussioni (interventi) e le votazioni relative agli atti di cui sopra

Questo documento definisce il protocollo di scambio dati tra un generico comune e l'applicazione web.
I dettagli delle modifiche al protocollo da apportare per integrare dati provenienti da diversi comuni, che adottano soluzioni tecniche e approcci al dominio differenti, sono descritti in un allegato a parte.

Nota metodologica
-----------------
Si è scelta la lingua inglese per lo schema XSD per non impedire al progetto, in futuro, una possibile valenza internazionale.


Schema e istanze
----------------
Per lo scambio dati si è definito uno schema XML, in formato XSD, definito secondo le `raccomandazioni del W3C`_, che descrive la tipologia dei flussi XML da scambiare.
Assieme allo schema, sono fornite istanze di esempio, in formato XML, che implementano lo schema.

**OM-XML.xsd**
  è lo schema XML (`visualizza`__)

.. __: ../../../data_import/schema/OM-XML.xsd

**institutions_sample.xml**
  esempio di flusso che definisce la composizione degli organi istituzionale di un Comune (`visualizza`__)

.. __: ./institutions_sample.xml

**deliberation_sample_20120229.xml** e **deliberation_sample_20120301.xml**
  esempi di proposta di delibera consiliare (2 snapshot di date diverse) 
  (`visualizza prima snapshot`_, `visualizza seconda snapshot`_)

.. _`visualizza prima snapshot`: ./deliberation_sample_20120229.xml
.. _`visualizza seconda snapshot`: ./deliberation_sample_20120301.xml

**sitting_sample.xml**
  esempio di votazioni relative a una seduta (`visualizza`__)

.. __: ./sitting_sample.xml

.. _`raccomandazioni del W3C`: http://www.w3.org/TR/xmlschema-0/

Lo schema XSD si limita a descrivere la struttura dei dati e la loro tipologia, non definisce le modalità in cui i flussi vengono scambiati (invio file, web service).

Per questo, nello schema, tutti i dati sono descritti insieme, come se fosse possibile, in linea di principio, ottenere tutti i dati di un Comune (composizione, atti e votazioni) in un unico gigantesco flusso.

Naturalmente questo approccio non è realistico e non sarebbe neanche efficiente, dato che per ogni minima variazione, sarebbe necessario rigenerare tutto il flusso. Vedremo più avanti il dettaglio della trasmissione dei flussi e come sia immaginato in modo da ottimizzare la gestione di *variazioni* nel tempo delle strutture del dominio.

Il punto di partenza dello schema XSD è l'elemento OpenMunicipio, che è descritto come una sequenza di elementi People, Acts e Sittings. A loro volta questi elementi sono suddivisi secondo una struttura ad albero illustrata schematicamente qui di seguito::

  OpenMunicipio
  |- People (composizione organi istituzionale)
  |  |- Offices (uffici amministrativi)
  |  |- Companies (aziende partecipate)
  |  |- Institutions (istituzioni)
  |  |- Groups (gruppi politici)
  |- Acts (atti istituzionali)
  |  |- ActsCouncil (atti consiglio)
  |  |  |- Interrogation
  |  |  |- Interpellation
  |  |  |- Motion
  |  |  |- Agenda (ordine del giorno)
  |  |  |- Emendation (emendamento)
  |  |  |- CouncilDeliberation (proposta di delibera)
  |  |- ActsCityGovernment (atti giunta)
  |  |  |- Investigation (investigazione)
  |  |  |- Decision (decisione giuntale)
  |  |  |- CityGovernmentDeliberation (delibera di giunta)
  |  |- ActsMayor (atti del Sindaco)
  |  |  |- Decree (decreto)
  |  |  |- Regulation (???)
  |  |- ActsOffices (atti amministrativi uffici)
  |  |  |- Determination (determina dirigenziale)
  |- Sittings (sedute di consiglio, giunta o commissione)


Dettaglio flussi XML
--------------------

Di seguito un esempio dei flussi che ci aspettiamo.

Viene utilizzata la notazione usata per i *filesystem*, e le URL,
con il carattere "/" usato come separatore delle directories.
Questo perché, sia nel caso di flussi offerti come web services, sia nel caso di invio files, questa notazione può essere usata per identificare univocamente il flusso in un albero di risorse.

Il nome del flusso contiene sempre un *timestamp*, che indica la data di produzione del flusso,
in modo che sia possibile gestire le variazioni nel tempo della struttura dati descritta.
Il formato della data è [aaammgg] il 29 febbraio 2012 viene espresso come 20120229.

Si fa riferimento ai files di esempio rilasciati assieme a questa documentazione
che contengono codice XML commentato, in modo da guidare alla comprensione della struttura dati.

**people/institutions_[aaaammgg].xml**
  contiene i dettagli degli organi istituzionali alla data indicata
  si veda il file institutions_sample.xml per il dettaglio della struttura dati

**people/offices_[aaaammgg].xml**
  contiene il dettaglio della composizione degli uffici amministrativi del comune
  # TODO
  
**people/companies_[aaaammgg].xml**
  contiene il dettaglio della composizione delle aziende municipalizzate o partecipate

**acts/acts_council/interrogation_[internal_id]_[aaaammgg].xml**
  contiene il dettaglio dell'interrogazione che, nel sistema informativo del Comune ha
  identificativo univoco ``internal_id``, alla data specificata dal timestamp; 
  si veda il file interrogation_sample.xml per il dettaglio della struttura dati
  
**acts/acts_council/deliberation_[internal_id]_[aaaammgg].xml**
  contiene il dettaglio della delibera (o proposta di deliberazione) che, nel sistema informativo del Comune ha
  identificativo univoco ``internal_id``, alla data specificata dal timestamp; 
  si veda il file deliberation_sample.xml per il dettaglio della struttura dati;
  
**sittings/sitting_[internal_id].xml**
  contiene il dettaglio di una seduta, con i dati relativi alle votazioni, ed eventualmente agli interventi,
  che in quella seduta sono occorsi; si veda il file sitting_sample.xml

  
Protocollo di scambio (principi generali)
-----------------------------------------
Sono enunciati alcuni principi generali,  
in quanto c'è da definire i dettagli e le eccezioni, di volta in volta con il Comune interessato.

Lo scambio dei files può avvenire secondo due modalità, alternative:

in Modalita PUSH (invio files o pacchetto)
++++++++++++++++++++++++++++++++++++++++++
Il Comune invia i dati su nostri server, in modalità PUSH, seguendo uno dei protocolli
standard (FTP, SSH, RSYNC, SVN, ...) da decidere assieme.

In questo caso siamo noi a gestire il servizio e il comune effettua le connessioni come client
quando ci sono comunicazioni da inviare.

In questo caso è sufficiente inviare i files che contengono cambiamenti rispetto agli ultimi inviati,
ricordandosi di aggiungere il timestamp della data di generazione nel nome del file.

in Modalità PULL
++++++++++++++++
Il Comune mette a disposizione un area condivisa con noi, dove noi andiamo a prendere i files.
Il protocollo di lettura può essere HTTP, FTP, SSH, RSYNC, SVN, anche qui da decidere assieme.

In questo caso è il Comune che ospita il server e noi che, periodicamente andiamo a leggere.

Per ottimizzare il numero di pagine lette e la velocità dell'operazione,
sarebbe utile avere un file aggiornato contenente l'elenco dei file cambiati, in modo da
leggere per primo quello.




