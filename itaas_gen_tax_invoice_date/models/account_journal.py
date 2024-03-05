# -*- coding: utf-8 -*-
# Copyright (C) 2020-present ITaas.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
class Account_Journal(models.Model):
    _inherit = "account.journal"



    is_reverse_journal = fields.Boolean("Is Reverse")
