import datetime

from odoo import models, fields, api
from datetime import datetime, timedelta

class ProductAttribute(models.Model):
    _inherit = 'product.template.attribute.line'

    _order = 'date_time_add_attribute_line, number'

    number = fields.Integer()
    sequence = fields.Integer("Sequence", default=10)

    date_time_add_attribute_line = fields.Datetime()

    def create(self, vals_list):
        for i_time,value in enumerate(vals_list):
            value['date_time_add_attribute_line'] = fields.Datetime.now() + timedelta(milliseconds=i_time)

        # print('itaas_orders_line_numberrrrrrrrrrrrrrrrrrrrrrrr',vals_list)
        res = super(ProductAttribute,self).create(vals_list)

        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_number_line = fields.Boolean(compute='get_number', store=True, compute_sudo=True)


    @api.depends('attribute_line_ids', 'attribute_line_ids.sequence')
    def get_number(self):
        print('get_number')
        for obj in self:
            number = 1
            for line in obj.attribute_line_ids.filtered(lambda x: x.attribute_id).sorted(lambda x: x.sequence):
                line.number = number
                print('ddddddd', number)
                number += 1
            obj.is_number_line = True



