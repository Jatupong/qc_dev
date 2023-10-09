# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits=dp.get_precision('Product Price'),
        help="Fixed amount discount.")

    @api.onchange('discount')
    def _onchange_discount_percent(self):
        # _onchange_discount method already exists in core,
        # but discount is not in the onchange definition
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange('discount_fixed')
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.constrains('discount', 'discount_fixed')
    def _check_only_one_discount(self):
        for line in self:
            if line.discount and line.discount_fixed:
                raise ValidationError(
                    _("You can only set one type of discount per line."))

    @api.depends('product_qty', 'price_unit', 'taxes_id','discount','discount_fixed')
    def _compute_amount(self):
        for line in self:
            print ('xxxxx')
            super(PurchaseOrderLine, line)._compute_amount()
            if self.discount_fixed:
                for line in self:
                    tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
                    totals = list(tax_results['totals'].values())[0]
                    amount_untaxed = totals['amount_untaxed'] - self.discount_fixed
                    amount_tax = totals['amount_tax']

                    line.update({
                        'price_subtotal': amount_untaxed,
                        'price_tax': amount_tax,
                        'price_total': (amount_untaxed + amount_tax) - self.discount_fixed,
                    })
                print("Discount Fixed",self.discount_fixed)
                print("Discount",self.discount)
            if self.discount:
                for line in self:
                    tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
                    totals = list(tax_results['totals'].values())[0]
                    amount_untaxed = totals['amount_untaxed'] -( totals['amount_untaxed']*(self.discount/100))
                    amount_tax = totals['amount_tax']

                    line.update({
                        'price_subtotal': amount_untaxed,
                        'price_tax': amount_tax,
                        'price_total': (amount_untaxed + amount_tax) - self.discount_fixed,
                    })
                print("Discount Fixed", self.discount_fixed)
                print("Discount", self.discount)
            print ('yyyyy')

            # tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            # totals = list(tax_results['totals'].values())[0]
            # amount_untaxed = totals['amount_untaxed']
            # amount_tax = totals['amount_tax']
            #
            # line.update({
            #     'price_subtotal': amount_untaxed,
            #     'price_tax': amount_tax,
            #     'price_total': amount_untaxed + amount_tax,
            # })

    # @api.depends('product_qty', 'price_unit', 'discount', 'taxes_id', 'discount_fixed')
    # def _compute_amount(self):
    #     for line in self:
    #         vals = line._prepare_compute_all_values()
    #         price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #         if line.discount_fixed > 0.0:
    #             # if self.env.user.company_id.discount_amount_condition and self.env.user.company_id.discount_amount_condition == 'unit':
    #             price -= line.discount_fixed/line.product_qty
    #         taxes = line.taxes_id.compute_all(
    #             price,
    #             vals['currency'],
    #             vals['quantity'],
    #             vals['product'],
    #             vals['partner'])
    #         line.update({
    #             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'price_total': taxes['total_included'],
    #             'price_subtotal': taxes['total_excluded'],
    #         })

    # 'price_subtotal': taxes['total_excluded'],
    def _prepare_account_move_line(self, move=False):
        vals = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        vals["discount_fixed"] = self.discount_fixed
        return vals


    def _get_discounted_price_unit(self):
        """Inheritable method for getting the unit price after applying
        discount(s).

        :rtype: float
        :return: Unit price after discount(s).
        """
        self.ensure_one()
        price_unit = super(PurchaseOrderLine,self)._get_discounted_price_unit()
        if self.discount_fixed:
            print('self.discount_fixedddddddddd:',self.discount_fixed)
            print('self.price_unit:',price_unit)
            print('aaaa:',price_unit - self.discount_fixed)
            # return price_unit - self.discount_fixed
            return round(price_unit - (self.discount_fixed / self.product_qty),2)
        return price_unit

