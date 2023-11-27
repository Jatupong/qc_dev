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


class WizardMultiCreateMo(models.TransientModel):
    _name = 'wizard.multi.create.mo'
    _description = 'Wizard multi create manufacturing order'

    def action_create_mo(self):
        manufacturing_request_custom_ids = self._context.get('active_ids', [])
        new_manufacturing_request_custom_ids = self.env['manufacturing.request.custom'].browse(manufacturing_request_custom_ids)
        print('manufacturing_request_custom_ids',manufacturing_request_custom_ids)
        print('new_manufacturing_request_custom_ids',new_manufacturing_request_custom_ids)
        if not new_manufacturing_request_custom_ids:
            raise UserError(_('Please select manufacturing request order in Approved'))
        for data in new_manufacturing_request_custom_ids:
            if data.state == 'd_manufacturing_created':
                raise UserError(_('รายการ Manufacturing Request นี้ ถูกสร้างคำสั่งผลิตเรียบร้อยแล้ว'))
            if data.state == 'a_draft':
                raise UserError(_('รายการ Manufacturing Request จะต้องถูก Approve ก่อนที่จะสร้างคำสั่งผลิตได้'))
            if data.state == 'b_confirm':
                raise UserError(_('รายการ Manufacturing Request ต้องอยู่ในสถานะ Approved เท่านั้น'))
        # print('start mr ', new_manufacturing_request_custom_ids)
        for mr in new_manufacturing_request_custom_ids:
            # print('in loop mr ', new_manufacturing_request_custom_ids)
            print('mr ', mr)
            tt_mr_ids = mr
            mr_ids = new_manufacturing_request_custom_ids.filtered(lambda x: x.custom_product_template_id == mr.custom_product_template_id and
                                                                             x.custom_bom_id == mr.custom_bom_id and
                                                                             x.custom_product_uom_id == mr.custom_product_uom_id and
                                                                             x.end_date == mr.end_date and
                                                                             x.custom_date_start_wo == mr.custom_date_start_wo and
                                                                             x.id != mr.id
                                                                   )
            tt_mr_ids |= mr_ids
            custom_product_qty = sum(tt_mr_ids.mapped('custom_product_qty'))
            print('custom_product_qty',custom_product_qty)

            mrp_vals = {
                'product_id': mr.custom_product_template_id.id,
                'product_qty': custom_product_qty,
                'product_uom_id': mr.custom_product_uom_id.id,
                'bom_id': mr.custom_bom_id.id,
                'origin': ', '.join(tt_mr_ids.mapped('number')),
                'date_deadline': mr.end_date,
                'date_planned_start': mr.custom_date_start_wo,
                # 'custom_request_id': mr.id,
            }
            print('mrp_valsmrp_vals',mrp_vals)
            # print('mrp_vals ', mrp_vals)
            new_line = self.env['mrp.production'].new(mrp_vals)
            new_line._onchange_product_id()
            new_line._compute_move_raw_ids()
            # new_line._onchange_move_raw()
            mrp_vals_dict = self.env['mrp.production']._convert_to_write({
                name: new_line[name] for name in new_line._cache
            })
            mrp_id = self.env['mrp.production'].create(mrp_vals_dict)
            for tmr in tt_mr_ids:
                tmr.custom_manufacturing_order_id = mrp_id.id
                tmr.state = 'd_manufacturing_created'
                tmr.manufacturing_date = fields.date.today()
                tmr.manufacturing_create_by = self.env.user

            new_manufacturing_request_custom_ids = new_manufacturing_request_custom_ids.filtered(lambda x: x.id not in tt_mr_ids.ids)
            if not new_manufacturing_request_custom_ids:
                break
            # print('end mr ', new_manufacturing_request_custom_ids)

        return