# encoding: utf-8
import datetime
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
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('adj_title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('presentation_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('emitting_institution', self.gf('django.db.models.fields.related.ForeignKey')(related_name='emitted_act_set', to=orm['people.Institution'])),
        ))
        db.send_create_signal('acts', ['Act'])

        # Adding M2M table for field recipients on 'Act'
        db.create_table('acts_act_recipient', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('act', models.ForeignKey(orm['acts.act'], null=False)),
            ('institutioncharge', models.ForeignKey(orm['people.institutioncharge'], null=False))
        ))
        db.create_unique('acts_act_recipient', ['act_id', 'institutioncharge_id'])

        # Adding M2M table for field category_set on 'Act'
        db.create_table('acts_act_category_set', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('act', models.ForeignKey(orm['acts.act'], null=False)),
            ('category', models.ForeignKey(orm['taxonomy.category'], null=False))
        ))
        db.create_unique('acts_act_category_set', ['act_id', 'category_id'])

        # Adding model 'ActSection'
        db.create_table(u'acts_act_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Act'])),
            ('parent_section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.ActSection'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acts', ['ActSection'])

        # Adding model 'ActSupport'
        db.create_table(u'acts_act_support', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.InstitutionCharge'])),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Act'])),
            ('support_type', self.gf('django.db.models.fields.IntegerField')()),
            ('support_date', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('acts', ['ActSupport'])

        # Adding model 'Deliberation'
        db.create_table('acts_deliberation', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('approval_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('publication_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('execution_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('initiative', self.gf('django.db.models.fields.IntegerField')()),
            ('approved_text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acts', ['Deliberation'])

        # Adding model 'Interrogation'
        db.create_table('acts_interrogation', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('answer_type', self.gf('django.db.models.fields.IntegerField')()),
            ('question_motivation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('answer_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('reply_text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acts', ['Interrogation'])

        # Adding model 'Interpellation'
        db.create_table('acts_interpellation', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('answer_type', self.gf('django.db.models.fields.IntegerField')()),
            ('question_motivation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('answer_text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acts', ['Interpellation'])

        # Adding model 'Motion'
        db.create_table('acts_motion', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('acts', ['Motion'])

        # Adding model 'Emendation'
        db.create_table('acts_emendation', (
            ('act_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acts.Act'], unique=True, primary_key=True)),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(related_name='related_emendation_set', to=orm['acts.Act'])),
            ('act_section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.ActSection'], null=True, blank=True)),
        ))
        db.send_create_signal('acts', ['Emendation'])

        # Adding model 'Status'
        db.create_table('acts_status', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('acts', ['Status'])

        # Adding model 'Transition'
        db.create_table(u'acts_transition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('final_status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Status'])),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Act'])),
            ('sitting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Sitting'], null=True, blank=True)),
            ('transition_date', self.gf('django.db.models.fields.DateField')(default=None)),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=128, null=True)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal('acts', ['Transition'])

        # Adding model 'Attach'
        db.create_table('acts_attach', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('document_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('text_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('pdf_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('pdf_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Act'])),
        ))
        db.send_create_signal('acts', ['Attach'])

        # Adding model 'Minute'
        db.create_table('acts_minute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('document_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('text_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('pdf_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('pdf_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('sitting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Sitting'])),
        ))
        db.send_create_signal('acts', ['Minute'])

        # Adding M2M table for field act_set on 'Minute'
        db.create_table('acts_minute_act_set', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('minute', models.ForeignKey(orm['acts.minute'], null=False)),
            ('act', models.ForeignKey(orm['acts.act'], null=False))
        ))
        db.create_unique('acts_minute_act_set', ['minute_id', 'act_id'])

        # Adding model 'Outcome'
        db.create_table('acts_outcome', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sitting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Sitting'])),
        ))
        db.send_create_signal('acts', ['Outcome'])

        # Adding M2M table for field act_set on 'Outcome'
        db.create_table('acts_outcome_act_set', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('outcome', models.ForeignKey(orm['acts.outcome'], null=False)),
            ('act', models.ForeignKey(orm['acts.act'], null=False))
        ))
        db.create_unique('acts_outcome_act_set', ['outcome_id', 'act_id'])

        # Adding model 'Calendar'
        db.create_table('acts_calendar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('acts', ['Calendar'])

        # Adding M2M table for field act_set on 'Calendar'
        db.create_table('acts_calendar_act_set', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('calendar', models.ForeignKey(orm['acts.calendar'], null=False)),
            ('act', models.ForeignKey(orm['acts.act'], null=False))
        ))
        db.create_unique('acts_calendar_act_set', ['calendar_id', 'act_id'])


    def backwards(self, orm):
        
        # Deleting model 'Act'
        db.delete_table('acts_act')

        # Removing M2M table for field recipients on 'Act'
        db.delete_table('acts_act_recipient')

        # Removing M2M table for field category_set on 'Act'
        db.delete_table('acts_act_category_set')

        # Deleting model 'ActSection'
        db.delete_table(u'acts_act_section')

        # Deleting model 'ActSupport'
        db.delete_table(u'acts_act_support')

        # Deleting model 'Deliberation'
        db.delete_table('acts_deliberation')

        # Deleting model 'Interrogation'
        db.delete_table('acts_interrogation')

        # Deleting model 'Interpellation'
        db.delete_table('acts_interpellation')

        # Deleting model 'Motion'
        db.delete_table('acts_motion')

        # Deleting model 'Emendation'
        db.delete_table('acts_emendation')

        # Deleting model 'Status'
        db.delete_table('acts_status')

        # Deleting model 'Transition'
        db.delete_table(u'acts_transition')

        # Deleting model 'Attach'
        db.delete_table('acts_attach')

        # Deleting model 'Minute'
        db.delete_table('acts_minute')

        # Removing M2M table for field act_set on 'Minute'
        db.delete_table('acts_minute_act_set')

        # Deleting model 'Outcome'
        db.delete_table('acts_outcome')

        # Removing M2M table for field act_set on 'Outcome'
        db.delete_table('acts_outcome_act_set')

        # Deleting model 'Calendar'
        db.delete_table('acts_calendar')

        # Removing M2M table for field act_set on 'Calendar'
        db.delete_table('acts_calendar_act_set')


    models = {
        'acts.act': {
            'Meta': {'object_name': 'Act'},
            'adj_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'category_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['taxonomy.Category']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'emitting_institution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'emitted_act_set'", 'to': "orm['people.Institution']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'presentation_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'presenters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'presenter_act_set'", 'to': "orm['people.InstitutionCharge']", 'through': "orm['acts.ActSupport']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'recipient_act_set'", 'to': "orm['people.InstitutionCharge']", 'db_table': "'acts_act_recipient'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'transitions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['acts.Status']", 'null': 'True', 'through': "orm['acts.Transition']", 'blank': 'True'})
        },
        'acts.actsection': {
            'Meta': {'object_name': 'ActSection', 'db_table': "u'acts_act_section'"},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.ActSection']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'acts.actsupport': {
            'Meta': {'object_name': 'ActSupport', 'db_table': "u'acts_act_support'"},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']"}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.InstitutionCharge']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'support_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'support_type': ('django.db.models.fields.IntegerField', [], {})
        },
        'acts.attach': {
            'Meta': {'object_name': 'Attach'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'document_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'pdf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'pdf_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'acts.calendar': {
            'Meta': {'object_name': 'Calendar'},
            'act_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['acts.Act']", 'symmetrical': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'acts.deliberation': {
            'Meta': {'object_name': 'Deliberation', '_ormbases': ['acts.Act']},
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'approval_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'approved_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'execution_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'initiative': ('django.db.models.fields.IntegerField', [], {}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'acts.emendation': {
            'Meta': {'object_name': 'Emendation', '_ormbases': ['acts.Act']},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_emendation_set'", 'to': "orm['acts.Act']"}),
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'act_section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.ActSection']", 'null': 'True', 'blank': 'True'})
        },
        'acts.interpellation': {
            'Meta': {'object_name': 'Interpellation', '_ormbases': ['acts.Act']},
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'answer_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'answer_type': ('django.db.models.fields.IntegerField', [], {}),
            'question_motivation': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'acts.interrogation': {
            'Meta': {'object_name': 'Interrogation', '_ormbases': ['acts.Act']},
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'answer_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'answer_type': ('django.db.models.fields.IntegerField', [], {}),
            'question_motivation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reply_text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'acts.minute': {
            'Meta': {'object_name': 'Minute'},
            'act_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['acts.Act']", 'symmetrical': 'False'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'document_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'pdf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'pdf_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'sitting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Sitting']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'acts.motion': {
            'Meta': {'object_name': 'Motion', '_ormbases': ['acts.Act']},
            'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'})
        },
        'acts.outcome': {
            'Meta': {'object_name': 'Outcome'},
            'act_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['acts.Act']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sitting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Sitting']"})
        },
        'acts.status': {
            'Meta': {'object_name': 'Status'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'acts.transition': {
            'Meta': {'object_name': 'Transition'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']"}),
            'final_status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Status']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'sitting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Sitting']", 'null': 'True', 'blank': 'True'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'transition_date': ('django.db.models.fields.DateField', [], {'default': 'None'})
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
        'people.institution': {
            'Meta': {'object_name': 'Institution'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution_type': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sub_body_set'", 'null': 'True', 'to': "orm['people.Institution']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'people.institutioncharge': {
            'Meta': {'object_name': 'InstitutionCharge', 'db_table': "u'people_institution_charge'"},
            'charge_type': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Institution']"}),
            'op_charge_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'substituted_by': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'reverse_substituted_by_set'", 'unique': 'True', 'null': 'True', 'to': "orm['people.InstitutionCharge']"}),
            'substitutes': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'reverse_substitute_set'", 'unique': 'True', 'null': 'True', 'to': "orm['people.InstitutionCharge']"})
        },
        'people.person': {
            'Meta': {'object_name': 'Person'},
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'birth_location': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'op_politician_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'people.sitting': {
            'Meta': {'object_name': 'Sitting'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Institution']"}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'taxonomy.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '100', 'blank': 'True'}),
            'tag_set': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'category_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['taggit.Tag']"})
        },
        'taxonomy.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taxonomy_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taxonomy_taggeditem_items'", 'to': "orm['taggit.Tag']"}),
            'tagger': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'tagging_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['acts']
