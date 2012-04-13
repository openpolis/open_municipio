from django.db import models
from django.template.defaultfilters import slugify

class SlugModel(models.Model):
    """
    An abstract base class providing helper methods for models declaring a ``SlugField``.
    """
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        # auto-generate a slug, if needed 
        if not self.pk and not self.slug:
            self.slug = self.calculate_slug()
        return super(SlugModel, self).save(*args, **kwargs)
    
    def slugify(self, tag, i=None):
        slug = slugify(tag)
        if i is not None:
            slug += "_%d" % i
        return slug
     
    def calculate_slug(self):
        """
        Calculate a slug for a given category name.
        
        If a calculated slug already exists in the DB, add a numerical prefix until is OK.
        """
        slug = self.slugify(self.name)
        model = self.__class__
        i = 0
        while True:
            i += 1
            try:
                model.objects.get(slug=slug)
                slug = self.slugify(self.name, i)
            except model.DoesNotExist:
                return slug