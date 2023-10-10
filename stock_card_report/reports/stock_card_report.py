# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockCardView(models.TransientModel):
    _name = "stock.card.view"
    _description = "Stock Card View"
    _order = "date"

    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name="product.product")
    product_qty = fields.Float()
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom")
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    is_initial = fields.Boolean()
    product_in = fields.Float()
    amount_in = fields.Float()
    product_out = fields.Float()
    amount_out = fields.Float()
    lot_id = fields.Many2one('stock.lot', string='Lot')
    move_line_id = fields.Char()

class StockCardReport(models.TransientModel):
    _name = "report.stock.card.report"
    _description = "Stock Card Report"

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()
    product_ids = fields.Many2many(comodel_name="product.product")
    location_id = fields.Many2one(comodel_name="stock.location")

    # Data fields, used to browse report data
    results = fields.Many2many(
        comodel_name="stock.card.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing store in database",
    )

    #stock.move
    # def _compute_results(self):
    #     self.ensure_one()
    #     date_from = self.date_from or "0001-01-01"
    #     self.date_to = self.date_to or fields.Date.context_today(self)
    #     locations = self.env["stock.location"].search(
    #         [("id", "child_of", [self.location_id.id])]
    #     )
    #     self._cr.execute(
    #         """
    #         SELECT move.date, move.product_id, move.product_qty,
    #             move.product_uom_qty, move.product_uom, move.reference,
    #             move.location_id, move.location_dest_id,
    #             case when move.location_dest_id in %s and move.location_id in %s
    #                 then move.product_qty end as product_int,
    #             case when move.location_dest_id in %s
    #                 then move.product_qty end as product_in,
    #             case when move.location_id in %s
    #                 then move.product_qty end as product_out,
    #             case when move.date < %s then True else False end as is_initial
    #         FROM stock_move move
    #         WHERE (move.location_id in %s or move.location_dest_id in %s)
    #             and move.state = 'done' and move.product_id in %s
    #             and CAST(move.date AS date) <= %s
    #         ORDER BY move.date, move.reference
    #     """,
    #         (
    #             tuple(locations.ids),
    #             tuple(locations.ids),
    #             tuple(locations.ids),
    #             tuple(locations.ids),
    #             date_from,
    #             tuple(locations.ids),
    #             tuple(locations.ids),
    #             tuple(self.product_ids.ids),
    #             self.date_to,
    #         ),
    #     )
    #     stock_card_results = self._cr.dictfetchall()
    #     ReportLine = self.env["stock.card.view"]
    #     self.results = [ReportLine.new(line).id for line in stock_card_results]

    #stock.move.line
    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from or "0001-01-01"
        self.date_to = self.date_to or fields.Date.context_today(self)
        locations = self.env["stock.location"].search(
            [("id", "child_of", [self.location_id.id])]
        )
        self._cr.execute(
            """
            SELECT move.date,
                move.product_id,
                move.qty_done as product_qty,
                move.product_uom_id as product_uom,
                move.reference,
                move.location_id,
                move.location_dest_id,
                move.lot_id,move.id as move_line_id,
                case when move.location_dest_id in %s
                    then move.qty_done end as product_in,
                case when move.location_id in %s
                    then move.qty_done end as product_out,
                case when move.date < %s then True else False end as is_initial
            FROM stock_move_line move
            WHERE (move.location_id in %s or move.location_dest_id in %s)
                and move.state = 'done' and move.product_id in %s
                and CAST(move.date AS date) <= %s
            ORDER BY move.date, move.reference
        """,
            (

                tuple(locations.ids),
                tuple(locations.ids),
                date_from,
                tuple(locations.ids),
                tuple(locations.ids),
                tuple(self.product_ids.ids),
                self.date_to,
            ),
        )
        stock_card_results = self._cr.dictfetchall()
        print('stock_card_results:',stock_card_results)
        ReportLine = self.env["stock.card.view"]
        for line in stock_card_results:
            if line["lot_id"]:
                lot = self.env['stock.lot'].sudo().search([('id', '=',line["lot_id"])],)
                line["lot_id"] = lot
        for line in stock_card_results:
            print(line)
        self.results = [ReportLine.new(line).id for line in stock_card_results]
        print(self.results)

    def _get_initial(self, product_line):
        try:
            print('_get_initial:')
            print('product_line:',product_line)
            product_input_qty = sum(product_line.mapped("product_in"))
            product_output_qty = sum(product_line.mapped("product_out"))
            print('product_input_qty:', product_input_qty)
            print('product_output_qty:',product_output_qty)
            return product_input_qty - product_output_qty
        except:
            return 0

    def print_report(self, report_type="qweb"):
        self.ensure_one()
        action = (
            report_type == "xlsx"
            and self.env.ref("stock_card_report.action_stock_card_report_xlsx")
            or self.env.ref("stock_card_report.action_stock_card_report_pdf")
        )
        return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref(
                "stock_card_report.report_stock_card_report_html"
            ).render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()
