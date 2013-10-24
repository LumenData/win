from django.db.models import fields
from django.template.defaultfilters import slugify

def unique_slug(model, slug_field, slug_value):
    orig_slug = slug = slugify(slug_value)
    
    index = 0
    
    while True:
        try:
            model.objects.get(**{slug_field: slug})
            index += 1
            slug = orig_slug + '-' + str(index)
        except model.DoesNotExist:
            return slug

class AutoSlugField(fields.SlugField):
    def pre_save(self, model_instance, add):
        if self.prepopulate_from:
            if self.unique:
                return unique_slug(model_instance.__class__, self.name, getattr(model_instance, self.prepopulate_from[0]))
            else:
                return slugify(getattr(model_instance, self.prepopulate_from[0]))
        else:
            return super(AutoSlugField, self).pre_save(model_instance, add)