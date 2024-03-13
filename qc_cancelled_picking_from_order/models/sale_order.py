# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:12|M:03|Y:2024]

from odoo import fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"


    # @api.multi
    def _action_cancel(self):
        mess=""
        mess+="fn _action_cancel Action!\n"
        res = super(SaleOrder, self)._action_cancel()
        if len(self.picking_ids) == 1:
            mess+="Picking_ids ID:[{}] Name:[{}] State:[{} -->".format(self.picking_ids.id,self.picking_ids.name,self.picking_ids.state)
            self.picking_ids.action_cancel()
            mess += "{}]\n".format(self.picking_ids.state)
        elif len(self.picking_ids) > 1:
            for picking in self.picking_ids:
                mess += "Picking_ids ID:[{}] Name:[{}] State:[{} -->".format(picking.id, picking.name,
                                                                         picking.state)
                picking.action_cancel()
                mess += "{}]\n".format(picking.state)
        for obj in self:
            obj.write({'state': 'draft'})

            reset_mr_id = obj.env['manufacturing.request.custom'].search([('sale_order_id.order_id', '=', self.name),('state','!=','cancel')],
                                                                    limit=1)
            print('reset_mr_id',reset_mr_id)
            for mr in reset_mr_id:
                mr.custom_action_cancel()

        if self.user_has_groups('base.group_no_one'):
            raise UserError(_(mess+"\nBy Debug mode [Sarawut Ph.]"))

        return res
