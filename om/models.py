from django.db import models

class Atto(models.Model):
    INIZIATIVA_CHOICES = (
        ('con', 'Consigliere'),
        ('pre', 'Presidente'),
        ('ass', 'Assessore'),
        ('giu', 'Giunta'),
        ('sin', 'Sindaco'),
    )
    idnum = models.CharField(max_length=128, blank=True)
    tipo_atto = models.ForeignKey('TipoAtto')
    data_presentazione = models.DateField(null=True)
    data_aggiornamento = models.DateField(null=True, blank=True)
    data_approvazione = models.DateField(null=True, blank=True)
    data_pubblicazione = models.DateField(null=True, blank=True)
    data_esecuzione = models.DateField(null=True, blank=True)
    titolo = models.CharField(max_length=196, blank=True)
    titolo_aggiuntivo = models.CharField(max_length=196, blank=True)
    iniziativa = models.CharField(max_length=3, choices=INIZIATIVA_CHOICES)
    testo = models.TextField(blank=True)
    verbale = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
      uc = u'%s: %s' % (self.tipo_atto, self.titolo)
      if self.idnum:
        uc = u'%s - %s' % (self.idnum, uc)
      if self.titolo_aggiuntivo:
        uc = u'%s (%s)' % (uc, self.titolo_aggiuntivo)
      return uc
      
    class Meta:
        db_table = u'om_atto'
        verbose_name_plural = u'atti'

class TipoAtto(models.Model):
    denominazione = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
      return u'%s' % self.denominazione
      
    class Meta:
        db_table = u'om_tipo_atto'
        verbose_name_plural = u'tipi atto'


class Allegato(models.Model):
    titolo = models.CharField(max_length=255)
    atto = models.ForeignKey('Atto')
    data = models.DateField(null=True, blank=True)
    testo = models.TextField(blank=True)
    file_pdf = models.FileField(upload_to="allegati/%Y%d%m", blank=True)
    url_testo = models.CharField(max_length=255, blank=True)
    url_pdf = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
      return u'%s' % self.titolo

    class Meta:
        db_table = u'om_allegato'
        verbose_name_plural = u'allegati'

'''



class AttoHasIter(models.Model):
    atto = models.ForeignKey('Atto')
    aiter = models.ForeignKey('Iter')
    data = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'opm_atto_has_iter'

class Iter(models.Model):
    fase = models.CharField(max_length=765, blank=True)
    concluso = models.IntegerField(null=True, blank=True)
    cache_cod = models.CharField(max_length=6, blank=True)
    class Meta:
        db_table = u'opm_iter'


class AttoHasSede(models.Model):
    atto = models.ForeignKey('Atto')
    sede = models.ForeignKey('Sede')
    tipo = models.CharField(max_length=765, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'opm_atto_has_sede'

class Sede(models.Model):
    codice = models.CharField(max_length=765, blank=True)
    ramo = models.CharField(max_length=765, blank=True)
    denominazione = models.CharField(max_length=765, blank=True)
    legislatura = models.IntegerField(null=True, blank=True)
    tipologia = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'opm_sede'

class EsitoSeduta(models.Model):
    atto = models.ForeignKey('Atto')
    sede = models.ForeignKey('Sede')
    data = models.DateField(null=True, blank=True)
    url = models.TextField()
    esito = models.TextField(blank=True)
    tipologia = models.CharField(max_length=765, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'opm_esito_seduta'

class Resoconto(models.Model):
    sede = models.ForeignKey('Sede')
    data = models.DateField(null=True, blank=True)
    comunicato = models.TextField(blank=True)
    sommario = models.TextField(blank=True)
    stenografico = models.TextField(blank=True)
    num_seduta = models.IntegerField(null=True, blank=True)
    legislatura = models.IntegerField()
    nota = models.TextField(blank=True)
    url_sommario = models.CharField(max_length=765, blank=True)
    url_stenografico = models.CharField(max_length=765, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    url_comunicato = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'opm_resoconto'



class Politico(models.Model):
    nome = models.CharField(max_length=90, blank=True)
    cognome = models.CharField(max_length=90, blank=True)
    n_monitoring_users = models.IntegerField()
    sesso = models.CharField(max_length=3, blank=True)
    class Meta:
        db_table = u'opm_politico'


class Carica(models.Model):
    politico = models.ForeignKey('Politico')
    tipo_carica = models.ForeignKey('TipoCarica')
    carica = models.CharField(max_length=90, blank=True)
    data_inizio = models.DateField(null=True, blank=True)
    data_fine = models.DateField(null=True, blank=True)
    legislatura = models.IntegerField(null=True, blank=True)
    circoscrizione = models.CharField(max_length=180, blank=True)
    presenze = models.IntegerField(null=True, blank=True)
    assenze = models.IntegerField(null=True, blank=True)
    missioni = models.IntegerField(null=True, blank=True)
    parliament_id = models.IntegerField(null=True, blank=True)
    indice = models.FloatField(null=True, blank=True)
    scaglione = models.IntegerField(null=True, blank=True)
    posizione = models.IntegerField(null=True, blank=True)
    media = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    ribelle = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'opm_carica'

class CaricaInterna(models.Model):
    id = models.IntegerField(primary_key=True)
    carica = models.ForeignKey('Carica')
    tipo_carica = models.ForeignKey('TipoCarica')
    sede = models.ForeignKey(Sede)
    data_inizio = models.DateField(null=True, blank=True)
    data_fine = models.DateField(null=True, blank=True)
    descrizione = models.CharField(max_length=765, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'opm_carica_interna'

class TipoCarica(models.Model):
    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'opm_tipo_carica'



class CaricaHasAtto(models.Model):
    atto = models.ForeignKey('Atto')
    carica = models.ForeignKey('Carica')
    tipo = models.CharField(max_length=765)
    data = models.DateField(null=True, blank=True)
    url = models.TextField(blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    delete_at = models.DateField(null=True, blank=True)
    class Meta:
        db_table = u'opm_carica_has_atto'


class Gruppo(models.Model):
    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=765, blank=True)
    acronimo = models.CharField(max_length=240, blank=True)
    class Meta:
        db_table = u'opm_gruppo'

class GruppoIsMaggioranza(models.Model):
    id = models.IntegerField(primary_key=True)
    gruppo = models.ForeignKey('Gruppo')
    data_inizio = models.DateField()
    data_fine = models.DateField(null=True, blank=True)
    maggioranza = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'opm_gruppo_is_maggioranza'


class CaricaHasGruppo(models.Model):
    carica = models.ForeignKey('Carica')
    gruppo = models.ForeignKey('Gruppo')
    data_inizio = models.DateField(primary_key=True)
    data_fine = models.DateField(null=True, blank=True)
    ribelle = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    presenze = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'opm_carica_has_gruppo'


class Seduta(models.Model):
    data = models.DateField(null=True, blank=True)
    numero = models.IntegerField()
    ramo = models.CharField(max_length=3)
    legislatura = models.IntegerField()
    url = models.TextField(blank=True)
    is_imported = models.IntegerField()
    class Meta:
        db_table = u'opm_seduta'

class Intervento(models.Model):
    atto = models.ForeignKey('Atto')
    carica = models.ForeignKey('Carica')
    tipologia = models.CharField(max_length=765, blank=True)
    url = models.TextField(blank=True)
    data = models.DateField(null=True, blank=True)
    sede = models.ForeignKey(Sede)
    numero = models.IntegerField(null=True, blank=True)
    ap = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    ut_fav = models.IntegerField()
    ut_contr = models.IntegerField()
    class Meta:
        db_table = u'opm_intervento'

class Votazione(models.Model):
    seduta = models.ForeignKey('Seduta')
    numero_votazione = models.IntegerField()
    titolo = models.TextField(blank=True)
    presenti = models.IntegerField(null=True, blank=True)
    votanti = models.IntegerField(null=True, blank=True)
    maggioranza = models.IntegerField(null=True, blank=True)
    astenuti = models.IntegerField(null=True, blank=True)
    favorevoli = models.IntegerField(null=True, blank=True)
    contrari = models.IntegerField(null=True, blank=True)
    esito = models.CharField(max_length=60, blank=True)
    ribelli = models.IntegerField(null=True, blank=True)
    margine = models.IntegerField(null=True, blank=True)
    tipologia = models.CharField(max_length=60, blank=True)
    descrizione = models.TextField(blank=True)
    url = models.CharField(max_length=765, blank=True)
    finale = models.IntegerField()
    nb_commenti = models.IntegerField()
    is_imported = models.IntegerField()
    titolo_aggiuntivo = models.TextField(blank=True)
    ut_fav = models.IntegerField()
    ut_contr = models.IntegerField()
    class Meta:
        db_table = u'opm_votazione'

class VotazioneHasAtto(models.Model):
    votazione = models.ForeignKey('Votazione')
    atto = models.ForeignKey('Atto')
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'opm_votazione_has_atto'

class VotazioneHasCarica(models.Model):
    votazione = models.ForeignKey('Votazione')
    carica = models.ForeignKey('Carica')
    voto = models.CharField(max_length=120, blank=True)
    ribelle = models.IntegerField()
    class Meta:
        db_table = u'opm_votazione_has_carica'

class VotazioneHasGruppo(models.Model):
    votazione = models.ForeignKey('Votazione')
    gruppo = models.ForeignKey('Gruppo')
    voto = models.CharField(max_length=120, blank=True)
    class Meta:
        db_table = u'opm_votazione_has_gruppo'
'''        
