from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

class SlugModel(models.Model):
    """
    An abstract base class encapsulating data & logic shared by models 
    needing a ``SlugField``.
    """
    slug = models.SlugField(verbose_name=_('Slug'), blank=True, unique=True, max_length=100)
    
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        # auto-generate a slug, if needed
        # only if this instance has not already been saved to the DB *and*
        # the ``slug`` field has not been manually set
        if not self.pk and not self.slug:
            self.slug = self.calculate_slug()
        return super(SlugModel, self).save(*args, **kwargs)
    
    def _slugify(self, base, i=None):
        slug = slugify(base)
        if i is not None:
            slug += '_%d' % i
        return slug
     
    def calculate_slug(self, base=None):
        """
        Convert an arbitrary string ``base`` into another one, suitable to be used as a slug.
        
        If the calculated slug already exists in the DB, add a numerical suffix until is OK.

        If the ``base`` argument is not provided, the source string default to the ``name`` attribute
        of the given model instance. If no ``name`` attribute is defined, neither, raise a ``TypeError``.
        """
        try:
            base = base or self.name
            # first candidate slug
            slug = self._slugify(base)
            # the model class this instance belongs to
            model = self.__class__
            i = 0
            while True:
                i += 1
                try:
                    # check if candidate slug already exists within the DB
                    model._default_manager.get(slug=slug)
                except model.DoesNotExist:
                    # candidate slug doesn't exist, so return it
                    return slug
                else:
                    # roll-over another candidate slug
                    slug = self._slugify(base, i)
        except AttributeError:
            msg = "You should either provide a `base' argument or define a `name' attribute for this model instance: %s" % self
            raise TypeError(msg)
