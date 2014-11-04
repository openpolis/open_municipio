import logging

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from open_municipio.monitoring.models import Monitoring

class Command(BaseCommand):
    """
    Remove from the database the Monitoring objects referring to non-existing
    monitored objects (aka dangling). This can happen, for instance, in case of 
    imported data that has been removed, after a test or a mistake was found
    """

    help = "Clear database from dangling monitoring objects"

    option_list = BaseCommand.option_list + (
        make_option('--dryrun',
                    action='store_true',
                    dest='dryrun',
                    default=False,
                    help='Do not alter database'),
        make_option('--preview',
                    action='store_true',
                    default=False,
                    help='Preview Monitoring objects to be removed'),
    )

    def handle(self, **options):

        if options['dryrun']:
            print "Dryrun mode ON: database will not be written ..."

        count = 0

        for m in Monitoring.objects.all():
            if m.content_object == None:
                if options['preview']:
                    print "Removing dangling monitored object: %s (%s)" % (m, m.id)

                if not options['dryrun']:
                    m.delete()        
                count = count + 1

        print "%s dangling monitoring objects deleted" % count
