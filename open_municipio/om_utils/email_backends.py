import datetime
from django.core.mail.backends.filebased import EmailBackend
import os

class EMLBackend(EmailBackend):
    """
    Class that writes email into a specified location, using the eml extension, rather than the default log one
    """
    def __init__(self, *args, **kwargs):
        super(EMLBackend, self).__init__(*args, **kwargs)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        fname = "%s-%s.eml" % (timestamp, abs(id(self)))
        self._fname = os.path.join(self.file_path, fname)
