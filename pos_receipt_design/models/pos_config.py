# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import fields, models, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    use_custom_receipt = fields.Boolean(string="Use Custom Receipt")
    receipt_design_id = fields.Many2one('receipt.design', string="Receipt Design")
    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    use_custom_receipt = fields.Boolean(string="Use Custom Receipt", related='pos_config_id.use_custom_receipt', readonly=False)
    receipt_design_id = fields.Many2one('receipt.design', string="Receipt Design", related='pos_config_id.receipt_design_id', readonly=False)