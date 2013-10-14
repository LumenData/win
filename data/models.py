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
	owner = models.ForeignKey(User, related_name="data_files", default=1)
	slug = models.SlugField(max_length=255, blank=True, default='')
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
		return ("data:file", (), {"slug": self.slug})

# @receiver(pre_delete, sender=DataFile)
# def datafile_delete(sender, instance, **kwargs):
# 	# Pass false so FileField doesn't save the model.
# 	instance.file.delete(False)


class DataColumn(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)
	name = models.CharField(max_length=255)
	description = models.TextField()
	parent_file = models.ForeignKey(DataFile, related_name = "data_columns")
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
