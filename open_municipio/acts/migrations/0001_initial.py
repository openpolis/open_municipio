# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Act'
        db.create_table('acts_act', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('idnum', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('adj_title', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('presentation_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('emitting_institution', self.gf('django.db.models.fields.related.ForeignKey')(related_name='emitted_act_set', to=orm['people.Institution'])),
            ('status_is_final', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_key', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('acts', ['Act'])

        # Adding M2M table for field recipient_set on 'Act'
        m2m_table_name = db.shorten_name('acts_act_recipient_set')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('act', models.ForeignKey(orm['acts.act'], null=False)),
            ('institutioncharge', models.ForeignKey(orm['people.institutioncharge'], null=False))
        ))
        db.create_unique(m2m_table_name, ['act_id', 'institutioncharge_id'])

        # Adding M2M table for field category_set on 'Act'
        m2m_table_name = db.shorten_name('acts_act_category_set')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('act', models.ForeignKey(orm['acts.act'], null=False)),
            ('category', models.ForeignKey(orm['taxonomy.category'], null=False))
        ))
        db.create_unique(m2m_table_name, ['act_id', 'category_id'])

        # Adding model 'ActSection'
        db.create_table(u'acts_act_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Act'], on_delete=models.PROTECT)),
            ('parent_section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.ActSection'], on_delete=models.PROTECT)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acts', ['ActSection'])

        # Adding model 'ActSupport'
        db.create_table(u'acts_act_support', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.InstitutionCharge'])),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Act'])),
            ('support_type', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('support_date', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('acts', ['ActSupport'])

        # Adding model 'ActDescriptor'
        db.create_table(u'acts_act_descriptor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Act'])),
        ))
        db.send_create_signal('acts', ['ActDescriptor'])

        # Adding model 'CGDeliberation'
        db.create_table('acts_cgdeliberation', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('approval_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('publication_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('final_idnum', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('execution_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('initiative', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('approved_text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acts', ['CGDeliberation'])

        # Adding model 'Deliberation'
        db.create_table('acts_deliberation', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('approval_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('publication_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('final_idnum', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('execution_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('initiative', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('approved_text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acts', ['Deliberation'])

        # Adding model 'Interrogation'
        db.create_table('acts_interrogation', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('answer_type', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('question_motivation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('answer_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('reply_text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acts', ['Interrogation'])

        # Adding model 'Interpellation'
        db.create_table('acts_interpellation', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('answer_type', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('question_motivation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('answer_text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acts', ['Interpellation'])

        # Adding model 'Motion'
        db.create_table('acts_motion', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=12)),
        ))
        db.send_create_signal('acts', ['Motion'])

        # Adding model 'Agenda'
        db.create_table('acts_agenda', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=12)),
        ))
        db.send_create_signal('acts', ['Agenda'])

        # Adding model 'Amendment'
        db.create_table('acts_amendment', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(related_name='amendment_set', on_delete=models.PROTECT, to=orm['acts.Act'])),
            ('act_section', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='amendment_set', null=True, on_delete=models.PROTECT, to=orm['acts.ActSection'])),
        ))
        db.send_create_signal('acts', ['Amendment'])

        # Adding model 'Transition'
        db.create_table(u'acts_transition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('final_status', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transition_set', to=orm['acts.Act'])),
            ('votation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['votations.Votation'], null=True, blank=True)),
            ('transition_date', self.gf('django.db.models.fields.DateField')(default=None)),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('acts', ['Transition'])

        # Adding model 'Attach'
        db.create_table('acts_attach', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('document_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('document_type', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('document_size', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('text_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('file_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=255, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachment_set', to=orm['acts.Act'])),
        ))
        db.send_create_signal('acts', ['Attach'])

        # Adding model 'Speech'
        db.create_table('acts_speech', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('document_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('document_type', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('document_size', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('text_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('file_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=255, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('sitting_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.SittingItem'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'], null=True, blank=True)),
            ('author_name_when_external', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('votation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['votations.Votation'], null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('seq_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('initial_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('audio_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('audio_file', self.gf('django.db.models.fields.files.FileField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('acts', ['Speech'])

        # Adding model 'ActHasSpeech'
        db.create_table('acts_acthasspeech', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('speech', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Speech'])),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Act'])),
            ('relation_type', self.gf('django.db.models.fields.CharField')(max_length=4)),
        ))
        db.send_create_signal('acts', ['ActHasSpeech'])

        # Adding model 'Calendar'
        db.create_table('acts_calendar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Institution'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('acts', ['Calendar'])

        # Adding M2M table for field act_set on 'Calendar'
        m2m_table_name = db.shorten_name('acts_calendar_act_set')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('calendar', models.ForeignKey(orm['acts.calendar'], null=False)),
            ('act', models.ForeignKey(orm['acts.act'], null=False))
        ))
        db.create_unique(m2m_table_name, ['calendar_id', 'act_id'])


    def backwards(self, orm):
        # Deleting model 'Act'
        db.delete_table('acts_act')

        # Removing M2M table for field recipient_set on 'Act'
        db.delete_table(db.shorten_name('acts_act_recipient_set'))

        # Removing M2M table for field category_set on 'Act'
        db.delete_table(db.shorten_name('acts_act_category_set'))

        # Deleting model 'ActSection'
        db.delete_table(u'acts_act_section')

        # Deleting model 'ActSupport'
        db.delete_table(u'acts_act_support')

        # Deleting model 'ActDescriptor'
        db.delete_table(u'acts_act_descriptor')

        # Deleting model 'CGDeliberation'
        db.delete_table('acts_cgdeliberation')

        # Deleting model 'Deliberation'
        db.delete_table('acts_deliberation')

        # Deleting model 'Interrogation'
        db.delete_table('acts_interrogation')

        # Deleting model 'Interpellation'
        db.delete_table('acts_interpellation')

        # Deleting model 'Motion'
        db.delete_table('acts_motion')

        # Deleting model 'Agenda'
        db.delete_table('acts_agenda')

        # Deleting model 'Amendment'
        db.delete_table('acts_amendment')

        # Deleting model 'Transition'
        db.delete_table(u'acts_transition')

        # Deleting model 'Attach'
        db.delete_table('acts_attach')

        # Deleting model 'Speech'
        db.delete_table('acts_speech')

        # Deleting model 'ActHasSpeech'
        db.delete_table('acts_acthasspeech')

        # Deleting model 'Calendar'
        db.delete_table('acts_calendar')

        # Removing M2M table for field act_set on 'Calendar'
        db.delete_table(db.shorten_name('acts_calendar_act_set'))


    models = {
        'acts.act': {
            'Meta': {'object_name': 'Act'},
            'adj_title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'category_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['taxonomy.Category']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'emitting_institution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'emitted_act_set'", 'to': "orm['people.Institution']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'is_key': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['locations.Location']", 'null': 'True', 'through': "orm['locations.TaggedActByLocation']", 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'presentation_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'presenter_set': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'presented_act_set'", 'to': "orm['people.InstitutionCharge']", 'through': "orm['acts.ActSupport']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'recipient_set': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'received_act_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['people.InstitutionCharge']"}),
            'status_is_final': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
        },
        'acts.actdescriptor': {
            'Meta': {'object_name': 'ActDescriptor', 'db_table': "u'acts_act_descriptor'"},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"})
        },
        'acts.acthasspeech': {
            'Meta': {'object_name': 'ActHasSpeech'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relation_type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'speech': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Speech']"})
        },
        'acts.actsection': {
            'Meta': {'object_name': 'ActSection', 'db_table': "u'acts_act_section'"},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']", 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.ActSection']", 'on_delete': 'models.PROTECT'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
        },
        'acts.actsupport': {
            'Meta': {'object_name': 'ActSupport', 'db_table': "u'acts_act_support'"},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']"}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.InstitutionCharge']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'support_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'support_type': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'acts.agenda': {
            'Meta': {'object_name': 'Agenda', '_ormbases': ['acts.Act']},
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'acts.amendment': {
            'Meta': {'object_name': 'Amendment', '_ormbases': ['acts.Act']},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'amendment_set'", 'on_delete': 'models.PROTECT', 'to': "orm['acts.Act']"}),
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'act_section': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'amendment_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['acts.ActSection']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'acts.attach': {
            'Meta': {'object_name': 'Attach'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachment_set'", 'to': "orm['acts.Act']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'document_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'document_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'document_type': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'blank': 'True'}),
            'file_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'acts.calendar': {
            'Meta': {'object_name': 'Calendar'},
            'act_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['acts.Act']", 'symmetrical': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Institution']"})
        },
        'acts.cgdeliberation': {
            'Meta': {'object_name': 'CGDeliberation', '_ormbases': ['acts.Act']},
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'approval_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'approved_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'execution_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'final_idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'initiative': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'acts.deliberation': {
            'Meta': {'object_name': 'Deliberation', '_ormbases': ['acts.Act']},
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'approval_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'approved_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'execution_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'final_idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'initiative': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'acts.interpellation': {
            'Meta': {'object_name': 'Interpellation', '_ormbases': ['acts.Act']},
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'answer_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'answer_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'question_motivation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'acts.interrogation': {
            'Meta': {'object_name': 'Interrogation', '_ormbases': ['acts.Act']},
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'answer_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'answer_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'question_motivation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reply_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'acts.motion': {
            'Meta': {'object_name': 'Motion', '_ormbases': ['acts.Act']},
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'acts.speech': {
            'Meta': {'object_name': 'Speech'},
            'audio_file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'blank': 'True'}),
            'audio_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']", 'null': 'True', 'blank': 'True'}),
            'author_name_when_external': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'document_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'document_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'document_type': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'blank': 'True'}),
            'file_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'related_act_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['acts.Act']", 'through': "orm['acts.ActHasSpeech']", 'symmetrical': 'False'}),
            'seq_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sitting_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.SittingItem']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'votation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['votations.Votation']", 'null': 'True', 'blank': 'True'})
        },
        'acts.transition': {
            'Meta': {'object_name': 'Transition'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transition_set'", 'to': "orm['acts.Act']"}),
            'final_status': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'transition_date': ('django.db.models.fields.DateField', [], {'default': 'None'}),
            'votation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['votations.Votation']", 'null': 'True', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'locations.location': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'blank': 'True'})
        },
        'locations.taggedactbylocation': {
            'Meta': {'object_name': 'TaggedActByLocation'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tagged_act_set'", 'to': "orm['locations.Location']"}),
            'tagger': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'tagging_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'})
        },
        'monitoring.monitoring': {
            'Meta': {'object_name': 'Monitoring'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_monitoring'", 'to': "orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'object_pk': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_set'", 'to': "orm['auth.User']"})
        },
        'newscache.news': {
            'Meta': {'object_name': 'News'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'generating_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'generating_content_type_set_for_news'", 'to': "orm['contenttypes.ContentType']"}),
            'generating_object_pk': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'news_type': ('django.db.models.fields.CharField', [], {'default': "'INST'", 'max_length': '4'}),
            'priority': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '3'}),
            'related_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_content_type_set_for_news'", 'to': "orm['contenttypes.ContentType']"}),
            'related_object_pk': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '512'})
        },
        'people.group': {
            'Meta': {'ordering': "('name', 'acronym')", 'object_name': 'Group'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'charge_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.InstitutionCharge']", 'through': "orm['people.GroupCharge']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'people.groupcharge': {
            'Meta': {'object_name': 'GroupCharge', 'db_table': "u'people_group_charge'"},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.InstitutionCharge']"}),
            'charge_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'people.institution': {
            'Meta': {'ordering': "('position',)", 'object_name': 'Institution'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution_type': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sub_body_set'", 'null': 'True', 'to': "orm['people.Institution']"}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'people.institutioncharge': {
            'Meta': {'ordering': "['person__first_name', 'person__last_name']", 'object_name': 'InstitutionCharge', 'db_table': "u'people_institution_charge'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'charge_set'", 'on_delete': 'models.PROTECT', 'to': "orm['people.Institution']"}),
            'n_absent_votations': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_present_votations': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_rebel_votations': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'op_charge_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'original_charge': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'committee_charge_set'", 'null': 'True', 'to': "orm['people.InstitutionCharge']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'substituted_by': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'reverse_substituted_by_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['people.InstitutionCharge']", 'blank': 'True', 'unique': 'True'}),
            'substitutes': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'reverse_substitute_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['people.InstitutionCharge']", 'blank': 'True', 'unique': 'True'})
        },
        'people.person': {
            'Meta': {'object_name': 'Person'},
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'birth_location': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'op_politician_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'people.sitting': {
            'Meta': {'object_name': 'Sitting'},
            'call': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Institution']", 'on_delete': 'models.PROTECT'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'people.sittingitem': {
            'Meta': {'object_name': 'SittingItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'related_act_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['acts.Act']", 'null': 'True', 'blank': 'True'}),
            'seq_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sitting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Sitting']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'taxonomy.category': {
            'Meta': {'object_name': 'Category'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'blank': 'True'}),
            'tag_set': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'category_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['taxonomy.Tag']"})
        },
        'taxonomy.tag': {
            'Meta': {'object_name': 'Tag'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'votations.chargevote': {
            'Meta': {'object_name': 'ChargeVote', 'db_table': "u'votations_charge_vote'"},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.InstitutionCharge']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_rebel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'votation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['votations.Votation']"}),
            'vote': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'votations.groupvote': {
            'Meta': {'object_name': 'GroupVote', 'db_table': "u'votations_group_vote'"},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'n_absents': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_abst': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_no': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_presents': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_rebels': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_yes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'votation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['votations.Votation']"}),
            'vote': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'votations.votation': {
            'Meta': {'object_name': 'Votation'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']", 'null': 'True'}),
            'act_descr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'charge_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.InstitutionCharge']", 'through': "orm['votations.ChargeVote']", 'symmetrical': 'False'}),
            'group_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Group']", 'through': "orm['votations.GroupVote']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'is_key': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'n_absents': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_abst': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_legal': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_maj': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_no': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_partecipants': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_presents': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_rebels': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_yes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'outcome': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sitting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Sitting']", 'null': 'True'})
        }
    }

    complete_apps = ['acts']