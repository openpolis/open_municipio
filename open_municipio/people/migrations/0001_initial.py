# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Person'
        db.create_table('people_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('birth_date', self.gf('django.db.models.fields.DateField')()),
            ('birth_location', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=128, unique=True, null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.IntegerField')()),
            ('op_politician_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('img', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('people', ['Person'])

        # Adding model 'PersonResource'
        db.create_table('people_personresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resource_set', to=orm['people.Person'])),
        ))
        db.send_create_signal('people', ['PersonResource'])

        # Adding model 'InstitutionResource'
        db.create_table('people_institutionresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resource_set', to=orm['people.Institution'])),
        ))
        db.send_create_signal('people', ['InstitutionResource'])

        # Adding model 'GroupResource'
        db.create_table('people_groupresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resource_set', to=orm['people.Group'])),
        ))
        db.send_create_signal('people', ['GroupResource'])

        # Adding model 'InstitutionCharge'
        db.create_table(u'people_institution_charge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_reason', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('substitutes', self.gf('django.db.models.fields.related.OneToOneField')(related_name='reverse_substitute_set', null=True, on_delete=models.PROTECT, to=orm['people.InstitutionCharge'], blank=True, unique=True)),
            ('substituted_by', self.gf('django.db.models.fields.related.OneToOneField')(related_name='reverse_substituted_by_set', null=True, on_delete=models.PROTECT, to=orm['people.InstitutionCharge'], blank=True, unique=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(related_name='charge_set', on_delete=models.PROTECT, to=orm['people.Institution'])),
            ('op_charge_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('original_charge', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='committee_charge_set', null=True, to=orm['people.InstitutionCharge'])),
            ('n_rebel_votations', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_present_votations', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_absent_votations', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('people', ['InstitutionCharge'])

        # Adding model 'InstitutionResponsability'
        db.create_table('people_institutionresponsability', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.InstitutionCharge'])),
            ('charge_type', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('people', ['InstitutionResponsability'])

        # Adding model 'CompanyCharge'
        db.create_table(u'people_organization_charge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_reason', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(related_name='charge_set', on_delete=models.PROTECT, to=orm['people.Company'])),
            ('charge_type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('people', ['CompanyCharge'])

        # Adding model 'AdministrationCharge'
        db.create_table(u'people_administration_charge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_reason', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('office', self.gf('django.db.models.fields.related.ForeignKey')(related_name='charge_set', on_delete=models.PROTECT, to=orm['people.Office'])),
            ('charge_type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('people', ['AdministrationCharge'])

        # Adding model 'Group'
        db.create_table('people_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('acronym', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True, null=True, blank=True)),
            ('img', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('people', ['Group'])

        # Adding model 'GroupCharge'
        db.create_table(u'people_group_charge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Group'])),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.InstitutionCharge'])),
            ('charge_description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_reason', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('people', ['GroupCharge'])

        # Adding model 'GroupResponsability'
        db.create_table('people_groupresponsability', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('charge_type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.GroupCharge'])),
        ))
        db.send_create_signal('people', ['GroupResponsability'])

        # Adding model 'GroupIsMajority'
        db.create_table('people_groupismajority', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Group'])),
            ('is_majority', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('people', ['GroupIsMajority'])

        # Adding model 'Institution'
        db.create_table('people_institution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sub_body_set', null=True, to=orm['people.Institution'])),
            ('institution_type', self.gf('django.db.models.fields.IntegerField')()),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('people', ['Institution'])

        # Adding model 'Company'
        db.create_table('people_company', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('people', ['Company'])

        # Adding model 'Office'
        db.create_table('people_office', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('people', ['Office'])

        # Adding model 'Sitting'
        db.create_table('people_sitting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('idnum', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('call', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Institution'], on_delete=models.PROTECT)),
        ))
        db.send_create_signal('people', ['Sitting'])

        # Adding model 'SittingItem'
        db.create_table('people_sittingitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sitting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Sitting'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('item_type', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('seq_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('people', ['SittingItem'])

        # Adding M2M table for field related_act_set on 'SittingItem'
        m2m_table_name = db.shorten_name('people_sittingitem_related_act_set')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sittingitem', models.ForeignKey(orm['people.sittingitem'], null=False)),
            ('act', models.ForeignKey(orm['acts.act'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sittingitem_id', 'act_id'])


    def backwards(self, orm):
        # Deleting model 'Person'
        db.delete_table('people_person')

        # Deleting model 'PersonResource'
        db.delete_table('people_personresource')

        # Deleting model 'InstitutionResource'
        db.delete_table('people_institutionresource')

        # Deleting model 'GroupResource'
        db.delete_table('people_groupresource')

        # Deleting model 'InstitutionCharge'
        db.delete_table(u'people_institution_charge')

        # Deleting model 'InstitutionResponsability'
        db.delete_table('people_institutionresponsability')

        # Deleting model 'CompanyCharge'
        db.delete_table(u'people_organization_charge')

        # Deleting model 'AdministrationCharge'
        db.delete_table(u'people_administration_charge')

        # Deleting model 'Group'
        db.delete_table('people_group')

        # Deleting model 'GroupCharge'
        db.delete_table(u'people_group_charge')

        # Deleting model 'GroupResponsability'
        db.delete_table('people_groupresponsability')

        # Deleting model 'GroupIsMajority'
        db.delete_table('people_groupismajority')

        # Deleting model 'Institution'
        db.delete_table('people_institution')

        # Deleting model 'Company'
        db.delete_table('people_company')

        # Deleting model 'Office'
        db.delete_table('people_office')

        # Deleting model 'Sitting'
        db.delete_table('people_sitting')

        # Deleting model 'SittingItem'
        db.delete_table('people_sittingitem')

        # Removing M2M table for field related_act_set on 'SittingItem'
        db.delete_table(db.shorten_name('people_sittingitem_related_act_set'))


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
        'acts.actsupport': {
            'Meta': {'object_name': 'ActSupport', 'db_table': "u'acts_act_support'"},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acts.Act']"}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.InstitutionCharge']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'support_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'support_type': ('django.db.models.fields.CharField', [], {'max_length': '12'})
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
        'people.administrationcharge': {
            'Meta': {'object_name': 'AdministrationCharge', 'db_table': "u'people_administration_charge'"},
            'charge_type': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'office': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'charge_set'", 'on_delete': 'models.PROTECT', 'to': "orm['people.Office']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'people.company': {
            'Meta': {'object_name': 'Company'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'people.companycharge': {
            'Meta': {'object_name': 'CompanyCharge', 'db_table': "u'people_organization_charge'"},
            'charge_type': ('django.db.models.fields.IntegerField', [], {}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'charge_set'", 'on_delete': 'models.PROTECT', 'to': "orm['people.Company']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'start_date': ('django.db.models.fields.DateField', [], {})
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
        'people.groupismajority': {
            'Meta': {'object_name': 'GroupIsMajority'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_majority': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'people.groupresource': {
            'Meta': {'object_name': 'GroupResource'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resource_set'", 'to': "orm['people.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'people.groupresponsability': {
            'Meta': {'object_name': 'GroupResponsability'},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.GroupCharge']"}),
            'charge_type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
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
        'people.institutionresource': {
            'Meta': {'object_name': 'InstitutionResource'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resource_set'", 'to': "orm['people.Institution']"}),
            'resource_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'people.institutionresponsability': {
            'Meta': {'object_name': 'InstitutionResponsability'},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.InstitutionCharge']"}),
            'charge_type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'people.office': {
            'Meta': {'object_name': 'Office'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
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
        'people.personresource': {
            'Meta': {'object_name': 'PersonResource'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resource_set'", 'to': "orm['people.Person']"}),
            'resource_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '64'})
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
        }
    }

    complete_apps = ['people']