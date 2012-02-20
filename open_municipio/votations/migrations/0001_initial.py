# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Votation'
        db.create_table('votations_votation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idnum', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('sitting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Sitting'])),
            ('n_legal', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('n_presents', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('n_yes', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('n_no', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('n_abst', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('n_maj', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('outcome', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('votations', ['Votation'])

        # Adding M2M table for field act_set on 'Votation'
        db.create_table('votations_votation_act_set', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('votation', models.ForeignKey(orm['votations.votation'], null=False)),
            ('act', models.ForeignKey(orm['acts.act'], null=False))
        ))
        db.create_unique('votations_votation_act_set', ['votation_id', 'act_id'])

        # Adding model 'GroupVote'
        db.create_table(u'votations_group_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('votation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['votations.Votation'])),
            ('vote', self.gf('django.db.models.fields.IntegerField')()),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Group'])),
        ))
        db.send_create_signal('votations', ['GroupVote'])

        # Adding model 'ChargeVote'
        db.create_table(u'votations_charge_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('votation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['votations.Votation'])),
            ('vote', self.gf('django.db.models.fields.IntegerField')()),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.InstitutionCharge'])),
            ('rebel', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('votations', ['ChargeVote'])


    def backwards(self, orm):
        
        # Deleting model 'Votation'
        db.delete_table('votations_votation')

        # Removing M2M table for field act_set on 'Votation'
        db.delete_table('votations_votation_act_set')

        # Deleting model 'GroupVote'
        db.delete_table(u'votations_group_vote')

        # Deleting model 'ChargeVote'
        db.delete_table(u'votations_charge_vote')


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
        'acts.actsupport': {
            'Meta': {'object_name': 'ActSupport', 'db_table': "u'acts_act_support'"},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']"}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.InstitutionCharge']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'support_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'support_type': ('django.db.models.fields.IntegerField', [], {})
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
        'people.group': {
            'Meta': {'object_name': 'Group'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'counselor_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.InstitutionCharge']", 'through': "orm['people.GroupCharge']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        },
        'votations.chargevote': {
            'Meta': {'object_name': 'ChargeVote', 'db_table': "u'votations_charge_vote'"},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.InstitutionCharge']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'rebel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'votation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['votations.Votation']"}),
            'vote': ('django.db.models.fields.IntegerField', [], {})
        },
        'votations.groupvote': {
            'Meta': {'object_name': 'GroupVote', 'db_table': "u'votations_group_vote'"},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'votation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['votations.Votation']"}),
            'vote': ('django.db.models.fields.IntegerField', [], {})
        },
        'votations.votation': {
            'Meta': {'object_name': 'Votation'},
            'act_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['acts.Act']", 'symmetrical': 'False'}),
            'charge_vote_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.InstitutionCharge']", 'through': "orm['votations.ChargeVote']", 'symmetrical': 'False'}),
            'group_vote_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Group']", 'through': "orm['votations.GroupVote']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idnum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'n_abst': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'n_legal': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'n_maj': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'n_no': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'n_presents': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'n_yes': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'outcome': ('django.db.models.fields.IntegerField', [], {}),
            'sitting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Sitting']"})
        }
    }

    complete_apps = ['votations']
