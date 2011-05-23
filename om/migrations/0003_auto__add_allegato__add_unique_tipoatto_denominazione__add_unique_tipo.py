# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Allegato'
        db.create_table(u'om_allegato', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('titolo', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('atto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['om.Atto'])),
            ('data', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('testo', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('file_pdf', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('url_testo', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('url_pdf', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('om', ['Allegato'])

        # Adding unique constraint on 'TipoAtto', fields ['denominazione']
        db.create_unique(u'om_tipo_atto', ['denominazione'])

        # Adding unique constraint on 'TipoAtto', fields ['slug']
        db.create_unique(u'om_tipo_atto', ['slug'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'TipoAtto', fields ['slug']
        db.delete_unique(u'om_tipo_atto', ['slug'])

        # Removing unique constraint on 'TipoAtto', fields ['denominazione']
        db.delete_unique(u'om_tipo_atto', ['denominazione'])

        # Deleting model 'Allegato'
        db.delete_table(u'om_allegato')


    models = {
        'om.allegato': {
            'Meta': {'object_name': 'Allegato'},
            'atto': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['om.Atto']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'created_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'titolo': ('django.db.models.fields.CharField', [], {'max_length': '196', 'blank': 'True'}),
            'titolo_aggiuntivo': ('django.db.models.fields.CharField', [], {'max_length': '196', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
