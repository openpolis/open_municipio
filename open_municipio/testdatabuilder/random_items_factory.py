#!/usr/bin/env python
# -*- coding: utf8 -*-
try:
    import json
except ImportError:
    import simplejson as json
import lipsum
from rst2pdf.createpdf import RstToPdf
import random
from datetime import *
import csv
import os

from django.core.files import File
from django.conf import settings

from open_municipio.people.models import *
from open_municipio.acts.models import *


def unify(seq, idfun=None):  
  '''
  remove double elements from the seq list
  idfun is a callback to the identity function
  '''
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


def get_institution_charges(institution='consiglio', majority=True, group=None, n=2):
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


def generate_random_act_attach(act, n=1):
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
        attach = Attach(act=act, title=title, text=body)
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
        attach.pdf_file.save(file_name, File(f))
        attach.save()
        os.remove(tmp_file)
        
        print "%s: %s uploaded" % (i, file_name)
    


def weighted_choice(weights):
    """
    choice of one element out of a weighted range
    """
    choice = random() * sum(weights)
    for i, w in enumerate(weights):
        choice -= w
        if choice < 0:
            return i
            

