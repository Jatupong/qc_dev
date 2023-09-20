# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)


import base64
import xlwt
from io import BytesIO
from datetime import datetime, date
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import misc
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare, float_is_zero
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz
from datetime import datetime, timedelta, date, time

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))


class WizardStockCardReport(models.TransientModel):
    _name = 'wizard.stock.card.report'
    _description = 'Wizard Stock Card Report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    location_ids = fields.Many2many('stock.location', 'location_stock_card_ref', string='Locations')
    category_id = fields.Many2one('product.category', string='Category')
    product_ids = fields.Many2many('product.product', 'product_stock_card_ref', string='Product')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    @api.model
    def default_get(self, fields):
        res = super(WizardStockCardReport, self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year, 1, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date)})

        return res

    # @api.onchange('category_id', 'product_id')
    # def onchange_category_product_id(self):
    #     if self.category_id and self.category_id:
    #         raise UserError(_("Please, Select either Category or Product."))
    #
    #     return

    def print_report_excel(self):
        [data] = self.read()
        datas = {'form': data}

        str2d = fields.Date.from_string
        date_from = str2d(self.date_from)
        date_to = str2d(self.date_to)
        # date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        # date_to_obj = datetime.strptime(self.date_from, '%Y-%m-%d')
        report_file = "Stock" + str(date_from.strftime("%d/%m/%Y")) + "-" + str(date_to.strftime("%d/%m/%Y"))
        self.env.ref('sato_stock_card_report.stock_card_report_xls').report_file = report_file

        return self.env.ref('sato_stock_card_report.stock_card_report_xls').report_action(self, data=datas, config=False)

    def _get_product(self):
        if self.product_ids:
            product_ids = self.product_ids
        else:
            domain_product = [('type', '=', 'product')]
            if self.category_id:
                domain_product += [('categ_id', 'child_of', [self.category_id.id])]

            product_ids = self.env['product.product'].search(domain_product)

        if not product_ids:
            if self.category_id:
                raise UserError(
                    _('Cannot find any products in %s.') % (self.category_id.display_name))
            else:
                raise UserError(_('Cannot find any products.'))

        return product_ids

    def _get_location(self):
        if self.location_ids:
            location_ids = self.env['stock.location'].search([('id', 'child_of', self.location_ids.ids)])
        else:
            location_ids = self.env['stock.location'].sudo().search([('usage', 'in', ['internal'])])

        return location_ids

    def _get_stock_move_product(self, locations):
        product_ids = self._get_product()
        self._cr.execute(
            """
            SELECT move.product_id
            FROM stock_move move
            WHERE(move.location_id in %s or move.location_dest_id in %s)
                and move.state = 'done'
                and move.company_id = %s
                and move.product_id in %s
                and CAST(move.date AS date) <= %s
                and move.company_id = %s
            GROUP BY move.product_id
        """,
            (
                tuple(locations.ids),
                tuple(locations.ids),
                self.company_id.id,
                tuple(product_ids.ids),
                self.date_to,
                self.company_id.id
            ),
        )
        stock_card_results = [x[0] for x in self.env.cr.fetchall()]
        # print('stock_card_results : ', stock_card_results)
        # return self.env['product.product'].sudo().browse(31238).filtered(lambda x: x.type in ['product'])
        return self.env['product.product'].sudo().browse(stock_card_results).filtered(lambda x: x.type in ['product'])

    def _get_stock_move_results(self, date_from, date_to, locations, product_ids, company_id):
        # print('_get_stock_move_results ', date_from, date_to, locations, product_ids, company_id)
        self._cr.execute("""
            SELECT move.date, move.product_id, move_line.qty_done,
                move.product_uom, move.reference, move_line.lot_id,
                move_line.location_id, move_line.location_dest_id, move.price_unit,
                move.id as move_id, move.origin,
                case when move_line.location_dest_id in %s
                    then move_line.qty_done end as product_in,
                case when move_line.location_id in %s
                    then move_line.qty_done end as product_out,
                case when move.date < %s 
                    then True else False end as is_initial
            FROM stock_move_line move_line
            JOIN stock_move move ON move.id = move_line.move_id
            WHERE (move_line.location_id in %s or move_line.location_dest_id in %s)
                and move.state = 'done' and move.product_id in %s 
                and CAST(move.date AS date) <= %s
                and move.company_id = %s
            ORDER BY move.date, move.reference
                            """, (
            tuple(locations.ids), tuple(locations.ids), date_from,
            tuple(locations.ids), tuple(locations.ids),
            tuple(product_ids.ids), date_to, company_id.id))

        stock_card_results = self._cr.dictfetchall()
        print('stock_card_results len:', len(stock_card_results))
        for move in stock_card_results:
            # print('** move ', move)
            # print('** move_id', move['move_id'])
            # print('** product_in ', move['product_in'])
            # print('** product_out ', move['product_out'])
            # print('** reference ', move['reference'])
            # print('** location_id ', move['location_id'])
            # print('** location_dest_id ', move['location_dest_id'])
            if move['product_in'] and move['product_out']:
                move['move_in'] = True
                move['move_out'] = True
            elif move['product_in']:
                move['move_in'] = True
                move['move_out'] = False
            else:
                move['move_in'] = False
                move['move_out'] = True

        return stock_card_results

    def _get_stock_move_results_by_product(self, product, stock_move_results):
        stock_move_results_by_product = list(filter(lambda x: x['product_id'] == product.id, stock_move_results))
        # print('len stock_move_results_by_product', len(stock_move_results_by_product))
        return stock_move_results_by_product

    def _get_stock_move_initial_qty_by_product(self, stock_move_results):
        stock_move_initial_results_by_product = list(filter(lambda x: x['is_initial'] == True, stock_move_results))
        sum_in = 0
        sum_out = 0
        for move in stock_move_initial_results_by_product:
            move_id = self.env['stock.move'].browse(move['move_id'])
            if move['product_in']:
                move_in = move_id.product_uom._compute_quantity(move['product_in'], move_id.product_id.uom_id)
            else:
                move_in = 0.00

            if move['product_out']:
                move_out = move_id.product_uom._compute_quantity(move['product_out'], move_id.product_id.uom_id)
            else:
                move_out = 0.00

            sum_in += move_in or 0.00
            sum_out += move_out or 0.00
        return sum_in - sum_out

    def _get_stock_move_after_by_product(self, stock_move_results):
        stock_move_after_results_by_product = list(filter(lambda x: x['is_initial'] == False, stock_move_results))
        move_val = []
        for move in stock_move_after_results_by_product:
            move_id = self.env['stock.move'].browse(move['move_id'])
            # print('move ',move)
            # print('move_id',move_id)
            # print('product_in ',move['product_in'])
            # print('product_out ',move['product_out'])
            # print('reference ',move['reference'])
            if move['product_in'] and move['product_out']:
                move_in = True
                move_out = True
            elif move['product_in']:
                move_in = True
                move_out = False
            else:
                move_in = False
                move_out = True
            # print('move_id.picking_id:',move_id.picking_id)
            # print('move_id.picking_id:',move_id.picking_id.name)
            sale_order_id = self.env['sale.order'].search([('name', '=', move['origin'])])
            invoice_text = ""
            for sale_order in sale_order_id:
                for invoice in sale_order.invoice_ids.filtered(lambda x: x.state not in ('cancel', 'draft')):
                    # print('sale_order:', sale_order)
                    invoice_text += invoice.name + " "
            if move_id.picking_id.name and not move_id.is_inventory:
                ref = move_id.picking_id.name
            elif move_id.is_inventory:
                ref = move_id.reference
            else:
                ref = move['reference']

            if move_id.product_id.uom_id != move_id.product_uom:
                qty = move_id.product_uom._compute_quantity(move['qty_done'], move_id.product_id.uom_id)
            else:
                qty = move['qty_done']

            if move_id.picking_id and move_id.picking_id.sale_id and move_id.picking_id.sale_id.invoice_ids:
                invoice_number = move_id.picking_id.sale_id.invoice_ids[0].name
            else:
                invoice_number = ''
            if move_id.picking_id:
                customer_invoice = move_id.picking_id.note_stock
            else:
                customer_invoice = ''
            if move_id.picking_id.sale_id.invoice_ids:
                sale_number = move_id.picking_id.sale_id.invoice_ids[0].name
            else:
                sale_number = ''

            if move_id.picking_id.sale_id.order_line:
                so_number = move_id.picking_id.sale_id.order_line[0].customer_po
            else:
                so_number = ''

            orig_location = ''
            if move_id.move_orig_ids:
                orig_location = move_id.move_orig_ids[0].location_id.name

            val = {
                'move_in': move_in,
                'move_out': move_out,
                'reference': ref,
                'picking_number': move_id.picking_id.name,
                'so_number': so_number,
                'customer_invoice': customer_invoice,
                'sale_number': sale_number,
                'invoice_number': invoice_number,
                'source': move_id.origin,
                'production_number': move_id.production_id.name,
                'remark': move_id.picking_id.note or '',
                'qty': qty,
                'uom': move_id.product_id.uom_id.name,
                'no_ref': move['origin'],
                'price_unit': move['price_unit'] or 0.0,
                'price_total': move['price_unit'] or 0.0 * qty,
                'value': move['price_unit'] or 0.0 * qty,
                'lot': self.env['stock.lot'].browse(move['lot_id']).name,
                'date': move['date'],
                'orig_location': orig_location,
                'location': move_id.location_id.display_name,
                'location_dest': move_id.location_dest_id.display_name,
            }
            move_val.append(val)
            # print('move_val:', move_val)
        return move_val

    def _get_stock_move_line(self, date_from, date_to, locations, product_ids, company_id):
        domain = [('date', '>=', date_from),
                  ('date', '<=', date_to),
                  ('company_id', '=', company_id.id),
                  ('move_id.state', '=', 'done'),
                  '|',('location_dest_id', 'in', locations.ids),('location_id', 'in', locations.ids),
                  ('product_id', 'in', product_ids.ids),
                  ]
        # print('domain', domain)
        stock_move_line = self.env['stock.move.line'].search(domain, order='date')
        # print('stock_move_line', stock_move_line)
        return stock_move_line


class WizardStockCardReportXls(models.AbstractModel):
    _name = 'report.sato_stock_card_report.stock_card_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def convert_usertz_to_utc(self, date_time):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        # print('user_tz : ',user_tz)
        tz = pytz.timezone('UTC')
        date_time = user_tz.localize(date_time).astimezone(tz)
        date_time = date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        return date_time

    def generate_xlsx_report(self, workbook, data, lines):
        # print('generate_xlsx_report product_in_report_xls')
        for_left = workbook.add_format({'align': 'left'})
        for_left_border = workbook.add_format({'align': 'left', 'border': True})
        for_left_bold = workbook.add_format({'valign': 'top', 'align': 'left', 'bold': True})
        for_left_bold_border = workbook.add_format({'valign': 'top', 'align': 'left', 'bold': True, 'border': True})

        for_right = workbook.add_format({'align': 'right'})
        for_right_border = workbook.add_format({'align': 'right', 'border': True})
        for_right_bold_border = workbook.add_format({'align': 'right', 'border': True, 'bold': True})
        for_right_border_num_format = workbook.add_format({'align': 'right', 'border': True, 'num_format': '#,##0.00'})
        for_right_bold_border_num_format = workbook.add_format(
            {'align': 'right', 'border': True, 'bold': True, 'num_format': '#,##0.00'})

        for_center = workbook.add_format({'align': 'center'})
        for_center_bold = workbook.add_format({'align': 'center', 'bold': True})
        for_center_border = workbook.add_format({'align': 'center', 'border': True})
        for_center_bold_border = workbook.add_format({'valign': 'vcenter','align': 'center', 'bold': True, 'border': True})
        for_center_border_num_format = workbook.add_format({'align': 'center', 'border': True, 'num_format': '#,##0.00'})

        for_center_date = workbook.add_format({'align': 'center', 'border': True, 'num_format': 'dd/mm/yyyy'})
        for_center_datetime = workbook.add_format({'align': 'center', 'border': True, 'num_format': 'dd/mm/yyyy HH:MM'})

        # def convert_utc_to_usertz(date_time):
        #     if not date_time:
        #         return ''
        #     user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        #     tz = pytz.timezone('UTC')
        #     date_time = tz.localize(fields.Datetime.from_string(date_time)).astimezone(user_tz)
        #     date_time = date_time.strftime('%d/%m/%Y %H:%M')
        #
        #     return date_time

        str2d = fields.Date.from_string
        str2dt = fields.Datetime.from_string
        date_from = str2d(lines.date_from)
        date_to = str2d(lines.date_to)
        location_ids = lines._get_location()
        product_ids = lines._get_stock_move_product(location_ids)
        if not product_ids:
            raise UserError(_("Products haven't ever moved."))

        date_from_time = self.convert_usertz_to_utc(datetime.combine(fields.Date.from_string(lines.date_from), time.min))
        date_to_time = self.convert_usertz_to_utc(datetime.combine(fields.Date.from_string(lines.date_to), time.max))
        stock_move_line = lines._get_stock_move_line(date_from_time, date_to_time, location_ids, product_ids, lines.company_id)

        worksheet = workbook.add_worksheet('Page 1')
        i_row = 1
        worksheet.merge_range(i_row, 0, i_row, 8, lines.company_id.name, for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 8, 'Stock Card Report', for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 8, 'Report Date ' + str(fields.Date.today().strftime("%d/%m/%Y")), for_center_bold)

        if lines.category_id:
            i_row += 1
            i_col = 0
            worksheet.write(i_row, i_col, 'Category', for_left_bold)
            i_col += 1
            worksheet.write(i_row, i_col, lines.category_id.display_name, for_left)

        i_row += 1
        i_col = 0
        worksheet.write(i_row, i_col, 'From Date', for_left_bold)
        i_col += 1
        worksheet.write(i_row, i_col, strToDate(str(lines.date_from)).strftime("%d/%m/%Y"), for_left)
        i_col += 1
        worksheet.write(i_row, i_col, '-', for_center)
        i_col += 1
        worksheet.write(i_row, i_col, strToDate(str(lines.date_to)).strftime("%d/%m/%Y"), for_left)

        i_row += 1
        i_col = 0
        worksheet.write(i_row, i_col, 'Date', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Document', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Customer PO', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Supplier Invoice', for_center_bold_border)
        # i_col += 1
        # worksheet.write(i_row, i_col, 'location', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Source location - Destination Location', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Source', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Qty In', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Qty Out', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Net Balance', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Unit', for_center_bold_border)

        for product in product_ids:
            stock_move_line_by_product = stock_move_line.filtered(lambda x:x.product_id.id == product.id)

            if not stock_move_line_by_product:
                continue

            i_row += 1
            i_col = 0
            worksheet.write(i_row, i_col, str(product.default_code) or '', for_left_bold)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row, 9, str(product.name), for_left_bold)
            if lines.location_ids:
                for location in lines.location_ids:
                    child_of_location = self.env['stock.location'].search([('id', 'child_of', location.ids)])
                    stock_move_line_by_product_location = stock_move_line_by_product.filtered(
                        lambda x: x.location_id in child_of_location or x.location_dest_id in child_of_location)

                    if not stock_move_line_by_product_location:
                        continue

                    product_qties = product.with_context(location=location.id,
                                                         to_date=date_from_time).read([
                        'qty_available',
                    ])
                    last_balance_qty = product_qties[0]['qty_available']
                    move_balance = 0.0
                    i_row += 1
                    i_col = 0
                    worksheet.merge_range(i_row, i_col, i_row, 7, location.display_name, for_left_bold_border)
                    i_col += 9
                    worksheet.write(i_row, i_col, last_balance_qty, for_right_bold_border_num_format)
                    i_col += 1
                    worksheet.write(i_row, i_col, product.uom_id.display_name, for_left_border)

                    move_in = 0.0
                    move_out = 0.0
                    move_balance += last_balance_qty
                    for sml in stock_move_line_by_product_location:
                        move_id = sml.move_id
                        i_col = 0
                        i_row += 1
                        worksheet.write(i_row, i_col, sml.date or ' ', for_center_date)
                        i_col += 1
                        worksheet.write(i_row, i_col, sml.picking_id.name or '', for_left_border)
                        i_col += 1
                        if move_id.picking_id.sale_id.order_line:
                            so_number = move_id.picking_id.sale_id.order_line[0].customer_po
                        else:
                            so_number = ''
                        worksheet.write(i_row, i_col, so_number, for_left_border)
                        i_col += 1
                        if move_id.picking_id.sale_id.invoice_ids:
                            sale_number = move_id.picking_id.sale_id.invoice_ids[0].name
                        else:
                            sale_number = ''
                        if move_id.picking_id:
                            customer_invoice = move_id.picking_id.note_stock
                        else:
                            customer_invoice = ''
                        worksheet.write(i_row, i_col, sale_number or customer_invoice or '', for_left_border)
                        # i_col += 1
                        # orig_location = ''
                        # if move_id.move_orig_ids:
                        #     orig_location = move_id.move_orig_ids[0].location_id.name
                        # else:
                        #     orig_location = move_id.location_id.name
                        # worksheet.write(i_row, i_col, orig_location, for_left_border)
                        i_col += 1
                        worksheet.write(i_row, i_col, move_id.location_id.display_name + ' - ' + move_id.location_dest_id.display_name, for_left_border)
                        i_col += 1
                        if move_id.picking_id.name and not move_id.is_inventory:
                            ref = move_id.picking_id.name
                        elif move_id.is_inventory:
                            ref = move_id.reference
                        else:
                            ref = move_id.reference
                        worksheet.write(i_row, i_col, move_id.origin or ref or '', for_left_border)

                        # move in
                        if sml.location_id not in child_of_location and sml.location_dest_id in child_of_location:
                            move_in += sml.qty_done
                            move_balance += sml.qty_done
                            i_col += 1
                            worksheet.write(i_row, i_col, sml.qty_done, for_right_border_num_format)
                            i_col += 1
                            worksheet.write(i_row, i_col, '', for_right_border_num_format)
                        # move transfer
                        elif sml.location_id in child_of_location and sml.location_dest_id in child_of_location:
                            i_col += 1
                            worksheet.write(i_row, i_col, sml.qty_done, for_right_border_num_format)
                            i_col += 1
                            worksheet.write(i_row, i_col, sml.qty_done, for_right_border_num_format)
                        # move out
                        elif sml.location_id in child_of_location and sml.location_dest_id not in child_of_location:
                            move_out += sml.qty_done
                            move_balance -= sml.qty_done
                            i_col += 1
                            worksheet.write(i_row, i_col, '', for_right_border_num_format)
                            i_col += 1
                            worksheet.write(i_row, i_col, sml.qty_done, for_right_border_num_format)

                        i_col += 1
                        worksheet.write(i_row, i_col, move_balance, for_right_border_num_format)
                        i_col += 1
                        worksheet.write(i_row, i_col, '', for_left_border)

                    i_row += 1
                    i_col = 0
                    worksheet.merge_range(i_row, i_col, i_row, 6, '', for_left_border)
                    i_col += 7
                    worksheet.write(i_row, i_col, move_in, for_right_bold_border_num_format)
                    i_col += 1
                    worksheet.write(i_row, i_col, move_out, for_right_bold_border_num_format)
                    i_col += 1
                    worksheet.write(i_row, i_col, move_balance, for_right_bold_border_num_format)
                    i_col += 1
                    worksheet.write(i_row, i_col, '', for_left_border)
            else:
                for location in location_ids:
                    stock_move_line_by_product_location = stock_move_line_by_product.filtered(
                        lambda x: x.location_id in location or x.location_dest_id in location)

                    if not stock_move_line_by_product_location:
                        continue

                    product_qties = product.with_context(location=location.id,
                                                         to_date=date_from_time).read([
                        'qty_available',
                    ])
                    last_balance_qty = product_qties[0]['qty_available']
                    move_balance = 0.0
                    i_row += 1
                    i_col = 0
                    worksheet.merge_range(i_row, i_col, i_row, 7, location.display_name, for_left_bold_border)
                    i_col += 8
                    worksheet.write(i_row, i_col, last_balance_qty, for_right_bold_border_num_format)
                    i_col += 1
                    worksheet.write(i_row, i_col, product.uom_id.display_name, for_left_border)

                    move_in = 0.0
                    move_out = 0.0
                    move_balance += last_balance_qty
                    for sml in stock_move_line_by_product_location:
                        move_id = sml.move_id
                        i_col = 0
                        i_row += 1
                        worksheet.write(i_row, i_col, sml.date or ' ', for_center_date)
                        i_col += 1
                        worksheet.write(i_row, i_col, sml.picking_id.name or '', for_left_border)
                        i_col += 1
                        if move_id.picking_id.sale_id.order_line:
                            so_number = move_id.picking_id.sale_id.order_line[0].customer_po
                        else:
                            so_number = ''
                        worksheet.write(i_row, i_col, so_number, for_left_border)
                        i_col += 1
                        if move_id.picking_id.sale_id.invoice_ids:
                            sale_number = move_id.picking_id.sale_id.invoice_ids[0].name
                        else:
                            sale_number = ''
                        if move_id.picking_id:
                            customer_invoice = move_id.picking_id.note_stock
                        else:
                            customer_invoice = ''
                        worksheet.write(i_row, i_col, sale_number or customer_invoice or '', for_left_border)
                        # i_col += 1
                        # orig_location = ''
                        # if move_id.move_orig_ids:
                        #     orig_location = move_id.move_orig_ids[0].location_id.name
                        # else:
                        #     orig_location = move_id.location_id.name
                        # worksheet.write(i_row, i_col, orig_location, for_left_border)
                        i_col += 1
                        worksheet.write(i_row, i_col,
                                        move_id.location_id.display_name + ' - ' + move_id.location_dest_id.display_name,
                                        for_left_border)
                        i_col += 1
                        if move_id.picking_id.name and not move_id.is_inventory:
                            ref = move_id.picking_id.name
                        elif move_id.is_inventory:
                            ref = move_id.reference
                        else:
                            ref = move_id.reference
                        worksheet.write(i_row, i_col, move_id.origin or ref or '', for_left_border)

                        # move in
                        if sml.location_id not in location and sml.location_dest_id in location:
                            move_in += sml.qty_done
                            move_balance += sml.qty_done
                            i_col += 1
                            worksheet.write(i_row, i_col, sml.qty_done, for_right_border_num_format)
                            i_col += 1
                            worksheet.write(i_row, i_col, '', for_right_border_num_format)
                        # move transfer
                        elif sml.location_id in location and sml.location_dest_id in location:
                            i_col += 1
                            worksheet.write(i_row, i_col, sml.qty_done, for_right_border_num_format)
                            i_col += 1
                            worksheet.write(i_row, i_col, sml.qty_done, for_right_border_num_format)
                        # move out
                        elif sml.location_id in location and sml.location_dest_id not in location:
                            move_out += sml.qty_done
                            move_balance -= sml.qty_done
                            i_col += 1
                            worksheet.write(i_row, i_col, '', for_right_border_num_format)
                            i_col += 1
                            worksheet.write(i_row, i_col, sml.qty_done, for_right_border_num_format)

                        i_col += 1
                        worksheet.write(i_row, i_col, move_balance, for_right_border_num_format)
                        i_col += 1
                        worksheet.write(i_row, i_col, '', for_left_border)

                    i_row += 1
                    i_col = 0
                    worksheet.merge_range(i_row, i_col, i_row, 5, '', for_left_border)
                    i_col += 6
                    worksheet.write(i_row, i_col, move_in, for_right_bold_border_num_format)
                    i_col += 1
                    worksheet.write(i_row, i_col, move_out, for_right_bold_border_num_format)
                    i_col += 1
                    worksheet.write(i_row, i_col, move_balance, for_right_bold_border_num_format)
                    i_col += 1
                    worksheet.write(i_row, i_col, '', for_left_border)

        workbook.close()

        # for product in product_ids:
        #     move_balance = 0.0
        #     stock_move_results_by_product = lines._get_stock_move_results_by_product(product, stock_move_results)
        #     last_balance_qty = lines._get_stock_move_initial_qty_by_product(stock_move_results_by_product)
        #     move_after = lines._get_stock_move_after_by_product(stock_move_results_by_product)
        #
        #     if not last_balance_qty and not move_after:
        #         continue
        #
        #     i_row += 1
        #     i_col = 0
        #     worksheet.merge_range(i_row, i_col, i_row, 7, 'สินค้า :' + str(product.display_name), for_left_bold_border)
        #     i_col += 9
        #     worksheet.write(i_row, i_col, last_balance_qty, for_right_bold_border_num_format)
        #     i_col += 1
        #     worksheet.write(i_row, i_col, product.uom_id.display_name, for_left_border)
        #
        #     move_balance += last_balance_qty
        #     move_in = 0.0
        #     move_out = 0.0
        #     for move in move_after:
        #         i_col = 0
        #         i_row += 1
        #         worksheet.write(i_row, i_col, move['date'] or ' ', for_center_date)
        #         i_col += 1
        #         worksheet.write(i_row, i_col, move['picking_number'] or '', for_left_border)
        #         i_col += 1
        #         worksheet.write(i_row, i_col, move['so_number'] or '', for_left_border)
        #         i_col += 1
        #         if move['sale_number']:
        #             worksheet.write(i_row, i_col, move['sale_number'] or '', for_left_border)
        #         else:
        #             worksheet.write(i_row, i_col, move['customer_invoice'] or '', for_left_border)
        #         i_col += 1
        #         worksheet.write(i_row, i_col, move['orig_location'], for_left_border)
        #         i_col += 1
        #         worksheet.write(i_row, i_col, move['location'] + ' - ' + move['location_dest'], for_left_border)
        #         i_col += 1
        #         worksheet.write(i_row, i_col, move['source'] or move['reference'] or '', for_left_border)
        #         if move['move_in'] and not move['move_out']:
        #             # move in
        #             move_in = move_in + move['qty']
        #             move_balance = move_balance + move['qty']
        #             i_col += 1
        #             worksheet.write(i_row, i_col, move['qty'] or '', for_right_border_num_format)
        #             i_col += 1
        #             worksheet.write(i_row, i_col, '', for_right_border_num_format)
        #         elif move['move_in'] and move['move_out']:
        #             # move transfer
        #             i_col += 1
        #             worksheet.write(i_row, i_col, move['qty'] or '', for_right_border_num_format)
        #             i_col += 1
        #             worksheet.write(i_row, i_col, move['qty'] or '', for_right_border_num_format)
        #         elif not move['move_in'] and move['move_out']:
        #             # move out
        #             move_out = move_out + move['qty']
        #             move_balance = move_balance - move['qty']
        #             i_col += 1
        #             worksheet.write(i_row, i_col, '', for_right_border_num_format)
        #             i_col += 1
        #             worksheet.write(i_row, i_col, move['qty'] or 'out', for_right_border_num_format)
        #         i_col += 1
        #         worksheet.write(i_row, i_col, move_balance, for_right_border_num_format)
        #         i_col += 1
        #         worksheet.write(i_row, i_col, '', for_left_border)
        #
        #     i_row += 1
        #     i_col = 0
        #     worksheet.merge_range(i_row, i_col, i_row, 4, '', for_left_border)
        #     i_col += 7
        #     worksheet.write(i_row, i_col, move_in, for_right_bold_border_num_format)
        #     i_col += 1
        #     worksheet.write(i_row, i_col, move_out, for_right_bold_border_num_format)
        #     i_col += 1
        #     worksheet.write(i_row, i_col, move_balance, for_right_bold_border_num_format)
        #     i_col += 1
        #     worksheet.write(i_row, i_col, '', for_left_border)

        # workbook.close()