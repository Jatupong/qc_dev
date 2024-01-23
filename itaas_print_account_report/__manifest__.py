# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)
# 13.0.3.7 แก้สมุดรายวันทุกใบ ข้อมูลเรียงตาม หน้าโปรแกรม และ partner ดึงจากระดับไลน์อันแรก
{
    'name' : 'Print Report General Account',
    'version' : '15.0.0.2',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Quotations',
    'summary' : 'Print Report Account',
    'description': """
                Print Report General Account:
                    - Print Report General Account
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['sale','base','account','purchase','account_accountant'],
    'data' : ['report/report_reg.xml',
              'report/debitcredit_report01_inherit.xml',
              'report/debitcredit_report02_inherit.xml',
              'report/debitcredit_report03_inherit.xml',
              'report/debitcredit_report04_inherit.xml',
              'report/debitcredit_report05_inherit.xml',

              'report/debitcredit_receipt_voucher.xml',
              'report/debitcredit_general_voucher.xml',

              'report/debitcredit_account_receivable_voucher.xml',
              'report/debitcredit_payment_report.xml',
              'report/debitcredit_payment_voucher.xml',


              # 'views/view_account_vat.xml',
              # 'views/account_move_view.xml',
              # 'views/credit.xml',

              'sequence.xml',
              ],


    #'report/productvariant_report.xml'],
    'installable' : True,
    'application' : False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
