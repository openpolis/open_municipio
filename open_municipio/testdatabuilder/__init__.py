# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.conf import settings

from open_municipio.testdatabuilder import conf
from open_municipio.people.models import Institution, Person, GroupCharge, Sitting, InstitutionCharge, municipality
from open_municipio.acts.models import  Act, ActSupport, Attachment, Deliberation, Interrogation
from open_municipio.taxonomy.models import Category, Tag
from open_municipio.votations.models import Votation, ChargeVote

try:
    import json
except ImportError:
    import simplejson as json

import random, os, sys, datetime, lipsum, itertools
from rst2pdf.createpdf import RstToPdf




class RandomItemsFactory(object):
    """
    This class is basically a collection of routines allowing automatic generation
    of a random dataset, that may be used to setup a realistic[*]_ testing enviroment
    for the *OpenMunicipio* web application.

    As a pre-requisite, the people models should be populated,
    either by the create_startup_people.py script, or by loading the test_data fixtures

    .. [*]: At least, this is the intended goal ;-)
    """

    APP_ROOT = os.path.abspath(os.path.dirname(__file__))

    def create_acts(self):
        """
        Create a bunch of acts.
        """
        # cleanup
        try:
            Act.objects.all().delete()
        except ObjectDoesNotExist:
            pass

        election_date = '2010-06-14'

        g = lipsum.Generator()

        #
        # creazione proposte di delibera di consiglio
        #
        institution = Institution.objects.get(slug='consiglio-comunale')

        for i in range(1, 20):
            d = Deliberation(
                idnum="%s" % i,
                title=g.generate_sentence(),
                text=g.generate_paragraph(),
                presentation_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                emitting_institution=institution,
                initiative=Deliberation.INITIATIVE_TYPES.counselor,
                )
            d.save()
            print "Delibera %s - %s creata" % (d.idnum, d.title)

            nf = random.randint(1, 3)
            nc = random.randint(0, 5)
            print "Aggiunta di %s primi firmatari"  % nf
            maj = random.choice([1, 1, 1, 1, 1, 1, 1, 1, 0]) # first-signers and co-signers come from maj 90% of the times
            presenters = self.get_institution_charges(majority=maj, n=(nf+nc))

            for presenter in presenters[0:nf]:
                act_support = ActSupport(
                    charge=presenter, act=d,
                    support_type=ActSupport.SUPPORT_TYPE.first_signer,
                    support_date=d.presentation_date
                )
                print "%s" % presenter
                act_support.save()

            print "Aggiunta di %s co firmatari"  % nc
            for presenter in presenters[nf:]:
                act_support = ActSupport(
                    charge=presenter, act=d,
                    support_type=ActSupport.SUPPORT_TYPE.co_signer,
                    support_date=d.presentation_date
                )
                print "%s" % presenter
                act_support.save()

            na = random.randint(0, 5)
            print "Aggiunta di %s allegati" % na
            self.generate_random_act_attach(d, n=na)


        for i in range(1, 10):
            a = Interrogation(
                idnum="%s" % i,
                title=g.generate_sentence(),
                text=g.generate_paragraph(),
                presentation_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                answer_type=random.choice([i[0] for i in Interrogation.STATUS]),
                emitting_institution=institution,
                )
            a.save()
            print "Interrogazione %s - %s creata" % (a.idnum, a.title)

        print "ok"

    def create_votations(self):
        # cleanup
        Sitting.objects.all().delete()
        Votation.objects.all().delete()

        council_institution = Institution.objects.get(institution_type=Institution.COUNCIL)

        # TODO:
        # .. yes and no percentages vary according to group and majority


        # generates N sittings and M votes
        n_sittings = random.randint(3, 4)
        n_votations = random.randint(5, 7)
        date_sitting = datetime.date.today() - datetime.timedelta(days=random.randint(n_sittings, 10))

        for s_cnt in range(1, n_sittings):

            date_sitting += datetime.timedelta(days=1)

            s = Sitting(
                idnum="C/000%s" % s_cnt,
                number=s_cnt,
                institution=council_institution,
                date=date_sitting
            )
            s.save()
            print "Seduta % screata" % s_cnt

            # generates N votations related to the current sitting
            for i in range(1, n_votations):

                # add a votation
                v = Votation(
                    sitting=s,
                    idnum="%s" % i,
                    n_legal=20,
                    )
                v.save()
                print "Votazione %s creata"  % i

                # link to a random act
                # leave some votations unlinked (10%)
                w = list(itertools.chain.from_iterable([
                    [False]*1, # 10% Do not link
                    [True]*9   # 90% Do link
                ]))
                if random.choice(w):
                    v.act = random.choice(Act.objects.all())
                    print "Atto collegato: %s" % v.act

                # define vote weights
                # itertools.chain.from_iterable flattens a nested list of lists
                # [i]*N creates a list of N integers i
                # choosing randomly from the flattened lists is almost equivalent
                # to choosing with weighted probabilities
                vw = list(itertools.chain.from_iterable([
                    [ChargeVote.VOTES.no]*30,  # 30% NO
                    [ChargeVote.VOTES.yes]*50,  # 50% YES
                    [ChargeVote.VOTES.abstained]*10,   #  5% ABSTAINED
                    [ChargeVote.VOTES.canceled]*5    #  5% ABSENT
                    [ChargeVote.VOTES.absent]*5    #  5% ABSENT
                ]))
                for charge in municipality.council.members:
                    # votings are drawn randomly with weighted probabilities
                    vote = random.choice(vw)
                    charge_vote = ChargeVote(votation=v, charge=charge, vote=vote)
                    charge_vote.save()
                    # print "%s voted %s" % (charge, charge_vote.vote)
                print "Voti creati"


                # compute voting totals
                v.n_yes = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.yes).count()
                v.n_no = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.no).count()
                v.n_abst = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.abstained).count()
                v.n_absents = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.absent).count()
                n_president = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.pres).count()
                v.n_presents = v.n_yes + v.n_no + v.n_abst + n_president
                v.n_maj = int(v.n_presents / 2) + 1
                if v.n_yes >= v.n_maj:
                    v.outcome = Votation.PASSED
                else:
                    v.outcome = Votation.REJECTED
                v.save()

                # update votation caches
                v.update_caches()
                print "Cache updated.\n"

                print "Totali"
                print "  Presenti: %s, Maggioranza: %s" % (v.n_presents, v.n_maj)
                print "  %s YES, %s NO, %s ABSTAINED" % (v.n_yes, v.n_no, v.n_abst)
                print "  Voto %s" % (v.get_outcome_display())

    def create_tags(self):
        """
        Create a bunch of tags, loaded from an external file.
        """
        print "Creating tags..."
        # Clear existing tag records
        Tag.objects.all().delete()
        try:
            for line in open(os.path.join(self.APP_ROOT, 'tags.txt')):
                Tag.objects.create(name=line.strip().lower())
        except IOError as e:
            print "Error while opening file: %s" % e
            sys.exit(1)

    def create_categories(self):
        """
        Create a bunch of categories, loaded from an external file.
        """
        print "Creating categories..."
        # Clear existing category records
        Category.objects.all().delete()
        try:
            for line in open(os.path.join(self.APP_ROOT, 'categories.txt')):
                Category.objects.create(name=line.strip().lower())
        except IOError as e:
            print "Error while opening file: %s" % e
            sys.exit(1)

    def classify_acts(self):
        """
        Classify each act in the database, by adding to it a random number of categories and,
        for each category, a random number of tags.
        """
        print  "Classifying acts..."
        for act in Act.objects.all():
            print  "        act #%s... " % act.pk
            # draw a random subset of categories
            population = list(Category.objects.all())
            sample_size = random.randint(conf.MIN_CATEGORIES_PER_ACT, conf.MAX_CATEGORIES_PER_ACT)
            categories = random.sample(population, sample_size)
            for category in categories:
                # add category to the act
                act.category_set.add(category)
                # draw a random subset of tags
                population = list(Tag.objects.all())
                sample_size = random.randint(conf.MIN_TAGS_PER_CATEGORY, conf.MAX_TAGS_PER_CATEGORY)
                tags = random.sample(population, sample_size)
                # add tags to the act
                act.tag_set.add(*tags, category=category)
                # associate tags with the category
                category.tag_set.add(*tags)


    def bookmark_acts(self):
        """
        Add the "key" status to a random subset of the acts stored within the DB.
        """
        print  "Bookmarkings acts..."
        for act in Act.objects.all():
            if random.random() < conf.KEY_ACTS_RATIO:
                act.is_key = True
                act.save()
                print  "        act #%s is key..." % act.pk


    def create_institutions(self):
        print "Institutions"
        sindaco_inst = Institution(
            name='Sindaco', institution_type=Institution.MAYOR,
            description="Ufficio del sindaco"
        )
        sindaco_inst.save()
        print "  sindaco"

        giunta_inst = Institution(
            name='Giunta comunale', institution_type=Institution.CITY_GOVERNMENT, parent=sindaco_inst,
            description="Descrizione dell'istituzione Giunta"
        )
        giunta_inst.save()
        print "  giunta"

        consiglio_inst = Institution(
            name='Consiglio comunale', institution_type=Institution.COUNCIL, parent=sindaco_inst,
            description="Descrizione dell'istituzione Consiglio"
        )
        consiglio_inst.save()
        print "  consiglio"

        # commissioni
        comm_descrizioni = [
            u"Bilancio e programmazione",
            u"Urbanistica, Infrastrutture e Lavori pubblici",
            u"Città sostenibile (Ambiente, Mobilità, Energia, Trasporto pubblico),frazioni, attività produttive, sport",
            u"Servizi alla Persona, Pubblica Istruzione e Politiche Giovanili",
            u"Cultura, Promozione e Turismo",
            u"Risorse Finanziarie e Patrimonio"
        ]
        commissioni = []
        print "  commissioni"
        for c in range(0,len(comm_descrizioni)):
            print "    %s - %s" % (c, comm_descrizioni[c])
            comm_inst = Institution(
                name='%d^ commissione' % (c+1), institution_type=Institution.COMMITTEE, parent=consiglio_inst,
                description=comm_descrizioni[c]
            )
            comm_inst.save()
            commissioni.append(comm_inst)


    def generate_people_dataset(self):
        """
        Generate institutions and commissions
        """
        self.create_institutions()

    def generate_acts_dataset(self):
        """
        Generate a random dataset for test purposes.
        """
        ## acts generation
        self.create_acts()
        ## taxonomy generation
        self.create_tags()
        self.create_categories()
        self.classify_acts()
        self.bookmark_acts()

    def generate_votations_dataset(self):
        """
        Generate a random votations dataset
        """
        self.create_votations()

    #
    # utilities
    #
    @classmethod
    def unify(cls, seq, idfun=None):
        """
        remove double elements from the seq list
        idfun is a callback to the identity function
        """
        # order preserving
        if idfun is None:
            def idfun(x): return x
        seen = {}
        result = []
        for item in seq:
            marker = idfun(item)
            # in old Python versions:
            # if seen.has_key(marker)
            # but in new ones:
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        return result

    @classmethod
    def create_person(cls):
        """
        create a random person in the db and return the person just created
        if the person already exists, return it
        """

        try:
            op_path = os.path.join(settings.PROJECT_ROOT, "testdatabuilder", "openpolis_samples")
            f = open(os.path.join(op_path, "op_politician_first_names_sex.csv"), "r")
            l = open(os.path.join(op_path, "op_politician_last_names.csv"), "r")
            loc = open(os.path.join(op_path, "op_politician_birth_locations.csv"), "r")
            dat = open(os.path.join(op_path, "op_politician_birth_dates.csv"), "r")

            first_names = cls.unify(f.readlines())
            last_names = cls.unify(l.readlines())
            birth_dates = cls.unify(dat.readlines())
            birth_locations = cls.unify(loc.readlines())

            first_name = random.choice(first_names)
            first_names.remove(first_name)
            first_name = first_name.strip()
            (names, gender) = first_name.split(',')
            if gender == 'M':
                gender = Person.GENDERS.male
            else:
                gender = Person.GENDERS.female
            names = names.split()
            first_name = random.choice(names)

            last_name = random.choice(last_names)
            last_names.remove(last_name)
            last_name = last_name.strip()

            birth_date = random.choice(birth_dates)
            birth_dates.remove(birth_date)
            birth_date = birth_date.strip()
            birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

            birth_location = random.choice(birth_locations)
            birth_locations.remove(birth_location)
            birth_location = birth_location.strip()

            persons = Person.objects.filter(first_name=first_name, last_name=last_name, birth_date=birth_date, birth_location=birth_location)
            if not persons:
                p = Person(first_name=first_name, last_name=last_name, birth_date=birth_date, birth_location=birth_location, gender=gender)
                p.save()
            else:
                p = persons[0]

            return p


        except IOError as e:
            print "Error while opening file: %s" % e
            return 0

    @classmethod
    def get_institution_charges(cls, institution='consiglio', majority=True, n=2):
        """
        returns a number of random institution charges, taken from a group
        or the group in majorities or opposition, as specified in the arguments

        prerequisites: at least n charges of that group must already exist
        if the number of charges is not sufficient, the maximum number is returned
        the function may return no charges (empty array) if the criteria are not matched
        """


        charges = []
        if majority:
            maj_gcharges = list(GroupCharge.objects.filter(group__groupismajority__is_majority=True,
                                                           group__groupismajority__end_date__isnull=True))

            rnd_gcharges = random.sample(maj_gcharges, n)
            for gcharge in rnd_gcharges:
                charges.append(gcharge.charge)

        return charges


    @classmethod
    def generate_random_act_attach(cls, act, n=1):
        """
        generates n random pdf attachments for an act

        title and body, are built using a lorem ipsum generator

        the attachments are built with text and a pdf file upload is simulated
        """
        # random title and body generation
        g = lipsum.MarkupGenerator()

        for i in range(1, n+1):
            title = g.generate_sentences_plain(1)
            body = g.generate_paragraphs_plain(random.randint(3, 50), start_with_lorem=True)

            # attach object created and saved
            attach = Attachment(act=act, title=title, text=body)
            attach.save()

            #
            # pdf document generation and upload in proper directory
            #

            # document setup
            if act is not None:
                header = "Atto %s - ###Title###" % (act.idnum,)
            else:
                header = "###Title###"
            footer = "###Section### - Pagina: ###Page###"
            text = "%s\n%s\n%s\n" % ("=" * int(len(title)*1.5), title, "=" * int(len(title)*1.5))
            text += body

            # pdf saved into tmp file
            file_name = "%s_%s.pdf" % (act.idnum, attach.id)
            tmp_file = os.path.join("/tmp", file_name)
            rst2pdf = RstToPdf(breaklevel=0, header=header, footer=footer)
            rst2pdf.createPdf(text=text,
                              output=tmp_file)

            # file is saved as attribute of the attach object and moved in the right path
            # see https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.FieldFile.save
            f = open(tmp_file, 'r')
            attach.file.save(file_name, File(f))
            attach.save()
            os.remove(tmp_file)

            print "%s: %s uploaded" % (i, file_name)


    @classmethod
    def weighted_choice(cls, weights):
        """
        choice of one element out of a weighted range
        """
        choice = random.random() * sum(weights)
        for i, w in enumerate(weights):
            choice -= w
            if choice < 0:
                return i


