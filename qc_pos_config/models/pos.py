# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class Pos_config(models.Model):
    _inherit ="pos.config"

    license_number = fields.Char('เลขที่อนุญาติ')
    pos_number = fields.Char('POS Number')
    operating_unit_id = fields.Many2one('operating.unit',string='Branch')
    refund_sequence_id = fields.Many2one('ir.sequence', string='Refund Order IDs Sequence', copy=False,
                                         ondelete='restrict')

# class hremployee(models.Model):
#     _inherit ="hr.employee"
#
#     _sql_constraints = [
#         ('user_uniq', '(1==1)',
#          "A user cannot be linked to multiple employees in the same company.")
#     ]



class PosSession(models.Model):
    _inherit = 'pos.session'

    def create_account_entry(self):
        # for order_id in self.order_ids:
        sale_ids = self.order_ids.filtered(lambda x: x.amount >= 0)
        return_ids = self.order_ids - sale_ids

        for sale_id in sale_ids:
            print ('generate sale move line')
        for sale_return_id in return_ids:
            print ('generate sale return')

        # for payment_id in self.payment_ids:
        pos_payment_ids = self.env['pos.payment'].search([('session_id', 'in', self.ids)])
        sale_pos_payment_is = pos_payment_ids.filtered(lambda x: x.amount >= 0)
        return_pos_payment_ids = pos_payment_ids - sale_pos_payment_is
        for sale_payment_id in sale_pos_payment_is:
            print('generate sale move line')

        for sale_return_payment_id in return_pos_payment_ids:
            print('generate sale move line')


    def _prepare_line(self, order_line):
        def get_income_account(order_line):
            print ('get_income_account')
            # res = super(PosSession,self).get_income_account(order_line)
            # return res
            product = order_line.product_id
            print('CHECK_1')
            account_ids = product.with_company(order_line.company_id)._get_product_accounts()
            print('CHECK_2',account_ids)
            if order_line.tax_ids_after_fiscal_position and order_line.tax_ids_after_fiscal_position[0].amount > 0:
                if order_line.refunded_orderline_id:
                    return order_line.order_id.fiscal_position_id.map_account(account_ids['income'])
                else:
                    return order_line.order_id.fiscal_position_id.map_account(account_ids['stock_output'])

            else:
                if order_line.refunded_orderline_id:
                    # print ('NO VAT --- RETURN')
                    return order_line.order_id.fiscal_position_id.map_account(account_ids['income'])
                else:
                    return order_line.order_id.fiscal_position_id.map_account(account_ids['stock_output'])


        print ('_prepare_line----- of new pos session')
        tax_ids = order_line.tax_ids_after_fiscal_position \
            .filtered(lambda t: t.company_id.id == order_line.order_id.company_id.id)
        sign = -1 if order_line.qty >= 0 else 1
        price = sign * order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
        # The 'is_refund' parameter is used to compute the tax tags. Ultimately, the tags are part
        # of the key used for summing taxes. Since the POS UI doesn't support the tags, inconsistencies
        # may arise in 'Round Globally'.
        check_refund = lambda x: x.qty * x.price_unit < 0
        is_refund = check_refund(order_line)
        tax_data = tax_ids.with_context(force_sign=sign).compute_all(price_unit=price, quantity=abs(order_line.qty),
                                                                     currency=self.currency_id, is_refund=is_refund)
        taxes = tax_data['taxes']
        # For Cash based taxes, use the account from the repartition line immediately as it has been paid already
        for tax in taxes:
            tax_rep = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
            tax['account_id'] = tax_rep.account_id.id
        date_order = order_line.order_id.date_order
        taxes = [{'date_order': date_order, **tax} for tax in taxes]
        return {
            'date_order': order_line.order_id.date_order,
            'income_account_id': get_income_account(order_line).id,
            'amount': order_line.price_subtotal,
            'taxes': taxes,
            'base_tags': tuple(tax_data['base_tags']),
        }



class pos_order(models.Model):
    _inherit = 'pos.order'

    def _prepare_invoice_vals(self):
        self.ensure_one()
        res = super(pos_order,self)._prepare_invoice_vals()
        res.update({
            'operating_unit_id': self.session_id.config_id.operating_unit_id,
        })
        return res


    def _compute_order_name(self):
        if len(self.refunded_order_ids) != 0:
            return ','.join(self.refunded_order_ids.mapped('name')) + _(' REFUND')
            # return self.session_id.config_id.refund_sequence_id._next()
        else:
            return self.session_id.config_id.sequence_id._next()

