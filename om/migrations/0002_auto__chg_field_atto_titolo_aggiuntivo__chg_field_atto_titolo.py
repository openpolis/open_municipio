# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Atto.titolo_aggiuntivo'
        db.alter_column(u'om_atto', 'titolo_aggiuntivo', self.gf('django.db.models.fields.CharField')(max_length=196))

        # Changing field 'Atto.titolo'
        db.alter_column(u'om_atto', 'titolo', self.gf('django.db.models.fields.CharField')(max_length=196))


    def backwards(self, orm):
        
        # Changing field 'Atto.titolo_aggiuntivo'
        db.alter_column(u'om_atto', 'titolo_aggiuntivo', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Atto.titolo'
        db.alter_column(u'om_atto', 'titolo', self.gf('django.db.models.fields.TextField')())


    models = {
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
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        }
    }

    complete_apps = ['om']
