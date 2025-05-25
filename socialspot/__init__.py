"""socialspot""" 

__title__ = ''
__package__ = 'socialspot'
__author__ = ''
__author_email__ = ''

from .__version__ import __version__
from .checking import socialspot as search
from .socialspot import main as cli 
from .sites import socialspotEngine, socialspotSite, socialspotDatabase
from .notify import QueryNotifyPrint as Notifier