'''
Created on 14/set/2013

@author: spegni
'''
import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from open_municipio.votations.models import Votation

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--fake',
            action='store_true',
            dest='fake',
            default=False,
            help='Simulate a delete operation, without modifying the database'),                                             
                                             
        make_option('--from_date',
            action='store_true',
            dest='from_date',
            default=None,
            help='Delete ballots after the specified date (YYYY-MM-DD)'),
                                             
        make_option('--to_date',
            action='store_true',
            dest='to_date',
            default=None,
            help='Delete ballots before the specified date (YYYY-MM-DD)'),
                                             
        make_option('--date',
            action='store_true',
            dest='date',
            default=None,
            help='Delete ballots in the specified date (YYYY-MM-DD)'),
        
        make_option('--year',
#            action='store_true',
            dest='year',
            default=None,
            help='Delete ballots in the specified year (YYYY)'),
        
        make_option('--month',
 #           action='store_true',
            dest='month',
            default=None,
            help='Delete ballots in the specified month (MM)'),
        
        make_option('--day',
#            action='store_true',
            dest='day',
            default=None,
            help='Delete ballots in the specified day (DD)'),
                                             
        make_option('--all',
            action='store_true',
            dest='all',
            default=False,
            help='Delete all ballots'),
        )

    fake = False
    date_format = "%Y-%M-%D"


    def handle(self, *args, **options):
        from_date = None
        to_date = None
        date = None
        
        year = None
        month = None
        day = None
        
        delete_all = False
        
        # analyze passed options
        
        if options["fake"]:
            self.fake = True
        
        if options["from_date"]:
            from_date = datetime.datetime.strptime(options["from_date"], self.date_format)
        
        if options["to_date"]:
            to_date = datetime.datetime.strptime(options["from_date"], self.date_format)
            
        if options["date"]:
            date = datetime.datetime.strptime(options["date"], self.date_format)
            
        if options["year"]:
            year = int(options["year"])
            
        if options["month"]:
            month = int(options["month"])
            
        if options["day"]:
            day = int(options["day"])
            
        if options["all"]:
            delete_all = True    
            
        # actually delete ballots
        
        if from_date or to_date:
            self._delete_interval(from_date, to_date)
            
        if date:
            self._delete_interval(date, date)
            
        if year or month or day:
            self._delete_date(year, month, day)
            
        if delete_all:
            self._delete_all()
        
    def _prompt(self, prompt_string, allowed_values=None):
        
        if not hasattr(allowed_values, "__iter__"):
            raise ValueError("The passed allowed values should be an iterable of string")
        
        if allowed_values:
            prompt = u"%s (%s)" % (prompt_string, ",".join(allowed_values))
        
        user_input = raw_input("%s: " % prompt)
        
        if allowed_values:
            if not user_input in allowed_values:
                print "The passed value is not allowed. Choose between: %s" % (",".join(allowed_values))
                return self._prompt(prompt_string, allowed_values)
                
                
        return user_input
        
    def _delete(self, qs):
        num_votes = qs.count()
        
        if not self.fake:
            # TODO prompt command for confirmation
            try:
                prompt = self._prompt("You are going to delete %s ballots. Are you sure?" % (num_votes,), ("y","n"))
                if prompt != "y":
                    raise CommandError("Command interrupted by the user")
            except KeyboardInterrupt:
                raise CommandError("Command interrupted by the user")
            qs.delete()
            
        print "Ballots deleted: %s" % (num_votes,)
        
    def _select_all(self):
        return Votation.objects.all()    
    
    def _delete_all(self):
        qs = self._select_all()
        self._delete(qs)
        
    def _delete_date(self, year=None, month=None, day=None):
        
        if not year and not month and not day:
            raise CommandError("At least one of day, month, year should be specified")
        
        qs = self._select_all()
        
        if year:
            qs = qs.filter(sitting__date__year=year)
            
        if month:
            qs = qs.filter(sitting__date__month=month)
            
        if day:
            qs = qs.filter(sitting__date__day=day)
            
        self._delete(qs)
        
    def _delete_interval(self, date_min=None, date_max=None):
        
        if not date_min and not date_max:
            raise CommandError("You must specify at least one between date_min and date_max")
        
        qs = self._select_all()
        
        if date_min:
            qs = qs.filter(sitting__date__gt=date_min)
            
        if date_max:
            qs = qs.filter(sitting__date__lt=date_max)
        
        self._delete(qs)
        
    