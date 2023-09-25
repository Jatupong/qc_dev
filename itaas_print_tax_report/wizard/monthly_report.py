# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
#from StringIO import StringIO
from io import BytesIO
import base64
from odoo.exceptions import UserError
from odoo.tools import misc
import xlwt
from decimal import *
from dateutil.relativedelta import relativedelta
import calendar
from io import StringIO
import xlsxwriter



#this is for tax report section
class monthly_report(models.TransientModel):
    _name = 'monthly.report'