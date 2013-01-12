from django.db import models
from datetime import datetime

class Newsletter(models.Model):
    """
    A simple table, to keep track of the sent newsletter.
    An instance is created at the beginning of the news extractions
    After emails are computed and sent, the instance is updated,
    with the sent timestamp and the number of mails sent.
    """
    n_mails = models.IntegerField(default=0)
    started = models.DateTimeField(editable=False, auto_now_add=True)
    finished = models.DateTimeField(editable=False, blank=True, null=True)

    def save(self, **kwargs):
        if not self.id:
            self.started = datetime.now()
        super(Newsletter,self).save()

    def __unicode__(self):
        return "inizio: {n.started}, fine: {n.finished}, n mail: {n.n_mails}".format(n=self)
