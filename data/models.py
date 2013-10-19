from django.db import models
from django.template.defaultfilters import slugify	
from django.contrib.auth.models import User

# For deleting the file on delete
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver


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

	@models.permalink
	def get_absolute_url(self):
		return ("data:filedetail", (), {"slug": self.slug})

	@models.permalink
	def get_absolute_delete_url(self):
		return ("data:filedelete", (), {"slug": self.slug})

	@models.permalink
	def get_absolute_import_url(self):
		return ("data:fileimport", (), {"slug": self.slug})


class DataFrame(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255, blank=True, default='')
	owner = models.ForeignKey(User, related_name="data_frame", default=1)

	def __unicode__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.name:
			self.name = self.file.name
		if not self.slug:
			self.slug = slugify(self.name)
		super(DataFile, self).save(*args, **kwargs)

	@models.permalink
	def get_absolute_url(self):
		return ("data:frame_detail", (), {"slug": self.slug})


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
#		self.db_column_name = self.owner.username + "_" + self.parent_file.slug + "_" + self.slug
		super(DataColumn, self).save(*args, **kwargs)

	@models.permalink
	def get_absolute_url(self):
		return ("data:file:column", (), {"slug": self.slug})
