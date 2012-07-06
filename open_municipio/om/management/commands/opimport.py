# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError, LabelCommand
from django.conf import settings
from optparse import make_option

import urllib2
import json
from open_municipio.people.models import Person, Group, InstitutionCharge, Institution, GroupCharge, InstitutionResponsability


class Command(LabelCommand):
    """
    Poiticians anagraphical data and their current and past charges are imported from the
    openpolitici database.

    An openpolis location id MUST be passed along to specify the location.

    Data may be compared or re-written. By default they're compared,
    to overwrite use the --overwrite option.
    """
    help = "Import a location's institution charges, given the op_location_id"

    option_list = BaseCommand.option_list + (
        make_option('--overwrite',
                    action='store_true',
                    dest='overwrite',
                    default=False,
                    help='Re-write charge from scratch'),
        )

    args = '<op_location_id>'
    label = 'op_location_id'

    def handle(self, *labels, **options):
        if not labels:
            raise CommandError('Enter at least one %s.' % self.label)

        if len(labels) > 1:
            raise CommandError('Enter a single %s.' % self.label)

        output = []
        for label in labels:
            label_output = self.handle_label(label, **options)
            if label_output:
                output.append(label_output)
        return '\n'.join(output)


    def handle_label(self, op_location_id, **options):

        # cleanup
        Person.objects.all().delete()
        InstitutionCharge.objects.all().delete()
        Group.objects.all().delete()

        # build location url and fetch the response in json format
        location_url = "%s/%s/" % (settings.OP_API_LOCATION_BASE_URL, op_location_id)
        json_data = self.get_json_response(location_url)
        if 'exception' in json_data:
            raise CommandError("%s\n" % json_data['exception'])
        else:
            for organ in ('giunta', 'consiglio'):
                self.stdout.write("%s\n%s\n" % (organ, '='*len(organ)))
                members = json_data[organ]
                for member in members:
                    # date reduction
                    birth_date = member['birth_date'][0:10]
                    start_date = member['date_start'][0:10]
                    if member['gender'] == 'M':
                        member_gender = Person.GENDERS.male
                    else:
                        member_gender = Person.GENDERS.male

                    # fetch or create person
                    p, p_created = Person.objects.get_or_create(
                        first_name=member['first_name'],
                        last_name=member['last_name'],
                        birth_date=birth_date,
                        birth_location=member['birth_location'],
                        gender=member_gender
                    )

                    if 'party' in member:
                        party = member['party']
                    if 'group' in member:
                        group = member['group']
                        g, g_created = Group.objects.get_or_create(
                            name=group,
                            acronym=group[0:15]
                        )

                    # create charge description
                    if organ == 'giunta':
                        charge_description = "Assessore %s" % member['charge_descr']
                        charge_institution = Institution.objects.get(institution_type=Institution.CITY_GOVERNMENT)
                    else:
                        charge_description = ""
                        charge_institution = Institution.objects.get(institution_type=Institution.COUNCIL)

                    # membership charge (do not insert vicesindaco now, do that at the end)
                    if member['charge'] != 'Vicesindaco':
                        charge = InstitutionCharge(
                            description=charge_description,
                            start_date = start_date,
                            person = p,
                            institution = charge_institution
                        )
                        charge.save()

                    if organ == 'giunta':
                        # sindaco è membro di giunta con responsability
                        if member['charge'] == 'Sindaco':
                            resp = InstitutionResponsability(
                                description="Sindaco",
                                start_date=start_date,
                                charge=charge,
                                charge_type=InstitutionResponsability.CHARGE_TYPES.mayor
                            )
                            resp.save()
                            # sindaco è anche membro di istituzione sindaco
                            sindaco_charge = InstitutionCharge(
                                description="Sindaco",
                                start_date = start_date,
                                person = p,
                                institution = Institution.objects.get(institution_type=Institution.MAYOR)
                            )
                            sindaco_charge.save()


                    if organ == 'consiglio':
                        # presidente del consiglio è consigliere con responsability
                        if member['charge'] == 'Presidente':
                            resp = InstitutionResponsability(
                                description="Presidente del Consiglio Comunale",
                                start_date=start_date,
                                charge=charge,
                                charge_type=InstitutionResponsability.CHARGE_TYPES.president
                            )
                            resp.save()

                        # vice presidente del consiglio è consigliere con responsability
                        if member['charge'] == 'Vicepresidente':
                            resp = InstitutionResponsability(
                                description="Vicepresidente del Consiglio Comunale",
                                start_date=start_date,
                                charge=charge,
                                charge_type=InstitutionResponsability.CHARGE_TYPES.vice
                            )
                            resp.save()

                        # nel consiglio il sindaco è consigliere con responsability
                        if not p_created and sindaco_charge.person == p:
                            resp = InstitutionResponsability(
                                description="Sindaco",
                                start_date=start_date,
                                charge=charge,
                                charge_type=InstitutionResponsability.CHARGE_TYPES.mayor
                            )
                            resp.save()

                        # group charge
                        gc = GroupCharge.objects.create(group=g, charge=charge, start_date=start_date)
                        gc.save()


                    # output line must be encoded explicitly into utf-8
                    # before being sent to stdout
                    output_line = "%s %s - %s - %s: %s\n" % \
                                (member['first_name'], member['last_name'],
                                 member['birth_date'][0:10], member['birth_location'],
                                 member['textual_rep'])
                    self.stdout.write(output_line.encode('utf-8'))

                self.stdout.write("\n")

                # add vicesindaco now, at the end
                # this is done here, because the Vicesindaco may come with two charges
                # assessore and vicesindaco
                #
                # it would be wrong to have both institutional charges, since
                # vicesindaco is better mapped as a ResponsabilityCharge
                #
                # the following code binds the vicesindaco to a previous
                # assessore charge, if existing, or create a new assessore charge,
                #and binds the responsability to it
                fd = None
                for m in members:
                    if m['charge'] == 'Vicesindaco':
                        fd = m
                        break

                if fd is not None:
                    # get the person (already created)
                    fd_person = Person.objects.get(
                        first_name=fd['first_name'],
                        last_name=fd['last_name'],
                        birth_date=fd['birth_date'][0:10],
                        birth_location=fd['birth_location']
                    )
                    # define institution (city government)
                    fd_charge_institution = Institution.objects.get(institution_type=Institution.CITY_GOVERNMENT)

                    # get or create a city gov charge for the person
                    fd_charge, created = InstitutionCharge.objects.get_or_create(
                        person=fd_person,
                        institution=fd_charge_institution,
                    )

                    # if newly created, then it is starting along with the Vicesindaco
                    # responsability and it is simply marked as Assessore
                    if created:
                        fd_charge.description="Assessore"
                        fd_charge.start_date=fd['date_start'][0:10]
                        fd_charge.save()

                    # responsability added to the charge
                    resp = InstitutionResponsability(
                        description="Vicesindaco",
                        start_date=fd_charge.start_date,
                        charge=fd_charge,
                        charge_type=InstitutionResponsability.CHARGE_TYPES.firstdeputymayor
                    )
                    resp.save()

                    self.stdout.write("Vicesindaco created\n")






    def get_json_response(self, url):
        """
        generic method to get json response from url,
        using basic authentication
        """
        username = settings.OP_API_USER
        password = settings.OP_API_PASS

        # this creates a password manager
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, username, password)
        # because we have put None at the start it will always
        # use this username/password combination for  urls
        # for which `theurl` is a super-url

        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        # create the AuthHandler

        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)
        # All calls to urllib2.urlopen will now use our handler
        # Make sure not to include the protocol in with the URL, or
        # HTTPPasswordMgrWithDefaultRealm will be very confused.
        # You must (of course) use it when fetching the page though.

        response = urllib2.urlopen(url)
        return json.loads(response.read())
