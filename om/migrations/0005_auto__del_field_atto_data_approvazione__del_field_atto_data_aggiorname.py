# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Atto.data_approvazione'
        db.delete_column('om_atto', 'data_approvazione')

        # Deleting field 'Atto.data_aggiornamento'
        db.delete_column('om_atto', 'data_aggiornamento')

        # Deleting field 'Atto.data_presentazione'
        db.delete_column('om_atto', 'data_presentazione')

        # Deleting field 'Atto.data_esecuzione'
        db.delete_column('om_atto', 'data_esecuzione')

        # Deleting field 'Atto.data_pubblicazione'
        db.delete_column('om_atto', 'data_pubblicazione')


    def backwards(self, orm):
        
        # Adding field 'Atto.data_approvazione'
        db.add_column('om_atto', 'data_approvazione', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Atto.data_aggiornamento'
        db.add_column('om_atto', 'data_aggiornamento', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Atto.data_presentazione'
        db.add_column('om_atto', 'data_presentazione', self.gf('django.db.models.fields.DateField')(null=True), keep_default=False)

        # Adding field 'Atto.data_esecuzione'
        db.add_column('om_atto', 'data_esecuzione', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Atto.data_pubblicazione'
        db.add_column('om_atto', 'data_pubblicazione', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)


    models = {
        'om.allegato': {
            'Meta': {'object_name': 'Allegato'},
            'atto': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['om.Atto']"}),
            'data': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'file_pdf': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'testo': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'titolo': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url_pdf': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'url_testo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'om.atto': {
            'Meta': {'object_name': 'Atto'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'iniziativa': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'testo': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tipo_atto': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['om.TipoAtto']"}),
            'titolo': ('django.db.models.fields.CharField', [], {'max_length': '196'}),
            'titolo_aggiuntivo': ('django.db.models.fields.CharField', [], {'max_length': '196', 'blank': 'True'}),
            'verbale': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'om.tipoatto': {
            'Meta': {'object_name': 'TipoAtto', 'db_table': "u'om_tipo_atto'"},
            'denominazione': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        }
    }

    complete_apps = ['om']
