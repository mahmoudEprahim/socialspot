"""socialspot""" # اسم المشروع الجديد

__title__ = ''
__package__ = 'socialspot' # ممتاز، تم التعديل هنا
__author__ = ''
__author_email__ = ''

from .__version__ import __version__
from .checking import socialspot as search # تم تغيير maigret إلى socialspot
from .socialspot import main as cli # تم تغيير maigret إلى socialspot (اسم الملف والدالة)
from .sites import socialspotEngine, socialspotSite, socialspotDatabase # تم تغيير Maigret إلى socialspot في أسماء الفئات
from .notify import QueryNotifyPrint as Notifier