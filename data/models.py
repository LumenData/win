from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class DataFrame(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)
	name = models.CharField(max_length=255, blank=True, default='some name')
	description = models.TextField(blank=True, default='')
	owner = models.ForeignKey(User, related_name="data_frames", default=1)
	slug = models.SlugField(max_length=255, blank=True, default='')
	db_table_name = models.CharField(max_length=255, blank=True, default='')
	docfile = models.FileField(upload_to='documents/')

	def __unicode__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		self.db_table_name = self.owner.username + "_" + self.slug
		super(DataFrame, self).save(*args, **kwargs)

	@models.permalink
	def get_absolute_url(self):
		return ("data:frame", (), {"slug": self.slug})


class DataColumn(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)
	name = models.CharField(max_length=255)
	description = models.TextField()
	parent_frame = models.ForeignKey(DataFrame, related_name = "data_columns")
	slug = models.SlugField(max_length=255, blank=True, default='')
	db_column_name = models.CharField(max_length=255, blank=True, default='')

	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
#		self.db_column_name = self.owner.username + "_" + self.parent_frame.slug + "_" + self.slug
		super(DataColumn, self).save(*args, **kwargs)

	@models.permalink
	def get_absolute_url(self):
		return ("data:frame:column", (), {"slug": self.slug})
