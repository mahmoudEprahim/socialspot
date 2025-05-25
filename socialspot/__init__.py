"""Maigret"""

__title__ = ''
__package__ = 'maigret'
__author__ = ''
__author_email__ = ''


from .__version__ import __version__
from .checking import maigret as search
from .maigret import main as cli
from .sites import MaigretEngine, MaigretSite, MaigretDatabase
from .notify import QueryNotifyPrint as Notifier
