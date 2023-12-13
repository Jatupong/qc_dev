# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, models,fields
from odoo.tools import float_compare
import base64

class PosOrder(models.Model):
    _inherit = 'pos.order'


    def confirm_coupon_programs(self, coupon_data):
        """
        This is called after the order is created.

        This will create all necessary coupons and link them to their line orders etc..

        It will also return the points of all concerned coupons to be updated in the cache.
        """
        print('confirm_coupon_programs_POS')
        # Keys are stringified when using rpc
        coupon_data = {int(k): v for k, v in coupon_data.items()}
        # Map negative id to newly created ids.
        coupon_new_id_map = {k: k for k in coupon_data.keys() if k > 0}

        # Create the coupons that were awarded by the order.
        coupons_to_create = {k: v for k, v in coupon_data.items() if k < 0 and not v.get('giftCardId')}

        coupon_create_vals = [{
            'program_id': p['program_id'],
            'partner_id': p.get('partner_id', False) or self.partner_id.id,
            'code': p.get('barcode') or self.env['loyalty.card']._generate_code(),
            'points': 0,
            'source_pos_order_id': self.id,
        } for p in coupons_to_create.values()]

        # Pos users don't have the create permission
        new_coupons = self.env['loyalty.card'].with_context(action_no_send_mail=True).sudo().create(coupon_create_vals)
        # We update the gift card that we sold when the gift_card_settings = 'scan_use'.
        gift_cards_to_update = [v for v in coupon_data.values() if v.get('giftCardId')]
        updated_gift_cards = self.env['loyalty.card']
        for coupon_vals in gift_cards_to_update:
            gift_card = self.env['loyalty.card'].browse(coupon_vals.get('giftCardId'))
            gift_card.write({
                'points': coupon_vals['points'],
                'source_pos_order_id': self.id,
                'partner_id': coupon_vals.get('partner_id', False),
            })
            updated_gift_cards |= gift_card

        # Map the newly created coupons
        for old_id, new_id in zip(coupons_to_create.keys(), new_coupons):
            coupon_new_id_map[new_id.id] = old_id

        all_coupons = self.env['loyalty.card'].browse(coupon_new_id_map.keys()).exists()
        lines_per_reward_code = defaultdict(lambda: self.env['pos.order.line'])
        for line in self.lines:
            if not line.reward_identifier_code:
                continue
            lines_per_reward_code[line.reward_identifier_code] |= line
        print('all_coupons:',all_coupons)
        for coupon in all_coupons:
            if coupon.id in coupon_new_id_map:
                # Coupon existed previously, update amount of points.
                loyalty_program_id = self.env['loyalty.program'].browse(coupon_data[coupon_new_id_map[coupon.id]]['program_id'])
                if loyalty_program_id and loyalty_program_id.program_type == 'gift_card' and  loyalty_program_id.gift_card_value and coupon_data[coupon_new_id_map[coupon.id]]['points'] > 0:
                    coupon.points = loyalty_program_id.gift_card_value
                    coupon.base_points = loyalty_program_id.gift_card_value
                else:
                    if coupon.program_id.program_type == 'gift_card':
                        coupon.points += coupon_data[coupon_new_id_map[coupon.id]]['points']
                        date_order = coupon.create_date.date()
                        vals={
                            'date_order':fields.Date.today(),
                            'date':date_order,
                            'qty':coupon.base_points,
                            'qty_done':abs(coupon_data[coupon_new_id_map[coupon.id]]['points']),
                            'ref':self.name,
                            'program_id':coupon.program_id.id,
                            'pos_order':self.id,
                            'partner_id':coupon.partner_id.id,

                        }
                        self.env['loyalty.program.line'].create(vals)
                        coupon.base_points -= abs(coupon_data[coupon_new_id_map[coupon.id]]['points'])







                if loyalty_program_id and loyalty_program_id.valid_date:
                    coupon.expiration_date = loyalty_program_id.valid_date

                if loyalty_program_id and loyalty_program_id.coupon_date:
                    date = datetime.now().date() + relativedelta(days=loyalty_program_id.coupon_date)
                    coupon.expiration_date = date

            for reward_code in coupon_data[coupon_new_id_map[coupon.id]].get('line_codes', []):
                lines_per_reward_code[reward_code].coupon_id = coupon
        # Send creation email
        new_coupons.with_context(action_no_send_mail=False)._send_creation_communication()
        # Reports per program
        report_per_program = {}
        coupon_per_report = defaultdict(list)
        # Important to include the updated gift cards so that it can be printed. Check coupon_report.
        for coupon in new_coupons | updated_gift_cards:
            if coupon.program_id not in report_per_program:
                report_per_program[coupon.program_id] = coupon.program_id.communication_plan_ids.\
                    filtered(lambda c: c.trigger == 'create').pos_report_print_id
            for report in report_per_program[coupon.program_id]:
                coupon_per_report[report.id].append(coupon.id)
        return {
            'coupon_updates': [{
                'old_id': coupon_new_id_map[coupon.id],
                'id': coupon.id,
                'points': coupon.points,
                'code': coupon.code,
                'program_id': coupon.program_id.id,
                'partner_id': coupon.partner_id.id,
            } for coupon in all_coupons if coupon.program_id.is_nominative],
            'program_updates': [{
                'program_id': program.id,
                'usages': program.total_order_count,
            } for program in all_coupons.program_id],
            'new_coupon_info': [{
                'program_name': coupon.program_id.name,
                'expiration_date': coupon.expiration_date,
                'code': coupon.code,
            } for coupon in new_coupons if (
                coupon.program_id.applies_on == 'future'
                # Don't send the coupon code for the gift card and ewallet programs.
                # It should not be printed in the ticket.
                and coupon.program_id.program_type not in ['gift_card', 'ewallet']
            )],
            'coupon_report': coupon_per_report,
        }
