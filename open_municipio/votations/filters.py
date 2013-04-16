from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.filterspecs import FilterSpec

class IsLinkedFilterSpec(FilterSpec):
    """
    Adds filtering by existance of at least one link to a related object.
    
    Note: this is an hack, as described in here:
    http://stackoverflow.com/questions/991926/custom-filter-in-django-admin
    
    Django 1.4 implements a proper API to define custom filters
    
    Set
    my_model_field.is_linked_filter = True
    in your model
    
    and add 'my_model_field' to the list_filter tuple in admin.py
    """
    
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super(IsLinkedFilterSpec, self).__init__(f, request, params, model,
                                                 model_admin, field_path)
        self.lookup_kwarg = '%s__isnull' % self.field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
    
    
    def choices(self, cl):
        yield {'selected': self.lookup_val == None,
               'query_string': cl.get_query_string({},[self.lookup_kwarg]),
               'display': _('Any')}
        
        yield {'selected': self.lookup_val == 'False',
               'query_string': cl.get_query_string({self.lookup_kwarg: False}),
               'display': _('Yes')}
        
        yield {'selected': self.lookup_val == 'True',
               'query_string': cl.get_query_string({self.lookup_kwarg: True}),
               'display': _('No')}
        
    
    
    def title(self):
        return "Linked"
    


# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'is_linked_filter', False),
                                   IsLinkedFilterSpec))
