# -*- coding: utf-8 -*-
import re

from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.template.defaultfilters import slugify

class Migration(DataMigration):

    VOTATION_SLUG_MAX_LEN=500

    def forwards(self, orm):
        for v in orm.Votation.objects.filter(models.Q(slug="") | models.Q(slug__isnull=True)):
            self.set_votation_default_slug(v) 

    def backwards(self, orm):
        # reset slugs

        for v in orm.Votation.objects.exclude(slug="").exclude(slug__isnull=True):
            v.slug = None
            v.save()


    def set_votation_default_slug(self, votation):
        """
        This method will be used for assigning a default slug to a
        Votation that does not have one.
        """

        if votation.sitting and votation.idnum:
            cleaned_idnum = re.sub(r'[^\w\d]+', '-', votation.idnum)
            # slug max len is 100
            votation.slug = slugify("%s-%s" % (votation.sitting.date.isoformat(), 
                                        cleaned_idnum))[:self.VOTATION_SLUG_MAX_LEN]
            votation.save()

        else:
            msg = "In order to compute the default slug, the Votation should be linked to a Sitting and have an idnum"
#            print msg
            raise RuntimeError(msg)
 

    models = {
        'acts.act': {
            'Meta': {'unique_together': "(('slug',), ('presentation_date', 'idnum', 'title'))", 'object_name': 'Act'},
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
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
            'n_absent_attendances': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_absent_votations': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_present_attendances': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'Meta': {'unique_together': "(('slug',), ('sitting', 'idnum'))", 'object_name': 'Votation'},
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
            'sitting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Sitting']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['votations']
    symmetrical = True
