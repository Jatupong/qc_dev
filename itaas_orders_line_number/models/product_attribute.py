from odoo import models, fields, api


class ProductAttribute(models.Model):
    _inherit = 'product.template.attribute.line'

    number = fields.Integer()
    sequence = fields.Integer("Sequence", default=10)

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



