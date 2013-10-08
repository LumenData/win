from django.db import models
from django.template.defaultfilters import slugify

class DataFrame(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True, editable=False)
	name = models.CharField(max_length=255)
	description = models.TextField()
	description2 = models.TextField()

	slug = models.SlugField(max_length=255, blank=True, default='')
	db_table_name = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super(DataFrame, self).save(*args, **kwargs)
	
	@models.permalink
	def get_absolute_url(self):
		return ("data:detail", (), {"slug": self.slug})
