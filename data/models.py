from django.db import models
from django.template.defaultfilters import slugify	
from django.contrib.auth.models import User

# For deleting the file on delete
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

# For importing from file to database
from win import settings
import os

# For deleting from database when dataframe is deleted
import MySQLdb

# For query from database
from MySQLdb.constants import FIELD_TYPE
import MySQLdb.cursors

############################## Data File ##############################

class DataFile(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	name = models.CharField(max_length=255, blank=True, default='')
	description = models.TextField(blank=True, default='')
	slug = models.SlugField(max_length=255, blank=True, default='')
	owner = models.ForeignKey(User, related_name="data_files", default=1)
	file = models.FileField(upload_to='datafiles/')

	def __unicode__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.name:
			self.name = self.file.name
		if not self.slug:
			self.slug = slugify(self.name)
		super(DataFile, self).save(*args, **kwargs)

	def delete(self):
		# Note: this wont work on queryset deletes
		self.file.delete()
		super(DataFile, self).delete()

	@models.permalink
	def get_absolute_url(self):
		return ("data:filedetail", (), {"slug": self.slug, "pk": self.id})

	@models.permalink
	def get_absolute_delete_url(self):
		return ("data:filedelete", (), {"slug": self.slug, "pk": self.id})

	@models.permalink
	def get_absolute_import_url(self):
		return ("data:fileimport", (), {"slug": self.slug, "pk": self.id})

############################## Data Frame ##############################


class DataFrame(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255, blank=True, default='')
	owner = models.ForeignKey(User, related_name="data_frame", default=1)
	db_table_name = models.CharField(max_length=255)
	
	db_host = settings.DATABASES['default']['HOST']
	db_user = settings.DATABASES['default']['USER']
	db_password = settings.DATABASES['default']['PASSWORD']
	db_name = settings.DATABASES['default']['NAME']

	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		"Save the model, specifying default values where needed"
		if not self.name:
			self.name = self.file.name
		if not self.slug:
			self.slug = slugify(self.name)
		super(DataFrame, self).save(*args, **kwargs)

	def delete(self):
		"Delete the dataframe and drop the underlying table"
		db = self.get_db()
		cursor = db.cursor()

		try:
			cursor.execute("DROP TABLE IF EXISTS %s" % (self.db_table_name,))
		except MySQLdb.Warning:
			pass
		cursor.close()	
		db.close()
		super(DataFrame, self).delete()

	def get_db(self, cursorclass = MySQLdb.cursors.Cursor):
		"Get connection to the database"
		db = MySQLdb.connect(cursorclass=cursorclass, host=self.db_host, user=self.db_user, passwd=self.db_password)
		db.select_db(self.db_name)
		return db

	def import_from_file(self, datafile):
		db_table = '_dataframe' + '_U' + str(datafile.owner) + '_DF' + str(self.id)	

		import_string = "python data/includes/csv2mysql.py --table=%s --database=%s --user=%s --password=%s --host=%s %s" % (db_table, self.db_name, self.db_user, self.db_password, self.db_host, datafile.file.path)
		import_status = {'command': '', 'output': ''}	
		import_status['command'] = import_string
		import_status['output'] = os.popen(import_string).read()
		
		self.db_table_name = db_table
		super(DataFrame, self).save()
		return import_status

	def get_data(self, nrows = 10):
		db = self.get_db()
		cursor = db.cursor()
		cursor.execute("SELECT * FROM %s LIMIT %s" % (self.db_table_name, nrows))
		query_results = cursor.fetchall()
		column_names = tuple([i[0] for i in cursor.description])
		cursor.close
		db.close()
		return query_results, column_names

	def query_results(self, query):
		db = self.get_db(cursorclass= MySQLdb.cursors.DictCursor)
		cursor = db.cursor()
		cursor.execute(query)
		query_results = cursor.fetchall()
		# There seems to be a problem with column_names
		column_names = tuple([i[0] for i in cursor.description])
		cursor.close
		db.close()
		return query_results, column_names

	@property
	def columns(self):
		db = self.get_db(MySQLdb.cursors.DictCursor)
		cursor = db.cursor()

		cursor.execute("EXPLAIN %s" % (self.db_table_name))
		columns = cursor.fetchall()
		cursor.close
		db.close()
		
		# Creating dict with field names as keys
		# Should make these lower case at some point
		newDict = {}
		for col in columns:
			# Assign key and title case
			key = col["Field"].title()
			
			# Split varchar(255) as varchar and 255
			if '(' in col["Type"]:
				col["length"] = col["Type"].split('(')[1].split(')')[0]
				col["Type"] = col["Type"].split('(')[0]
			
			# Numeric / Measure
			if col["Type"] in ("int", "double"):
				col["type_category"] = "numeric"
				col["role"] = "measure"

			# Character / Dimension
			if col["Type"] in ("varchar"):
				col["type_category"] = "character"
				col["role"] = "dimension"

			# Time / Dimension
			if col["Type"] in ("date", "datetime", "time"):
				col["type_category"] = "time"
				col["role"] = "dimension"

			# Get rid of useless info from database
			del col["Key"]
			del col["Extra"]
			del col["Default"]
			del col["Field"]
			
			# Switch key to lowercase (type from Type)
			col["type"] = col.pop("Type")

			newDict[key] = col

		return newDict


	@models.permalink
	def get_absolute_url(self):
		return ("data:framedetail", (), {"slug": self.slug, "pk": self.id})

	@models.permalink
	def get_absolute_delete_url(self):
		return ("data:framedelete", (), {"slug": self.slug, "pk": self.id})

	@models.permalink
	def get_absolute_report_url(self):
		return ("data:framereport", (), {"slug": self.slug, "pk": self.id})

