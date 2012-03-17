from open_municipio.testdatabuilder import conf

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
        raise NotImplementedError
    
    def generate_dataset(self):
        """
        Generate a random dataset for test purposes. 
        """
        self.create_acts()
        ## taxonomy generation
        self.create_tags()
        self.create_categories()
        self.classify_acts()
        
        
        