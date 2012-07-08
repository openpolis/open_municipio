from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned 
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import pre_delete 
from django.template.defaultfilters import slugify

from open_municipio.om_utils.exceptions import MalformedLinkedList 

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
        
        
class LinkedListModel(models.Model):
    """
    An abstract model class representing a node of a (double-)linked list of model instances.
    
    It encapsulates generic data & logic that can be used to manage such data stuctures, including:
    
    * linked list navigation
    * addition/removal of nodes
    
    To use the facilities provided by this model, just subclass it and overrride the 
    ``_update_links()`` method, providing an implementation suitable to your specific
    use case.    
    """
    # a pointer to the *next* node in the list
    # the *previous* node may be accessed via the ``_previous`` attribute
    # (automagically added by Django as specified by ``related_name``
    next = models.OneToOneField('self', blank=True, null=True, 
                                related_name='_previous', on_delete=models.SET_NULL)
    
    # TODO: what happens if we had a node in the middle without specifying the ``_previous`` field?
    # the ``next`` field should be checked so that it cannot be pointed to a node already pointed by
    # another one    
    class Meta:
        abstract=True
    
    def save(self, *args, **kwargs):
        # update the ``_previous`` cache field
        self._update_links()
        # call base implementation of ``save()`` method
        super(LinkedListModel, self).save(*args, **kwargs)

    # in order to assure referential integrity, the previous node 
    # should be accessed only through this read-only attribute 
    @property
    def previous(self):
        """
        Return the node which comes before this one in the linked list.
        
        If this node is the first one on the list, return ``None``.
        """ 
        return self._previous
    
    @property
    def is_first(self):
        """
        Return ``True`` if this node is the first one on the linked list;
        ``False`` otherwise``
        """
        return self._previous is None
    
    @property
    def is_last(self):
        """
        Return ``True`` if this node is the last one on the linked list;
        ``False`` otherwise``
        """
        return self.next is None
    
    def calculate_previous(self):
        """
        Calculate the node which comes before this one in the linked list.
        
        If this node is the first one on the list, return ``None``.
        
        If multiple "previous" nodes are found, raise a ``MalformedLinkedList`` exception.
        """
        try:
            previous = self._default_manager.get(next=self)
            return previous
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise MalformedLinkedList("Node %s have more than one link pointing to it" % self) 
    
    def _update_links(self):
        """
        Update the ``_previous`` cache field.
        """
        self._previous = self.calculate_previous()

    
## Signal handlers
@receiver(pre_delete)
def update_linked_list(sender, **kwargs):
    """
    After a node has been deleted from the linked list, 
    accordingly update the next/previous pointers. 
    """
    # only react to signals sent by subclasses of ``LinkedListModel``
    if issubclass(sender, LinkedListModel):
        node = kwargs['instance'] # list node being deleted        
        if node.is_first or node.is_last:
            # if we are going to remove the first or the last node, 
            # then no action is needed, since the ``ON_DELET_SET_NULL`` 
            # SQL constraint took care of setting up things for us
            pass
        else:
            # we are going to remove a node in the middle of the linked list,
            # so a little bit of re-wiring is needed
            # adjust "next" pointer for the previous node
            node._previous.next = node.next._previous
            # adjust "previous" pointer for the next node
            node.next._previous = node._previous.next 