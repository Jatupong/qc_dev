# Copyright 2019 Elico Corp, Dominique K. <dominique.k@elico-corp.com.sg>
# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Add Field Purchase",
    "version": "15.0.1.0.0",
    "summary": " ",
    "author": "Elico Corp, Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "license": "AGPL-3",
    'depends': ['purchase', 'itaas_company_detail_address', 'itaas_partner_detail_address',
                'itaas_contact_person', 'itaas_image_signature','base'],
    "data": [
        # "security/ir.model.access.csv",
        # "wizard/purchase_make_invoice_advance_views.xml",
        # "views/res_config_settings_views.xml",
        # "views/purchase_add_field_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
