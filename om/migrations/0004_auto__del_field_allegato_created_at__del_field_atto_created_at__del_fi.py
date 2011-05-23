# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Allegato.created_at'
        db.delete_column('om_allegato', 'created_at')

        # Deleting field 'Atto.created_at'
        db.delete_column('om_atto', 'created_at')

        # Deleting field 'Atto.updated_at'
        db.delete_column('om_atto', 'updated_at')


    def backwards(self, orm):
        
        # Adding field 'Allegato.created_at'
        db.add_column('om_allegato', 'created_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)

        # Adding field 'Atto.created_at'
        db.add_column('om_atto', 'created_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)

        # Adding field 'Atto.updated_at'
        db.add_column('om_atto', 'updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)


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
            'data_aggiornamento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_approvazione': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_esecuzione': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_presentazione': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'data_pubblicazione': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'iniziativa': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
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
