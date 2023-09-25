from odoo import models, fields, api


class AddColumFieldInCustomers(models.Model):
    _inherit = 'res.partner'

    team_customers = fields.Many2one('res.teams.customers', string='Team')
    type_customers = fields.Many2one('res.type.customers', string='Type')
    group_customers = fields.Many2one('res.group.customers', string='Group')
    channel_customers = fields.Many2one('res.channel.customers', string='Channel')

    region = fields.Char(string='Region')
    area_type = fields.Char(string='Area')
    payment_term_code = fields.Char(string='Payment term code',related="property_supplier_payment_term_id.payment_term_code")




