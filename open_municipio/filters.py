from datetime import date

from django.db.models.loading import get_model

from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext as _
from django.contrib.admin import SimpleListFilter

class OMByYearFilterSpec(SimpleListFilter):    
    title = _('year')
    model = None
    field = None
    field_queryset = None

    parameter_name = "year"
    
    def __init__(self, *args, **kwargs):
        return super(OMByYearFilterSpec, self).__init__(*args,**kwargs)

    def lookups(self, request, model_admin):
        if self.model is None:
            raise Exception("You didn't specify the model to which this filter should be applied")

        if self.field is None:
            raise Exception("You didn't specify the field name to filter upon")

        options = ()

        years = []

        try:
            years = self.model.objects.dates(self.field,"year","DESC")

            for y in years:
                label = y.strftime("%Y")

                options += ( ( label,label ), )

        except Exception, e:
            # in case of any error, continue
            pass

        return options

    def queryset(self, request, queryset):

        if self.value() != None:
            year = self.value()
            return self.queryset_by_year(queryset, year)

        return queryset

    def queryset_by_year(self, queryset, year):
        raise Exception("You must override this method")

class OMByMonthFilterSpec(SimpleListFilter):
    title = _('month')
    model = None
    field = None

    parameter_name = "month"

    def __init__(self, *args, **kwargs):
        return super(OMByMonthFilterSpec, self).__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        options = ()

        for m in range(1,13):
            # you must set the 1st day of time, o/w may generate invalid dates
            # (e.g. 30 February, 31 April, etc...
            label = date.today().replace(day=1,month=m).strftime("%B")
            options += ( ( m, label ), )

        return options

    def queryset(self, request, queryset):
        month = self.value()

        if month is not None:   
            return self.queryset_by_month(queryset,month)

        return queryset

    def queryset_by_month(self, queryset, month):
        raise Exception("You must override this method")

class OMBySubTypeFilterSpec(SimpleListFilter):
    title = _('type')
    model = None

    parameter_name = "type"

    def lookups(self, request, model_admin):
        if self.model is None:
            raise Exception("You must specify a model before applying the sub-type filter")

        options = ()

        try:
            subs = self.model.__subclasses__()
            for s in subs:
                options += ( ( s.__name__,_(s.__name__)), )
        except Exception, e:
            pass

        return options


    def queryset(self, request, queryset):
        type = self.value()

        if type is not None:
            model_name = self.model._meta.object_name
            app_label = self.model._meta.app_label
            model_table_name = self.model._meta.db_table

            type_class = get_model(app_label, type)
            table_name = type_class._meta.db_table
        
            qs = queryset.extra(tables = [ table_name ], \
                where = [ '"%s"."id" = "%s"."act_ptr_id"' % \
                    (model_table_name, table_name) ])

            return qs

        return queryset


class OMByFieldDistinctFilter(SimpleListFilter):
    
    title = None
    model = None
    field = None
    field_label = None
    parameter_name = None
    
    def __init__(self, *args, **kwargs):
        self.title = self.title or self.field
        self.parameter_name = self.parameter_name or self.field

        super(OMByFieldDistinctFilter, self).__init__(*args, **kwargs)

    def lookups(self, request, model_admin):

#        print "in lookups: model = %s, field = %s ..." % (self.model, self.field)

        assert self.model != None
        assert self.field != None

        values = self.model.objects.all().values(self.field, self.field_label).distinct()

        res = map(lambda v: (v[self.field], v[self.field_label]), values)
        
#        print "res: %s" % res
        return res

    def queryset(self, request, queryset):
        res_qs = queryset

        if self.value() != None:
            filter_by = { self.field: self.value() }
            res_qs = res_qs.filter(**filter_by)

        return res_qs



