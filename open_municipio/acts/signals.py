"""
Act-related, custom signals go here.
"""

from django.dispatch import Signal

# sent when an act has reached its *initial* status (usually, ``PRESENTED``) 
act_presented = Signal(providing_args=[])
# sent when an act receives a new signature from a politician
act_signed = Signal(providing_args=[])
# sent when an act changes its status
act_status_changed = Signal(providing_args=[])