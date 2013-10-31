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
	
	def get_db(self):
		db = MySQLdb.connect(host=self.db_host, user=self.db_user, passwd=self.db_password)
		db.select_db(self.db_name)
		return db

	def save(self, *args, **kwargs):
		if not self.name:
			self.name = self.file.name
		if not self.slug:
			self.slug = slugify(self.name)
		super(DataFrame, self).save(*args, **kwargs)

	def delete(self):
		db = self.get_db()
		cursor = db.cursor()

		try:
			cursor.execute("DROP TABLE IF EXISTS %s" % (self.db_table_name,))
		except MySQLdb.Warning:
			pass
		cursor.close()	
		db.close()
		super(DataFrame, self).delete()

	def import_from_file(self, datafile):		
		db_table = '_dataframe' + '_U' + str(datafile.owner) + '_DF' + str(self.id)	

		import_string = "python data/includes/csv2mysql.py --table=%s --database=%s --user=%s --password=%s --host=%s %s" % (db_table, self.db_name, self.db_user, self.db_password, self.db_host, datafile.file.path)
		import_status = {'command': '', 'output': ''}	
		import_status['command'] = import_string
		import_status['output'] = os.popen(import_string).read()
		
		self.db_table_name = db_table
		super(DataFrame, self).save()
		return import_status
	
	def get_data(self):
		db = self.get_db()
		cursor = db.cursor()
		cursor.execute("SELECT * FROM %s" % (self.db_table_name))
		query_results = cursor.fetchall()

		cursor.close
		db.close()
		return query_results
		
	@models.permalink
	def get_absolute_url(self):
		return ("data:framedetail", (), {"slug": self.slug, "pk": self.id})

	@models.permalink
	def get_absolute_delete_url(self):
		return ("data:framedelete", (), {"slug": self.slug, "pk": self.id})



# Prob should get rid of this
class DataColumn(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)
	name = models.CharField(max_length=255)
	description = models.TextField()
	data_frame = models.ForeignKey(DataFrame, related_name = "data_column")
	slug = models.SlugField(max_length=255, blank=True, default='')
	db_column_name = models.CharField(max_length=255, blank=True, default='')

	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super(DataColumn, self).save(*args, **kwargs)

	@models.permalink
	def get_absolute_url(self):
		return ("data:file:column", (), {"slug": self.slug, "pk": self.id})
