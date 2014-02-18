from datetime import datetime

from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from open_municipio.acts.models import ActSupport


def get_possible_acts():
    return map(lambda c: c.model, ContentType.objects.filter(app_label="acts"))

class Command(BaseCommand):
    
    date_format = "%Y-%m-%d"

    option_list = BaseCommand.option_list + (
        make_option("--date_from",
            action="store",
            dest="date_from",
            type="string",
            default=None,
            help="Set the beginning of the interval for which signatures should be deleted"),
         make_option("--date_to",
            action="store",
            dest="date_to",
            type="string",
            default=None,
            help="Set the end of the interval for which signatures should be deleted"),
          make_option("--act_type",
            action="store",
            dest="act_type",
            type="string",
            default=None,
            help="Set the type of act for which signatures should be deleted. Values: %s" % (",".join(get_possible_acts()))),
           make_option("--support_type",
            action="store",
            dest="support_type",
            type="string",
            default=None,
            help="Set the type of act for which signatures should be deleted. Values: %s" % (",".join(get_possible_acts()))),
     
    )

    def handle(self, *args, **options):
        
        signatures = self.select_signatures(options)

        try:
            num_sign = signatures.count()
            signatures.delete()
            print "Deleted %s signatures" % (num_sign)
        except Exception, e: 
            print "Error deleting signatures: %s" % e


    def select_signatures(self, options):

        date_from = options.get("date_from", None)
        date_to = options.get("date_to", None)
        act_type = options.get("act_type", None)
        support_type = options.get("support_type", None)

        qs = ActSupport.objects

        if date_from:
            date_from = datetime.strptime(date_from, self.date_format)
            qs = qs.filter(support_date__gte=date_from)

        if date_to:
            date_to = datetime.strptime(date_to, self.date_format)
            qs = qs.filter(support_date__lte=date_to)

        if support_type:
            qs = qs.filter(support_type=support_type)

        # TODO filter by act_type
        # TODO handle errors in input values

        return qs.all()

