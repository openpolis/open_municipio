from open_municipio.testdatabuilder import conf

from open_municipio.acts.models import Act
from open_municipio.taxonomy.models import Category, Tag

import random, os, sys


class RandomItemsFactory(object):
    """
    This class is basically a collection of routines allowing automatic generation
    of a random dataset, that may be used to setup a realistic[*]_ testing enviroment
    for the *OpenMunicipio* web application.
    
    .. [*]: At least, this is the intended goal ;-)
    """
    
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    
    def create_acts(self):
        """
        Create a bunch of acts. 
        """
        raise NotImplementedError
    
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
                act.tag_set.add(*tags)
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

    def generate_dataset(self):
        """
        Generate a random dataset for test purposes. 
        """
        # self.create_acts()
        ## taxonomy generation
        self.create_tags()
        self.create_categories()
        self.classify_acts()
        self.bookmark_acts()
        
if __name__ == '__main__':
    RandomItemsFactory().generate_dataset()
        
