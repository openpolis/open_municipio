# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Decision.commitment_set'
        db.add_column(u'acts_decision', 'commitment_set',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acts.Commitment'], null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field commitment_set on 'Decision'
        db.delete_table(db.shorten_name(u'acts_decision_commitment_set'))


    def backwards(self, orm):
        # Deleting field 'Decision.commitment_set'
        db.delete_column(u'acts_decision', 'commitment_set_id')

        # Adding M2M table for field commitment_set on 'Decision'
        m2m_table_name = db.shorten_name(u'acts_decision_commitment_set')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('decision', models.ForeignKey(orm[u'acts.decision'], null=False)),
            ('commitment', models.ForeignKey(orm[u'acts.commitment'], null=False))
        ))
        db.create_unique(m2m_table_name, ['decision_id', 'commitment_id'])


    models = {
        u'acts.act': {
            'Meta': {'unique_together': "(('slug',), ('presentation_date', 'idnum', 'title'))", 'object_name': 'Act'},
            'adj_title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'category_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['taxonomy.Category']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'emitting_institution': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'emitted_act_set'", 'null': 'True', 'blank': 'True', 'to': u"orm['people.Institution']"}),
            'emitting_office': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'emitted_act_set'", 'null': 'True', 'to': u"orm['people.Office']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'is_key': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['locations.Location']", 'null': 'True', 'through': u"orm['locations.TaggedActByLocation']", 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'presentation_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'presenter_administrator_set': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'presented_act_set'", 'to': u"orm['people.AdministrationCharge']", 'through': u"orm['acts.ActAdministratorSignature']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'presenter_set': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'presented_act_set'", 'to': u"orm['people.InstitutionCharge']", 'through': u"orm['acts.ActSupport']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'recipient_administrator_set': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'received_act_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['people.AdministrationCharge']"}),
            'recipient_set': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'received_act_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['people.InstitutionCharge']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'status_is_final': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
        },
        u'acts.actadministratorsignature': {
            'Meta': {'object_name': 'ActAdministratorSignature'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.Act']"}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.AdministrationCharge']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signature_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        u'acts.actdescriptor': {
            'Meta': {'object_name': 'ActDescriptor', 'db_table': "u'acts_act_descriptor'"},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.Act']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Person']"})
        },
        u'acts.acthasspeech': {
            'Meta': {'object_name': 'ActHasSpeech'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.Act']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relation_type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'speech': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.Speech']"})
        },
        u'acts.actsection': {
            'Meta': {'object_name': 'ActSection', 'db_table': "u'acts_act_section'"},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.Act']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.ActSection']", 'on_delete': 'models.PROTECT'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
        },
        u'acts.actsupport': {
            'Meta': {'object_name': 'ActSupport', 'db_table': "u'acts_act_support'"},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.Act']"}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.InstitutionCharge']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'support_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'support_type': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'acts.agenda': {
            'Meta': {'object_name': 'Agenda', '_ormbases': [u'acts.Act']},
            u'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'acts.amendment': {
            'Meta': {'object_name': 'Amendment', '_ormbases': [u'acts.Act']},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'amendment_set'", 'on_delete': 'models.PROTECT', 'to': u"orm['acts.Act']"}),
            u'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'act_section': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'amendment_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['acts.ActSection']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'acts.attach': {
            'Meta': {'object_name': 'Attach'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachment_set'", 'to': u"orm['acts.Act']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'document_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'document_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'document_type': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'blank': 'True'}),
            'file_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'acts.calendar': {
            'Meta': {'object_name': 'Calendar'},
            'act_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['acts.Act']", 'symmetrical': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Institution']"})
        },
        u'acts.cgdeliberation': {
            'Meta': {'object_name': 'CGDeliberation', '_ormbases': [u'acts.Act']},
            u'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'approval_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'approved_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'execution_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'final_idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'initiative': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'acts.commitment': {
            'Meta': {'object_name': 'Commitment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.AdministrationCharge']"}),
            'payee_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['people.Company']", 'null': 'True', 'blank': 'True'}),
            'selection_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        u'acts.decision': {
            'Meta': {'object_name': 'Decision', '_ormbases': [u'acts.Act']},
            u'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'commitment_set': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.Commitment']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PRESENTED'", 'max_length': '12'}),
            'total_commitment': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'})
        },
        u'acts.decree': {
            'Meta': {'object_name': 'Decree', '_ormbases': [u'acts.Act']},
            u'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'commitment_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['acts.Commitment']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PRESENTED'", 'max_length': '12'}),
            'total_commitment': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'})
        },
        u'acts.deliberation': {
            'Meta': {'object_name': 'Deliberation', '_ormbases': [u'acts.Act']},
            u'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'approval_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'approved_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'execution_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'final_idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'initiative': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'acts.interpellation': {
            'Meta': {'object_name': 'Interpellation', '_ormbases': [u'acts.Act']},
            u'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'answer_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'answer_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'question_motivation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'acts.interrogation': {
            'Meta': {'object_name': 'Interrogation', '_ormbases': [u'acts.Act']},
            u'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'answer_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'answer_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'question_motivation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reply_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'acts.motion': {
            'Meta': {'object_name': 'Motion', '_ormbases': [u'acts.Act']},
            u'act_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acts.Act']", 'unique': 'True', 'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'acts.speech': {
            'Meta': {'unique_together': "(('slug',), ('author', 'author_name_when_external', 'sitting_item', 'seq_order'))", 'object_name': 'Speech'},
            'audio_file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'blank': 'True'}),
            'audio_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Person']", 'null': 'True', 'blank': 'True'}),
            'author_name_when_external': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'document_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'document_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'document_type': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'blank': 'True'}),
            'file_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'related_act_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['acts.Act']", 'through': u"orm['acts.ActHasSpeech']", 'symmetrical': 'False'}),
            'seq_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sitting_item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.SittingItem']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'votation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['votations.Votation']", 'null': 'True', 'blank': 'True'})
        },
        u'acts.transition': {
            'Meta': {'object_name': 'Transition'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transition_set'", 'to': u"orm['acts.Act']"}),
            'attendance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendances.Attendance']", 'null': 'True', 'blank': 'True'}),
            'final_status': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'transition_date': ('django.db.models.fields.DateField', [], {'default': 'None'}),
            'votation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['votations.Votation']", 'null': 'True', 'blank': 'True'})
        },
        u'attendances.attendance': {
            'Meta': {'object_name': 'Attendance'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.Act']", 'null': 'True'}),
            'act_descr': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'charge_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['people.InstitutionCharge']", 'through': u"orm['attendances.ChargeAttendance']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'is_key': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'n_absents': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_legal': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_presents': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sitting': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Sitting']", 'null': 'True'})
        },
        u'attendances.chargeattendance': {
            'Meta': {'object_name': 'ChargeAttendance'},
            'attendance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendances.Attendance']"}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.InstitutionCharge']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locations.location': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'blank': 'True'})
        },
        u'locations.taggedactbylocation': {
            'Meta': {'object_name': 'TaggedActByLocation'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.Act']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tagged_act_set'", 'to': u"orm['locations.Location']"}),
            'tagger': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'tagging_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'monitoring.monitoring': {
            'Meta': {'object_name': 'Monitoring'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_monitoring'", 'to': u"orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'object_pk': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_set'", 'to': u"orm['auth.User']"})
        },
        u'newscache.news': {
            'Meta': {'object_name': 'News'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'generating_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'generating_content_type_set_for_news'", 'to': u"orm['contenttypes.ContentType']"}),
            'generating_object_pk': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'news_type': ('django.db.models.fields.CharField', [], {'default': "'INST'", 'max_length': '4'}),
            'priority': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '3'}),
            'related_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_content_type_set_for_news'", 'to': u"orm['contenttypes.ContentType']"}),
            'related_object_pk': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '512'})
        },
        u'people.administrationcharge': {
            'Meta': {'object_name': 'AdministrationCharge', 'db_table': "u'people_administration_charge'"},
            'charge_type': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'office': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'charge_set'", 'on_delete': 'models.PROTECT', 'to': u"orm['people.Office']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Person']"}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'people.company': {
            'Meta': {'object_name': 'Company'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'people.group': {
            'Meta': {'ordering': "('name', 'acronym')", 'object_name': 'Group'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'charge_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['people.InstitutionCharge']", 'through': u"orm['people.GroupCharge']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'people.groupcharge': {
            'Meta': {'object_name': 'GroupCharge', 'db_table': "u'people_group_charge'"},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.InstitutionCharge']"}),
            'charge_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'people.institution': {
            'Meta': {'ordering': "('position',)", 'object_name': 'Institution'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution_type': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sub_body_set'", 'null': 'True', 'to': u"orm['people.Institution']"}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'people.institutioncharge': {
            'Meta': {'ordering': "['person__first_name', 'person__last_name']", 'object_name': 'InstitutionCharge', 'db_table': "u'people_institution_charge'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'charge_set'", 'on_delete': 'models.PROTECT', 'to': u"orm['people.Institution']"}),
            'n_absent_attendances': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_absent_votations': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_present_attendances': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_present_votations': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_rebel_votations': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'op_charge_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'original_charge': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'committee_charge_set'", 'null': 'True', 'to': u"orm['people.InstitutionCharge']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Person']"}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'substituted_by': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'reverse_substituted_by_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['people.InstitutionCharge']", 'blank': 'True', 'unique': 'True'}),
            'substitutes': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'reverse_substitute_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['people.InstitutionCharge']", 'blank': 'True', 'unique': 'True'})
        },
        u'people.office': {
            'Meta': {'object_name': 'Office'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['people.Office']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'people.person': {
            'Meta': {'object_name': 'Person'},
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'birth_location': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'op_politician_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'people.sitting': {
            'Meta': {'object_name': 'Sitting'},
            'call': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Institution']", 'on_delete': 'models.PROTECT'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'people.sittingitem': {
            'Meta': {'object_name': 'SittingItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'related_act_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['acts.Act']", 'null': 'True', 'blank': 'True'}),
            'seq_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sitting': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Sitting']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'taxonomy.category': {
            'Meta': {'object_name': 'Category'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'blank': 'True'}),
            'tag_set': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'category_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['taxonomy.Tag']"})
        },
        u'taxonomy.tag': {
            'Meta': {'object_name': 'Tag'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'votations.chargevote': {
            'Meta': {'object_name': 'ChargeVote', 'db_table': "u'votations_charge_vote'"},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.InstitutionCharge']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_rebel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'votation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['votations.Votation']"}),
            'vote': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'votations.groupvote': {
            'Meta': {'object_name': 'GroupVote', 'db_table': "u'votations_group_vote'"},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'n_absents': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_abst': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_no': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_presents': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_rebels': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_yes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'votation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['votations.Votation']"}),
            'vote': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'votations.votation': {
            'Meta': {'unique_together': "(('slug',), ('sitting', 'idnum'))", 'object_name': 'Votation'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acts.Act']", 'null': 'True'}),
            'act_descr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'charge_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['people.InstitutionCharge']", 'through': u"orm['votations.ChargeVote']", 'symmetrical': 'False'}),
            'group_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['people.Group']", 'through': u"orm['votations.GroupVote']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'sitting': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Sitting']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['acts']