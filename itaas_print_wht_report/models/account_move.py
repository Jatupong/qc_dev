# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from datetime import datetime, timedelta
from odoo import api,fields, models, _
from odoo.osv import osv
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import base64
import xlwt
import math
import math



class AccountMoveLine(models.AbstractModel):
    _inherit = 'account.wht.type'

    condition = fields.Selection([("pnd2_1", "1"), ("pnd2_2", "2"), ("pnd2_3", "3"), ("pnd2_4", "4"), ("pnd2_5", "5")],
                                 string="Condition PND2")

class AccountMove(models.AbstractModel):
    _inherit = 'account.move'

    def debug_mode(self):
        return self.user_has_groups('base.group_no_one')

class AccountMoveline(models.AbstractModel):
    _inherit = 'account.move.line'

    def debug_mode(self):
        return self.user_has_groups('base.group_no_one')