# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Atto'
        db.create_table(u'om_atto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idnum', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('tipo_atto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['om.TipoAtto'])),
            ('data_presentazione', self.gf('django.db.models.fields.DateField')(null=True)),
            ('data_aggiornamento', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('data_approvazione', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('data_pubblicazione', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('data_esecuzione', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('titolo', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('titolo_aggiuntivo', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('iniziativa', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('testo', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('verbale', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('om', ['Atto'])

        # Adding model 'TipoAtto'
        db.create_table(u'om_tipo_atto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('denominazione', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
        ))
        db.send_create_signal('om', ['TipoAtto'])


    def backwards(self, orm):
        
        # Deleting model 'Atto'
        db.delete_table(u'om_atto')

        # Deleting model 'TipoAtto'
        db.delete_table(u'om_tipo_atto')


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
            'titolo': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'titolo_aggiuntivo': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
