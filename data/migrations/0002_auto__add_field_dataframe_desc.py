# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DataFrame.desc'
        db.add_column('data_dataframe', 'desc',
                      self.gf('django.db.models.fields.TextField')(default='blank value'),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DataFrame.desc'
        db.delete_column('data_dataframe', 'desc')


    models = {
        'data.dataframe': {
            'Meta': {'object_name': 'DataFrame'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'db_table_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'desc': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['data']