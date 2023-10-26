# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models, _

class ReceiptDesign(models.Model):
    _name = "receipt.design"
    _rec_name = "name"

    name = fields.Char(string="Name")
    receipt_design = fields.Text(string='Description', required=True)

    @api.model
    def _create_receipt_design_1(self):
        record_data = {}
        record_data['name'] = "Receipt Design 1"
        record_data['receipt_design'] = """ 
        <div class="pos-receipt">
            <div style="font-size: 80%; text-align:center;">
                <div><span t-esc='receipt.date.localestring'/>  <span t-esc='receipt.name'/></div>
            </div>
            <br/>
            <t t-if='receipt.company.logo'>
                <img style="width: 30%;display: block;margin: auto;" t-att-src='receipt.company.logo' alt="Logo"/>
                <br/>
            </t>
            <div style="font-size: 80%; text-align:center;">
                <t t-if='!receipt.company.logo'>
                    <h2 class="pos-receipt-center-align">
                        <t t-esc='receipt.company.name' />
                    </h2>
                </t>
                <t t-if='receipt.company.contact_address'>
                    <div><t t-esc='receipt.company.contact_address' /></div>
                </t>
                <t t-if='receipt.company.phone'>
                    <div>Tel:<t t-esc='receipt.company.phone' /></div>
                </t>
                <t t-if='receipt.company.website'>
                    <div><t t-esc='receipt.company.website' /></div>
                </t>
                <t t-if='receipt.header_html'>
                    <t t-raw='receipt.header_html' />
                </t>
                <t t-if='!receipt.header_html and receipt.header'>
                    <div><t t-esc='receipt.header' /></div>
                </t>
                <br/>
            </div>
            <br />
            <!-- Orderlines -->
            <div class='orderlines'>
                <div style="text-align:center; font-size: 75%; border-top: 1px dashed black;border-bottom: 1px dashed black;padding-top: 5px;padding-bottom: 5px;">
                    <div>Receipt : <span t-esc='receipt.name' /></div>
                    <br/>
                    <div>Date : 
                        <t t-if="order.formatted_validation_date">
                          <span t-esc='order.formatted_validation_date' />
                        </t>
                        <t t-else="">
                            <span t-esc='order.validation_date' />
                        </t>
                    </div>
                    <br/>
                    <t t-if='receipt.client'>
                        <div>Client : <t t-esc='receipt.client.name' /></div>
                        <br/>
                    </t>
                    <t t-if='receipt.cashier'>
                    <div class='cashier'>
                        <div>Served by <t t-esc='receipt.cashier' /></div>
                    </div>
                    </t>
                    
                    </div>
                    <br/>
                    <br/>
                    <table style="width: 100%;">
                        <tr style="border-bottom: 2px solid black;font-size:15px;">
                        <th style="text-align:left;">Product</th>
                        <th>Qty</th>
                        <th style="text-align: center;">Unit Price</th>
                        <th>Amount</th>
                        </tr>
                        <tr t-foreach="receipt.orderlines" t-as="line" style="border-bottom: 1px solid #ddd;font-size: 16px;font-family: initial;">
                        <td><div style="padding-top: 10px;padding-bottom: 10px;">
                            <span t-esc='line.product_name_wrapped[0]'/>
                            <t t-if='line.discount !== 0'>
                                <h5 style="margin-top: 0%;margin-bottom: 0%;font-size: 12px;color: #848484;">
                                    <t t-esc='line.discount' />% Discount 
                                </h5>
                            </t>
                            <t t-if="line.customer_note">
                              <div style="font-size: 13px;" t-esc="line.customer_note"/>
                            </t>
                            </div>
                        </td>
                        <td style="text-align: center;"><span t-esc="line.quantity"/><span t-if='line.unit_name !== "Units"' t-esc='line.unit_name'/></td>
                        <td style="text-align: center;"><span t-esc="widget.pos.format_currency_no_symbol(line.price)"/></td>
                        <td style="text-align: center;"><span t-esc='widget.pos.format_currency_no_symbol(line.price_display)'/></td>
                        </tr>
                    </table>
                </div>
            <div>
            <!-- Subtotal -->
            <t t-set='taxincluded' t-value='Math.abs(receipt.subtotal - receipt.total_with_tax) &lt;= 0.000001' />
            <t t-if='!taxincluded'>
                <br/> 
                <div style="font-weight: 700;text-align: right; font-size: 20px;border-top: 2px solid;margin-left: 30%; padding-top: 2%;">Subtotal : <span t-esc='widget.pos.format_currency(receipt.subtotal)' class="pos-receipt-right-align"/></div>
                <t t-foreach='receipt.tax_details' t-as='tax'>
                    <div style="font-weight: 700;text-align: right;">
                        <t t-esc='tax.name' />
                        <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)' class="pos-receipt-right-align"/>
                    </div>
                </t>
            </t>
            <!-- Total -->
            <br/>
            <div style="font-size: 20px;text-align: right;font-weight: 700; border-top: 2px solid;margin-left: 30%;padding-top: 2%;">
                TOTAL :
                <span t-esc='widget.pos.format_currency(receipt.total_with_tax)'/>
            </div>
            <br/>
            <!-- Extra Payment Info -->
            <t t-if='receipt.total_discount'>
                <div style="font-size: 14px;text-align: right;border-top: 1px solid;margin-left: 30%;padding-top: 2%;">
                    Discounts
                    <span t-esc='widget.pos.format_currency(receipt.total_discount)'/>
                </div>
            </t>
            <br/>
            <t t-if='taxincluded'>
                <t t-foreach='receipt.tax_details' t-as='tax'>
                    <div style="font-size: 15px; text-align: right; font-weight: 700; border-top: 1px solid;margin-left: 30%;padding-top: 2%;">
                        <t t-esc='tax.name' />
                        <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)'/>
                    </div>
                </t>
                <div style="font-size: 15px; text-align: right; font-weight: 700;">
                    Total Taxes :
                    <span t-esc='widget.pos.format_currency(receipt.total_tax)'/>
                </div>
            </t>
            </div>
            <br/>
            <br/>
            <div style="border-top: 1px dashed black;padding-top: 5%;border-bottom: 1px dashed black;">
                <!-- Payment Lines -->
                <t t-foreach='paymentlines' t-as='line'>
                    <div style="font-size: 14px;">
                        <t t-esc='line.name' />
                        <span t-esc='widget.pos.format_currency_no_symbol(line.get_amount())' class="pos-receipt-right-align"/>
                    </div>
                </t>
                <br/>
                <div class="receipt-change" style="font-size: 14px;">
                    CHANGE
                    <span t-esc='widget.pos.format_currency(receipt.change)' class="pos-receipt-right-align"/>
                </div>
                <br/>
            </div>
            <div class='before-footer' />
            <!-- Footer -->
            <div t-if='receipt.footer_html'  class="pos-receipt-center-align" style="font-size: 14px;">
                <t t-raw='receipt.footer_html'/>
            </div>
            <div t-if='!receipt.footer_html and receipt.footer'  class="pos-receipt-center-align" style="font-size: 13px;">
                <br/>
                <t t-esc='receipt.footer'/>
                <br/>
                <br/>
            </div>
            <div class='after-footer' style="font-size: 14px;">
                <t t-foreach='paymentlines' t-as='line'>
                    <t t-if='line.ticket'>
                        <br />
                        <div class="pos-payment-terminal-receipt">
                            <t t-raw='line.ticket'/>
                        </div>
                    </t>
                </t>
            </div>
            <br/>
            <div style="text-align:center;">
                Thank You. Please Visit Again !!
            </div>
        </div>"""
        record_id = self.create(record_data)
        pos_config_id = self.env.ref('point_of_sale.pos_config_main')
        if record_id and pos_config_id:
            pos_config_id.use_custom_receipt = True
            pos_config_id.receipt_design_id = record_id.id

    @api.model
    def _create_receipt_design_2(self):
        record_data = {}
        record_data['name'] = "Receipt Design 2"
        record_data['receipt_design'] = """ 
        <div class="pos-receipt" style="font-family: monospace;">
            <div class="pos-center-align" style="font-size: 12px;">
                <t t-if="order.formatted_validation_date">
                    <t t-esc="order.formatted_validation_date"/>
                </t>
                <t t-else="">
                    <t t-esc="order.validation_date"/>
                </t> 
                <br/><t t-esc="order.name"/></div>
            <br />
            <t t-esc="widget.pos.company.name"/><br />
            <div style="font-size:13px">
                Phone: <t t-esc="widget.pos.company.phone || ''"/><br />
            </div>
            <div style="font-size:13px">
                User: <t t-esc="widget.pos.cashier ? widget.pos.cashier.name : widget.pos.user.name"/><br />
            </div>
            <br />
            <t t-if="receipt.header">
                <div style='text-align:center; font-size:13px'>
                    <t t-esc="receipt.header" />
                </div>
                <br />
            </t>
            <table class='receipt-orderlines' style="font-size:13px;">
                <colgroup>
                    <col width='45%' />
                    <col width='25%' />
                    <col width='30%' />
                </colgroup>
                <tr t-foreach="orderlines" t-as="orderline">
                    <td><div style="padding-top: 5px;padding-bottom: 5px;">
                          <t t-esc="orderline.get_product().display_name"/>
                           <t t-if="orderline.get_discount() > 0">
                              <div style="font-size: 12px;font-style: italic;color: #808080;">
                                  <t t-esc="orderline.get_discount()"/>% discount
                              </div>
                          </t>
                            <t t-if="orderline.customerNote">
                                <div style="font-size: 12px;" t-esc="orderline.customerNote"/>
                            </t>
                        </div>
                    </td>
                    <td class="pos-right-align">
                        <div>
                          <t t-esc="orderline.get_quantity_str_with_unit()"/>
                        </div>
                    </td>
                    <td class="pos-right-align">
                        <div>
                          <t t-esc="widget.pos.format_currency(orderline.get_display_price())"/>
                        </div>
                    </td>
                </tr>
            </table>
            <br />
            <!-- Subtotal -->
            <t t-set='taxincluded' t-value='Math.abs(receipt.subtotal - receipt.total_with_tax) &lt;= 0.000001' />
            <t t-if='!taxincluded'>
                <br/>
                <div style="font-weight: 700; font-size: 14px;">Subtotal<span t-esc='widget.pos.format_currency(receipt.subtotal)' class="pos-receipt-right-align"/></div>
                <t t-foreach='receipt.tax_details' t-as='tax'>
                    <div style="font-weight: 700; font-size: 14px;">
                        <t t-esc='tax.name' />
                        <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)' class="pos-receipt-right-align"/>
                    </div>
                </t>
            </t>
            <!-- Total -->
            <br/>
            <div style="font-weight: 700; font-size: 14px;">
                TOTAL
                <span t-esc='widget.pos.format_currency(receipt.total_with_tax)' class="pos-receipt-right-align"/>
            </div>
            <br/><br/>
            <!-- Payment Lines -->
            <t t-foreach='paymentlines' t-as='line'>
                <div style="font-size: 14px;">
                    <t t-esc='line.name' />
                    <span t-esc='widget.pos.format_currency_no_symbol(line.get_amount())' class="pos-receipt-right-align"/>
                </div>
            </t>
            <br/>
            <div class="receipt-change" style="font-size: 14px;">
                CHANGE
                <span t-esc='widget.pos.format_currency(receipt.change)' class="pos-receipt-right-align"/>
            </div>
            <br/>
            <!-- Extra Payment Info -->
            <t t-if='receipt.total_discount'>
                <div style="font-size: 14px;">
                    Discounts
                    <span t-esc='widget.pos.format_currency(receipt.total_discount)' class="pos-receipt-right-align"/>
                </div>
            </t>
            <t t-if='taxincluded'>
                <t t-foreach='receipt.tax_details' t-as='tax'>
                    <div style="font-size: 14px;">
                        <t t-esc='tax.name' />
                        <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)' class="pos-receipt-right-align"/>
                    </div>
                </t>
                <div style="font-size: 14px;">
                    Total Taxes
                    <span t-esc='widget.pos.format_currency(receipt.total_tax)' class="pos-receipt-right-align"/>
                </div>
            </t>
            <div class='before-footer' />
            <!-- Footer -->
            <div t-if='receipt.footer_html' style="text-align: center; font-size: 14px;">
                <t t-raw='receipt.footer_html'/>
            </div>
            <div t-if='!receipt.footer_html and receipt.footer' style="text-align: center;font-size: 14px;">
                <br/>
                <t t-esc='receipt.footer'/>
                <br/><br/>
            </div>
            <div class='after-footer' style="font-size: 14px;">
                <t t-foreach='paymentlines' t-as='line'>
                    <t t-if='line.ticket'>
                        <br />
                        <div class="pos-payment-terminal-receipt">
                            <t t-raw='line.ticket'/>
                        </div>
                    </t>
                </t>
            </div>   
            <br/><br/>   
            <div style="text-align:center;border-top: 2px dotted black;padding-top: 15px;">
                <t t-if='receipt.cashier'>
                    <div class='cashier' style="text-align:center;">
                        <div>Served by <t t-esc='receipt.cashier' /></div>
                    </div>
                </t>
                <br/>
                Thank You. Please Visit Again !!
            </div>
        </div>"""
        self.create(record_data)

    @api.model
    def _create_receipt_design_3(self):
        record_data = {}
        record_data['name'] = "Receipt Design 3"
        record_data['receipt_design'] = """ 
        <div class="pos-receipt">
            <t t-esc="widget.pos.company.name"/><br />
            <div style="font-size:13px">
                Phone: <t t-esc="widget.pos.company.phone || ''"/><br />
            </div>
            <div style="font-size:13px">
                User : <t t-esc="widget.pos.cashier ? widget.pos.cashier.name : widget.pos.user.name"/><br />
            </div>
            <br/>
            <div style="font-size:13px">
                Date : 
                <t t-if="order.formatted_validation_date">
                    <t t-esc="order.formatted_validation_date"/>
                </t>
                <t t-else="">
                    <t t-esc="order.validation_date"/>
                </t>
                <br />
            </div>
            <div style="font-size:13px">
                Order : <t t-esc="order.name"/><br />
            </div>
            <br />
            <div style="font-size:13px">
                Cashier :  <t t-esc='receipt.cashier' /><br />
            </div>
            <br/>
            <t t-if="receipt.header">
                <div style='text-align:center; font-size:13px'>
                    <t t-esc="receipt.header" />
                </div>
                <br />
            </t>
            <div>
                <table class='receipt-orderlines' style="font-size:15px; border-style: double;
            border-left: none;border-right: none;border-bottom: none;width: 100%;">
                <colgroup>
                    <col width='40%' />
                    <col width='30%' />
                    <col width='30%' />
                </colgroup>
                <tr style="border-bottom: 1px dashed black;">
                    <th style="text-align:left;">Product</th>
                    <th style="text-align:center;">Qty</th>
                    <th style="text-align:center;">Amount</th>
                </tr>
                <tr t-foreach="orderlines" t-as="orderline">
                    <td style="padding-top: 1%;padding-bottom: 1%;">
                        <t t-esc="orderline.get_product().display_name"/>
                        <t t-if="orderline.get_discount() > 0">
                            <div style="font-size: 12px;font-style: italic;color: #808080;">
                                <t t-esc="orderline.get_discount()"/>% discount
                            </div>
                        </t>
                        <t t-if="orderline.customerNote">
                            <div style="font-size: 14px;" t-esc="orderline.customerNote"/>
                        </t>
                    </td>
                    <td class="pos-center-align">
                        <t t-esc="orderline.get_quantity_str_with_unit()"/>
                    </td>
                    <td class="pos-center-align">
                        <t t-esc="widget.pos.format_currency(orderline.get_display_price())"/>
                    </td>
                </tr>
                </table>
            </div>
            <br />
            <div style="padding-top: 6px;">
                <!-- Subtotal -->
                <t t-set='taxincluded' t-value='Math.abs(receipt.subtotal - receipt.total_with_tax) &lt;= 0.000001' />
                <t t-if='!taxincluded'>
                    <br/>
                    <div style="font-weight: 700; font-size: 14px; border-top:1px dashed;"><span style="margin-left: 40%;">Subtotal : </span><span t-esc='widget.pos.format_currency(receipt.subtotal)' class="pos-receipt-right-align"/></div>
                    <t t-foreach='receipt.tax_details' t-as='tax'>
                        <div style="font-weight: 700; font-size: 14px;">
                            <span style="margin-left: 40%;"><t t-esc='tax.name' /></span>
                            <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)' class="pos-receipt-right-align"/>
                        </div>
                    </t>
                </t>
                <!-- Total -->
                <br/>
                <div style="font-weight: 700; font-size: 14px;">
                    <span style="margin-left: 40%;">TOTAL : </span>
                    <span t-esc='widget.pos.format_currency(receipt.total_with_tax)' class="pos-receipt-right-align"/>
                </div>
                <br/><br/>
            </div>
            <!-- Payment Lines -->
            <t t-foreach='paymentlines' t-as='line'>
                <div style="font-size: 14px;border-top:1px dashed;padding-top: 5px;">
                    <span style="margin-left: 40%;"><t t-esc='line.name' /></span>
                    <span t-esc='widget.pos.format_currency_no_symbol(line.get_amount())' class="pos-receipt-right-align"/>
                </div>
            </t>
            <br/>  
            <div class="receipt-change" style="font-size: 14px;">
            <span style="margin-left: 40%;">CHANGE : </span>
                <span t-esc='widget.pos.format_currency(receipt.change)' class="pos-receipt-right-align"/>
            </div>
            <br/>
            <!-- Extra Payment Info -->
            <t t-if='receipt.total_discount'>
                <div style="font-size: 14px; border-top:1px dashed;padding-top: 5px;">
                    <span style="margin-left: 40%;">Discounts : </span>
                    <span t-esc='widget.pos.format_currency(receipt.total_discount)' class="pos-receipt-right-align"/>
                </div>
            </t>
            <t t-if='taxincluded'>
                <t t-foreach='receipt.tax_details' t-as='tax'>
                    <div style="font-size: 14px;">
                        <span style="margin-left: 40%;"><t t-esc='tax.name' /></span>
                        <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)' class="pos-receipt-right-align"/>
                    </div>
                </t>
                <div style="font-size: 14px;">
                    <span style="margin-left: 40%;">Total Taxes : </span>
                    <span t-esc='widget.pos.format_currency(receipt.total_tax)' class="pos-receipt-right-align"/>
                </div>
            </t>
            <div class='before-footer' />
            <!-- Footer -->
            <div t-if='receipt.footer_html' style="text-align: center; font-size: 14px;">
                <t t-raw='receipt.footer_html'/>
            </div>
            <div t-if='!receipt.footer_html and receipt.footer' style="text-align: center;font-size: 14px;">
                <br/>
                <t t-esc='receipt.footer'/>
                <br/><br/>
            </div>
            <div class='after-footer' style="font-size: 14px;">
                <t t-foreach='paymentlines' t-as='line'>
                    <t t-if='line.ticket'>
                        <br />
                        <div class="pos-payment-terminal-receipt">
                            <t t-raw='line.ticket'/>
                        </div>
                    </t>
                </t>
            </div>
            <br/><br/>
            <div>
                Thank You. Please Visit Again !!
            </div>
        </div>"""
        self.create(record_data)

    @api.model
    def _create_receipt_design_4(self):
        record_data = {}
        record_data['name'] = "ใบกำกับภาษีอย่างย่อ QC"
        record_data['receipt_design'] = """
      
        
      <div class="pos-receipt">
            <!--<div style="font-size: 80%; text-align:center;">-->
            <!--    <div><span t-esc='receipt.date.localestring'/>  <span t-esc='receipt.name'/></div>-->
            <!--</div>-->
            <br/>
            <t t-if="receipt.company.logo">
                <img class="pos-receipt-logo" t-att-src="receipt.company.logo" alt="Logo"/>
                <br/>
            </t>
            <t t-if="!receipt.company.logo">
                <h2 class="pos-receipt-center-align">
                    <t t-esc="receipt.company.name" />
                </h2>
                <br/>
            </t>
            <div class="pos-receipt-contact">
                <t t-if="receipt.company.contact_address">
                    <div><t t-esc="receipt.company.contact_address" /></div>
                </t>
                <t t-if="receipt.company.phone">
                    <div>Tel:<t t-esc="receipt.company.phone" /></div>
                </t>
                <t t-if="receipt.company.vat">
                    <div><t t-esc="receipt.company.vat_label"/>:<t t-esc="receipt.company.vat" /></div>
                </t>
                <t t-if="receipt.company.email">
                    <div><t t-esc="receipt.company.email" /></div>
                </t>
                <t t-if="receipt.company.website">
                    <div><t t-esc="receipt.company.website" /></div>
                </t>
                <t t-if="receipt.header_html">
                    <t t-out="receipt.header_html" />
                </t>
                <t t-if="!receipt.header_html and receipt.header">
                    <div style="white-space:pre-line"><t t-esc="receipt.header" /></div>
                </t>
                <t t-if="receipt.cashier">
                    <div class="cashier">
                        <div>--------------------------------</div>
                        <div>Served by <t t-esc="receipt.cashier" /></div>
                    </div>
                </t>
                <br/>
            </div>
            <!-- BOX 1 -->
            <div class='orderlines'>
               
                <br/>
                    <table style="width: 100%;">
                        <tr style="border-bottom: 1px solid black;font-size:13px;">
     
                        <th style="text-align:left;">รายการ</th>
                        <th style="text-align: left;">จำนวน</th>
                        <th style="text-align: left;">รวม</th>
                  
                        </tr>
                        
                        <t t-set="total_product" t-value="0"/>
                        <tr t-foreach="receipt.orderlines" t-as="line" style="border-bottom: 1px solid #ddd;font-size: 13px;font-family: initial;">
                        
                        <td><div style="padding-top: 10px;padding-bottom: 10px;">
                            <span t-esc='line.product_name_wrapped[0]'/>
                            <t t-if='line.discount !== 0'>
                                <h5 style="margin-top: 0%;margin-bottom: 0%;font-size: 12px;color: #848484;">
                                    <t t-esc='line.discount' />% Discount 
                                </h5>
                            </t>
                            <t t-if="line.customer_note">
                              <div style="font-size: 13px;" t-esc="line.customer_note"/>
                            </t>
                            </div>
                        </td>
                        
                        <td style="text-align: center;"><span t-esc="line.quantity"/><span t-if='line.unit_name !== "Units"'/></td>
                        <td style="text-align: center;"><span t-esc='widget.pos.format_currency_no_symbol(line.price_display)'/></td>
                        
                        <t t-if='line.price_display >= 0'>
                          <t t-set="total_product" t-value="total_product+line.price_display"/>
                        </t>
                        
                        </tr>
                        
                      
                    </table>
                </div>
                
                
                
                
            <!-- BOX 4 -->  
            <div style="font-size: 13px; border-top: 1px solid; padding-top: 3%; padding-bottom: 3%;">
              <div style="font-size: 13px;">
                <t t-set="total_qty" t-value="0"/>
                <t t-set="order_qty" t-value="0"/>
                <t t-foreach='receipt.orderlines' t-as='line'>
                  <t t-if="line['price_display'] &gt; 0">
                    <t t-set="total_qty" t-value="total_qty+line['quantity']"/>
                  </t>
                  <t t-if="line['orderlines'] &gt; 0">
                    <t t-set="order_qty" t-value="line+line['orderlines']"/>
                  </t>
                </t>
                <!--<span class="pos-receipt-left-align">รายการ : &amp;nbsp;</span>-->
                <!--<t t-esc="order_qty"/>-->
                <!--<span>&amp;nbsp</span>-->
                <span class="pos-receipt-left-align">จำนวนชิ้น : &amp;nbsp;</span>
                <t t-esc="total_qty"/>
              </div>
            </div>
            <!-- BOX 2/3 -->
            <div>
              <!--Subtotal -->
              <t t-set='taxincluded' t-value='Math.abs(receipt.subtotal - receipt.total_with_tax) &lt;= 0.000001' />
              <t t-if='!taxincluded'>
                  <div style="font-weight: 700;text-align: right; font-size: 20px;border-top: 2px solid;margin-left: 30%; padding-top: 2%;">Subtotal : <span t-esc='widget.pos.format_currency(receipt.subtotal)' class="pos-receipt-right-align"/></div>
                  <t t-foreach='receipt.tax_details' t-as='tax'>
                      <div style="font-weight: 700;text-align: right;">
                          <t t-esc='tax.name' />
                          <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)' class="pos-receipt-right-align"/>
                      </div>
                  </t>
              </t>
              <div style="border-top: 1px solid; padding-top: 3%; padding-bottom: 3%; ">
                <div style="font-size: 13px;">
                    รวมเป็นเงิน : <span t-esc='widget.pos.format_currency(total_product) ' class="pos-receipt-right-align" />
                </div>
                <div style="font-size: 13px;">
                    ส่วนลด : <span t-esc='widget.pos.format_currency(total_product-receipt.subtotal)' class="pos-receipt-right-align" />
                </div>
                <div style="font-size: 13px; ">
                    มูลค่าสุทธิ :  <span  t-esc='widget.pos.format_currency(receipt.subtotal)' class="pos-receipt-right-align"/>
                </div>
              </div>
              <!-- BOX 3 -->
              <div style="border-top: 1px solid; padding-top: 3%; padding-bottom: 3%;">
                <t t-if='taxincluded'>
                  <div style="font-size: 13px;">
                    VAT :
                    <span t-esc='widget.pos.format_currency(receipt.total_tax)' class="pos-receipt-right-align"/>
                  </div>
                    <!--<t t-foreach='receipt.tax_details' t-as='tax'>-->
                    <!--    <div style="font-size: 15px; text-align: right; font-weight: 700; border-top: 1px solid;margin-left: 30%;padding-top: 2%;">-->
                    <!--        <t t-esc='tax.name' />-->
                    <!--        <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)'/>-->
                    <!--    </div>-->
                    <!--</t>-->
                </t>
              </div>
              <div style="padding-bottom: 3%;">
                <t t-if='taxincluded'>
                  <div style="font-size: 13px;">
                    มูลค่าสุทธิก่อน VAT :
                    <span t-esc='widget.pos.format_currency(receipt.subtotal - receipt.total_tax)' class="pos-receipt-right-align"/>
                  </div>

                    <!--<t t-foreach='receipt.tax_details' t-as='tax'>-->
                    <!--    <div style="font-size: 15px; text-align: right; font-weight: 700; border-top: 1px solid;margin-left: 30%;padding-top: 2%;">-->
                    <!--        <t t-esc='tax.name' />-->
                    <!--        <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)'/>-->
                    <!--    </div>-->
                    <!--</t>-->
                </t>
              </div>
            </div>
              <!-- BOX 4 -->
              <t t-foreach='paymentlines' t-as='line'>
                <div style="font-size: 13px; padding-top: 3%; border-top: 1px solid;">
                  <span t-esc='line.name'/><span>&amp;nbsp;&amp;nbsp</span>
                  <span t-esc='widget.pos.format_currency_no_symbol(line.get_amount())' class="pos-receipt-left-align"/>
                  <span t-esc='widget.pos.format_currency(receipt.change)' class="pos-receipt-right-align"/>
                  <span class="pos-receipt-right-align">เงินทอน&amp;nbsp;&amp;nbsp;&amp;nbsp;</span>
                </div>
              </t>
              
              <t t-if="receipt.new_coupon_info and receipt.new_coupon_info.length !== 0">
                <div class="pos-coupon-rewards">
                    <div>------------------------</div>
                    <div>
                        Coupon Codes
                    </div>
                    <t t-foreach="receipt.new_coupon_info" t-as="coupon_info" t-key="coupon_info.code">
                        <div class="coupon-container">
                          <div style="font-size: 110%;">
                            <t t-esc="coupon_info['program_name']"/>
                          </div>
                          <div>
                            <span>Valid until: </span> 
                            <t t-if="coupon_info['expiration_date']">
                              <t t-esc="coupon_info['expiration_date']"/>
                            </t>
                            <t t-else="">
                              no expiration
                            </t>
                          </div>
                          <div>
                            <img t-att-src="'/report/barcode/Code128/'+coupon_info['code']" style="width:200px;height:50px" alt="Barcode"/>
                          </div>
                          <div>
                            <t t-esc="coupon_info['code']"/>
                          </div>
                        </div>
                    </t>
                </div>
            </t>
              
            <div class='before-footer' />
            <!-- Footer -->
            <div t-if='receipt.footer_html'  class="pos-receipt-center-align" style="font-size: 14px;">
                <t t-raw='receipt.footer_html'/>
            </div>
            <div t-if='!receipt.footer_html and receipt.footer'  class="pos-receipt-center-align" style="font-size: 13px;">
                <br/>
                <t t-esc='receipt.footer'/>
                <br/>
                <br/>
            </div>
            <div class='after-footer' style="font-size: 14px;">
                <t t-foreach='paymentlines' t-as='line'>
                    <t t-if='line.ticket'>
                        <br />
                        <div class="pos-payment-terminal-receipt">
                            <t t-raw='line.ticket'/>
                        </div>
                    </t>
                </t>
                
                  <t t-if='receipt.cashier'>
                    <div class='cashier'>
                       <div>พนักงานขาย <t t-esc='receipt.cashier' /></div>
                    </div>
                  </t>
                  
                  <br></br>
                  
                   <div class="pos-receipt-center-align">
                                         <span>รับประกันความเสียหายอันเกิดจากการขนส่งของทางเรา และ/หรือ พบตำหนิที่ไม่เป็นมาตรฐานของโรงงาน ภายใน 7 วัน </span>
                    </div>
                
                  
                   <div t-if="receipt.footer_html"  class="pos-receipt-center-align">
                <t t-out="receipt.footer_html" />
            </div>

            <div t-if="!receipt.footer_html and receipt.footer"  class="pos-receipt-center-align" style="white-space:pre-line">
                <br/>
                <t t-esc="receipt.footer" />
                <br/>
                <br/>
            </div>

            <div class="after-footer">
                <t t-foreach="receipt.paymentlines" t-as="line" t-key="line_index">
                    <t t-if="line.ticket">
                        <br />
                        <div class="pos-payment-terminal-receipt">
                            <t t-out="line.ticket" />
                        </div>
                    </t>
                </t>
            </div>

            <br/>
            <div class="pos-receipt-order-data">
                <div><t t-esc="receipt.name" /></div>
                <t t-if="receipt.date.localestring">
                    <div><t t-esc="receipt.date.localestring" /></div>
                </t>
                <t t-else="">
                    <div><t t-esc="receipt.date.validation_date" /></div>
                </t>
            </div>
        
            </div>
            <br/>
            

            <!--<div style="text-align:center;">-->
            <!--    Thank You. Please Visit Again !!-->
            <!--</div>-->
        </div>"""

        self.create(record_data)

        #ใบเสร็จอย่างย่อ OCT

        """
         
        <div class="pos-receipt">
            <!--<div style="font-size: 80%; text-align:center;">-->
            <!--    <div><span t-esc='receipt.date.localestring'/>  <span t-esc='receipt.name'/></div>-->
            <!--</div>-->
            <br/>
            <t t-if='receipt.company.logo'>
                <img style="width: 30%;display: block;margin: auto;" t-att-src='receipt.company.logo' alt="Logo"/>
                <br/>
            </t>
            <div style="font-size: 80%; text-align:center;">
                <t t-if='!receipt.company.logo'>
                    <h2 class="pos-receipt-center-align">
                        <t t-esc='receipt.company.name' />
                    </h2>
                </t>
                <t t-if='receipt.company.contact_address'>
                    <div><t t-esc='receipt.company.contact_address' /></div>
                </t>
                <t t-if='receipt.company.phone'>
                    <div>Tel:<t t-esc='receipt.company.phone' /></div>
                </t>
                <t t-if='receipt.company.website'>
                    <div><t t-esc='receipt.company.website' /></div>
                </t>
                <t t-if='receipt.header_html'>
                    <t t-raw='receipt.header_html' />
                </t>
                <t t-if='!receipt.header_html and receipt.header'>
                    <div><t t-esc='receipt.header' /></div>
                </t>
                <br/>
            </div>
            <!-- BOX 1 -->
            <div class='orderlines'>
                <div style="text-align:left; font-size: 75%;">
                  <t t-set="name_receipt" t-value="receipt.name.split('Order')"/>
                  <span>เลขที่เอกสาร : <span t-esc='receipt.name' /></span>
                  <div>วันที่ขาย : 
                    <t t-if="order.formatted_validation_date">
                      <span t-esc='order.formatted_validation_date' />
                    </t>
                    <t t-else="">
                      <span t-esc='order.validation_date' />
                    </t>
                  </div>
                  <t t-if='receipt.client'>
                      <div>Client : <t t-esc='receipt.client.name' /></div>
                      <br/>
                  </t>
                  <t t-if='receipt.cashier'>
                    <div class='cashier'>
                       <div>พนักงานขาย <t t-esc='receipt.cashier' /></div>
                    </div>
                  </t>
                </div>
                <br/>
                    <table style="width: 100%;">
                        <tr style="border-bottom: 1px solid black;font-size:13px;">
                        <th> &amp;nbsp;&amp;nbsp;&amp;nbsp; </th>
                        <th style="text-align:left;">รายการสินค้า</th>
                        <th style="text-align: left;">หน่วยละ</th>
                        <th>รวมเงิน</th>
                        </tr>
                        
                        <t t-set="total_product" t-value="0"/>
                        <tr t-foreach="receipt.orderlines" t-as="line" style="border-bottom: 1px solid #ddd;font-size: 13px;font-family: initial;">
                        <td style="text-align: center;"><span t-esc="line.quantity"/><span t-if='line.unit_name !== "Units"'/></td>
                        <td><div style="padding-top: 10px;padding-bottom: 10px;">
                            <span t-esc='line.product_name_wrapped[0]'/>
                            <t t-if='line.discount !== 0'>
                                <h5 style="margin-top: 0%;margin-bottom: 0%;font-size: 12px;color: #848484;">
                                    <t t-esc='line.discount' />% Discount 
                                </h5>
                            </t>
                            <t t-if="line.customer_note">
                              <div style="font-size: 13px;" t-esc="line.customer_note"/>
                            </t>
                            </div>
                        </td>
                        <td style="text-align: center;"><span t-esc="widget.pos.format_currency_no_symbol(line.price)"/></td>
                        <td style="text-align: center;"><span t-esc='widget.pos.format_currency_no_symbol(line.price_display)'/></td>
                        
                        <t t-if='line.price_display >= 0'>
                          <t t-set="total_product" t-value="total_product+line.price_display"/>
                        </t>
                        
                        </tr>
                    </table>
                </div>
            <!-- BOX 4 -->    
            <div style="font-size: 13px; border-top: 1px solid; padding-top: 3%; padding-bottom: 3%;">
              <div style="font-size: 13px;">
                <t t-set="total_qty" t-value="0"/>
                <t t-set="order_qty" t-value="0"/>
                <t t-foreach='receipt.orderlines' t-as='line'>
                  <t t-if="line['price_display'] &gt; 0">
                    <t t-set="total_qty" t-value="total_qty+line['quantity']"/>
                  </t>
                  <t t-if="line['orderlines'] &gt; 0">
                    <t t-set="order_qty" t-value="line+line['orderlines']"/>
                  </t>
                </t>
                <!--<span class="pos-receipt-left-align">รายการ : &amp;nbsp;</span>-->
                <!--<t t-esc="order_qty"/>-->
                <!--<span>&amp;nbsp</span>-->
                <span class="pos-receipt-left-align">จำนวนชิ้น : &amp;nbsp;</span>
                <t t-esc="total_qty"/>
              </div>
            </div>
            <!-- BOX 2/3 -->
            <div>
              <!--Subtotal -->
              <t t-set='taxincluded' t-value='Math.abs(receipt.subtotal - receipt.total_with_tax) &lt;= 0.000001' />
              <t t-if='!taxincluded'>
                  <div style="font-weight: 700;text-align: right; font-size: 20px;border-top: 2px solid;margin-left: 30%; padding-top: 2%;">Subtotal : <span t-esc='widget.pos.format_currency(receipt.subtotal)' class="pos-receipt-right-align"/></div>
                  <t t-foreach='receipt.tax_details' t-as='tax'>
                      <div style="font-weight: 700;text-align: right;">
                          <t t-esc='tax.name' />
                          <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)' class="pos-receipt-right-align"/>
                      </div>
                  </t>
              </t>
              <div style="border-top: 1px solid; padding-top: 3%; padding-bottom: 3%; ">
                <div style="font-size: 13px;">
                    รวมเป็นเงิน : <span t-esc='widget.pos.format_currency(total_product) ' class="pos-receipt-right-align" />
                </div>
                <div style="font-size: 13px;">
                    ส่วนลด : <span t-esc='widget.pos.format_currency(total_product-receipt.subtotal)' class="pos-receipt-right-align" />
                </div>
                <div style="font-size: 13px; ">
                    รวมทั้งสิน :  <span  t-esc='widget.pos.format_currency(receipt.subtotal)' class="pos-receipt-right-align"/>
                </div>
              </div>
              <!-- BOX 3 -->
              <div style="border-top: 1px solid; padding-top: 3%; padding-bottom: 3%;">
                <t t-if='taxincluded'>
                  <div style="font-size: 13px;">
                    รวมมูลค่าสินค้า :
                    <span t-esc='widget.pos.format_currency(receipt.subtotal - receipt.total_tax)' class="pos-receipt-right-align"/>
                  </div>
                  <div style="font-size: 13px;">
                    ภาษีมูลค่าเพิ่ม :
                    <span t-esc='widget.pos.format_currency(receipt.total_tax)' class="pos-receipt-right-align"/>
                  </div>
                    <!--<t t-foreach='receipt.tax_details' t-as='tax'>-->
                    <!--    <div style="font-size: 15px; text-align: right; font-weight: 700; border-top: 1px solid;margin-left: 30%;padding-top: 2%;">-->
                    <!--        <t t-esc='tax.name' />-->
                    <!--        <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)'/>-->
                    <!--    </div>-->
                    <!--</t>-->
                </t>
              </div>
            </div>
              <!-- BOX 4 -->
              <t t-foreach='paymentlines' t-as='line'>
                <div style="font-size: 13px; padding-top: 3%; border-top: 1px solid;">
                  <span t-esc='line.name'/><span>&amp;nbsp;&amp;nbsp</span>
                  <span t-esc='widget.pos.format_currency_no_symbol(line.get_amount())' class="pos-receipt-left-align"/>
                  <span t-esc='widget.pos.format_currency(receipt.change)' class="pos-receipt-right-align"/>
                  <span class="pos-receipt-right-align">เงินทอน&amp;nbsp;&amp;nbsp;&amp;nbsp;</span>
                </div>
              </t>
              
              <t t-if="receipt.new_coupon_info and receipt.new_coupon_info.length !== 0">
                <div class="pos-coupon-rewards">
                    <div>------------------------</div>
                    <div>
                        Coupon Codes
                    </div>
                    <t t-foreach="receipt.new_coupon_info" t-as="coupon_info" t-key="coupon_info.code">
                        <div class="coupon-container">
                          <div style="font-size: 110%;">
                            <t t-esc="coupon_info['program_name']"/>
                          </div>
                          <div>
                            <span>Valid until: </span> 
                            <t t-if="coupon_info['expiration_date']">
                              <t t-esc="coupon_info['expiration_date']"/>
                            </t>
                            <t t-else="">
                              no expiration
                            </t>
                          </div>
                          <div>
                            <img t-att-src="'/report/barcode/Code128/'+coupon_info['code']" style="width:200px;height:50px" alt="Barcode"/>
                          </div>
                          <div>
                            <t t-esc="coupon_info['code']"/>
                          </div>
                        </div>
                    </t>
                </div>
            </t>
              
            <div class='before-footer' />
            <!-- Footer -->
            <div t-if='receipt.footer_html'  class="pos-receipt-center-align" style="font-size: 14px;">
                <t t-raw='receipt.footer_html'/>
            </div>
            <div t-if='!receipt.footer_html and receipt.footer'  class="pos-receipt-center-align" style="font-size: 13px;">
                <br/>
                <t t-esc='receipt.footer'/>
                <br/>
                <br/>
            </div>
            <div class='after-footer' style="font-size: 14px;">
                <t t-foreach='paymentlines' t-as='line'>
                    <t t-if='line.ticket'>
                        <br />
                        <div class="pos-payment-terminal-receipt">
                            <t t-raw='line.ticket'/>
                        </div>
                    </t>
                </t>
            </div>
            <br/>
            <!--<div style="text-align:center;">-->
            <!--    Thank You. Please Visit Again !!-->
            <!--</div>-->
        </div>
        
        """





        #ใบกำกับภาษีอย่างย่อ QC

        '''
                       <div class="pos-receipt">
            <!--<div style="font-size: 80%; text-align:center;">-->
            <!--    <div><span t-esc='receipt.date.localestring'/>  <span t-esc='receipt.name'/></div>-->
            <!--</div>-->
            <br/>
            <t t-if="receipt.company.logo">
                <img class="pos-receipt-logo" t-att-src="receipt.company.logo" alt="Logo"/>
                <br/>
            </t>
            <t t-if="!receipt.company.logo">
                <h2 class="pos-receipt-center-align">
                    <t t-esc="receipt.company.name" />
                </h2>
                <br/>
            </t>
            <div class="pos-receipt-contact">
                <t t-if="receipt.company.contact_address">
                    <div><t t-esc="receipt.company.contact_address" /></div>
                </t>
                <t t-if="receipt.company.phone">
                    <div>Tel:<t t-esc="receipt.company.phone" /></div>
                </t>
                <t t-if="receipt.company.vat">
                    <div><t t-esc="receipt.company.vat_label"/>:<t t-esc="receipt.company.vat" /></div>
                </t>
                <t t-if="receipt.company.email">
                    <div><t t-esc="receipt.company.email" /></div>
                </t>
                <t t-if="receipt.company.website">
                    <div><t t-esc="receipt.company.website" /></div>
                </t>
                <t t-if="receipt.header_html">
                    <t t-out="receipt.header_html" />
                </t>
                <t t-if="!receipt.header_html and receipt.header">
                    <div style="white-space:pre-line"><t t-esc="receipt.header" /></div>
                </t>
                <t t-if="receipt.cashier">
                    <div class="cashier">
                        <div>--------------------------------</div>
                        <div>Served by <t t-esc="receipt.cashier" /></div>
                    </div>
                </t>
                <br/>
            </div>
            <!-- BOX 1 -->
            <div class='orderlines'>
               
                <br/>
                    <table style="width: 100%;">
                        <tr style="border-bottom: 1px solid black;font-size:13px;">
     
                        <th style="text-align:left;">รายการ</th>
                        <th style="text-align: left;">จำนวน</th>
                        <th style="text-align: left;">รวม</th>
                  
                        </tr>
                        
                        <t t-set="total_product" t-value="0"/>
                        <tr t-foreach="receipt.orderlines" t-as="line" style="border-bottom: 1px solid #ddd;font-size: 13px;font-family: initial;">
                        
                        <td><div style="padding-top: 10px;padding-bottom: 10px;">
                            <span t-esc='line.product_name_wrapped[0]'/>
                            <t t-if='line.discount !== 0'>
                                <h5 style="margin-top: 0%;margin-bottom: 0%;font-size: 12px;color: #848484;">
                                    <t t-esc='line.discount' />% Discount 
                                </h5>
                            </t>
                            <t t-if="line.customer_note">
                              <div style="font-size: 13px;" t-esc="line.customer_note"/>
                            </t>
                            </div>
                        </td>
                        
                        <td style="text-align: center;"><span t-esc="line.quantity"/><span t-if='line.unit_name !== "Units"'/></td>
                        <td style="text-align: center;"><span t-esc='widget.pos.format_currency_no_symbol(line.price_display)'/></td>
                        
                        <t t-if='line.price_display >= 0'>
                          <t t-set="total_product" t-value="total_product+line.price_display"/>
                        </t>
                        
                        </tr>
                        
                      
                    </table>
                </div>
                
                
                
                
            <!-- BOX 4 -->  
            <div style="font-size: 13px; border-top: 1px solid; padding-top: 3%; padding-bottom: 3%;">
              <div style="font-size: 13px;">
                <t t-set="total_qty" t-value="0"/>
                <t t-set="order_qty" t-value="0"/>
                <t t-foreach='receipt.orderlines' t-as='line'>
                  <t t-if="line['price_display'] &gt; 0">
                    <t t-set="total_qty" t-value="total_qty+line['quantity']"/>
                  </t>
                  <t t-if="line['orderlines'] &gt; 0">
                    <t t-set="order_qty" t-value="line+line['orderlines']"/>
                  </t>
                </t>
                <!--<span class="pos-receipt-left-align">รายการ : &amp;nbsp;</span>-->
                <!--<t t-esc="order_qty"/>-->
                <!--<span>&amp;nbsp</span>-->
                <span class="pos-receipt-left-align">จำนวนชิ้น : &amp;nbsp;</span>
                <t t-esc="total_qty"/>
              </div>
            </div>
            <!-- BOX 2/3 -->
            <div>
              <!--Subtotal -->
              <t t-set='taxincluded' t-value='Math.abs(receipt.subtotal - receipt.total_with_tax) &lt;= 0.000001' />
              <t t-if='!taxincluded'>
                  <div style="font-weight: 700;text-align: right; font-size: 20px;border-top: 2px solid;margin-left: 30%; padding-top: 2%;">Subtotal : <span t-esc='widget.pos.format_currency(receipt.subtotal)' class="pos-receipt-right-align"/></div>
                  <t t-foreach='receipt.tax_details' t-as='tax'>
                      <div style="font-weight: 700;text-align: right;">
                          <t t-esc='tax.name' />
                          <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)' class="pos-receipt-right-align"/>
                      </div>
                  </t>
              </t>
              <div style="border-top: 1px solid; padding-top: 3%; padding-bottom: 3%; ">
                <div style="font-size: 13px;">
                    รวมเป็นเงิน : <span t-esc='widget.pos.format_currency(total_product) ' class="pos-receipt-right-align" />
                </div>
                <div style="font-size: 13px;">
                    ส่วนลด : <span t-esc='widget.pos.format_currency(total_product-receipt.subtotal)' class="pos-receipt-right-align" />
                </div>
                <div style="font-size: 13px; ">
                    รวมทั้งสิน :  <span  t-esc='widget.pos.format_currency(receipt.subtotal)' class="pos-receipt-right-align"/>
                </div>
              </div>
              <!-- BOX 3 -->
              <div style="border-top: 1px solid; padding-top: 3%; padding-bottom: 3%;">
                <t t-if='taxincluded'>
                  <div style="font-size: 13px;">
                    รวมมูลค่าสินค้า :
                    <span t-esc='widget.pos.format_currency(receipt.subtotal - receipt.total_tax)' class="pos-receipt-right-align"/>
                  </div>
                  <div style="font-size: 13px;">
                    ภาษีมูลค่าเพิ่ม :
                    <span t-esc='widget.pos.format_currency(receipt.total_tax)' class="pos-receipt-right-align"/>
                  </div>
                    <!--<t t-foreach='receipt.tax_details' t-as='tax'>-->
                    <!--    <div style="font-size: 15px; text-align: right; font-weight: 700; border-top: 1px solid;margin-left: 30%;padding-top: 2%;">-->
                    <!--        <t t-esc='tax.name' />-->
                    <!--        <span t-esc='widget.pos.format_currency_no_symbol(tax.amount)'/>-->
                    <!--    </div>-->
                    <!--</t>-->
                </t>
              </div>
            </div>
              <!-- BOX 4 -->
              <t t-foreach='paymentlines' t-as='line'>
                <div style="font-size: 13px; padding-top: 3%; border-top: 1px solid;">
                  <span t-esc='line.name'/><span>&amp;nbsp;&amp;nbsp</span>
                  <span t-esc='widget.pos.format_currency_no_symbol(line.get_amount())' class="pos-receipt-left-align"/>
                  <span t-esc='widget.pos.format_currency(receipt.change)' class="pos-receipt-right-align"/>
                  <span class="pos-receipt-right-align">เงินทอน&amp;nbsp;&amp;nbsp;&amp;nbsp;</span>
                </div>
              </t>
              
              <t t-if="receipt.new_coupon_info and receipt.new_coupon_info.length !== 0">
                <div class="pos-coupon-rewards">
                    <div>------------------------</div>
                    <div>
                        Coupon Codes
                    </div>
                    <t t-foreach="receipt.new_coupon_info" t-as="coupon_info" t-key="coupon_info.code">
                        <div class="coupon-container">
                          <div style="font-size: 110%;">
                            <t t-esc="coupon_info['program_name']"/>
                          </div>
                          <div>
                            <span>Valid until: </span> 
                            <t t-if="coupon_info['expiration_date']">
                              <t t-esc="coupon_info['expiration_date']"/>
                            </t>
                            <t t-else="">
                              no expiration
                            </t>
                          </div>
                          <div>
                            <img t-att-src="'/report/barcode/Code128/'+coupon_info['code']" style="width:200px;height:50px" alt="Barcode"/>
                          </div>
                          <div>
                            <t t-esc="coupon_info['code']"/>
                          </div>
                        </div>
                    </t>
                </div>
            </t>
              
            <div class='before-footer' />
            <!-- Footer -->
            <div t-if='receipt.footer_html'  class="pos-receipt-center-align" style="font-size: 14px;">
                <t t-raw='receipt.footer_html'/>
            </div>
            <div t-if='!receipt.footer_html and receipt.footer'  class="pos-receipt-center-align" style="font-size: 13px;">
                <br/>
                <t t-esc='receipt.footer'/>
                <br/>
                <br/>
            </div>
            <div class='after-footer' style="font-size: 14px;">
                <t t-foreach='paymentlines' t-as='line'>
                    <t t-if='line.ticket'>
                        <br />
                        <div class="pos-payment-terminal-receipt">
                            <t t-raw='line.ticket'/>
                        </div>
                    </t>
                </t>
                
                  <t t-if='receipt.cashier'>
                    <div class='cashier'>
                       <div>พนักงานขาย <t t-esc='receipt.cashier' /></div>
                    </div>
                  </t>
                  
                  <br></br>
                  
                   <div class="pos-receipt-center-align">
                                         <span>รับประกันความเสียหายอันเกิดจากการขนส่งของทางเรา และ/หรือ พบตำหนิที่ไม่เป็นมาตรฐานของโรงงาน ภายใจ 7 วัน</span>
                    </div>
                
                  
                   <div t-if="receipt.footer_html"  class="pos-receipt-center-align">
                <t t-out="receipt.footer_html" />
            </div>

            <div t-if="!receipt.footer_html and receipt.footer"  class="pos-receipt-center-align" style="white-space:pre-line">
                <br/>
                <t t-esc="receipt.footer" />
                <br/>
                <br/>
            </div>

            <div class="after-footer">
                <t t-foreach="receipt.paymentlines" t-as="line" t-key="line_index">
                    <t t-if="line.ticket">
                        <br />
                        <div class="pos-payment-terminal-receipt">
                            <t t-out="line.ticket" />
                        </div>
                    </t>
                </t>
            </div>

            <br/>
            <div class="pos-receipt-order-data">
                <div><t t-esc="receipt.name" /></div>
                <t t-if="receipt.date.localestring">
                    <div><t t-esc="receipt.date.localestring" /></div>
                </t>
                <t t-else="">
                    <div><t t-esc="receipt.date.validation_date" /></div>
                </t>
            </div>
        
            </div>
            <br/>
            

            <!--<div style="text-align:center;">-->
            <!--    Thank You. Please Visit Again !!-->
            <!--</div>-->
        </div>
        '''



class PosSession(models.Model):
    _inherit = "pos.session"
    
    def _loader_params_receipt_design(self):
        return {'search_params': {'fields': []}}
    
    def _pos_ui_models_to_load(self):
        models = super()._pos_ui_models_to_load()
        if 'receipt.design' not in models:
            models.append('receipt.design')
        return models
    
    def _get_pos_ui_receipt_design(self, params):
        receipt_design = self.env['receipt.design'].search_read(**params['search_params'])
        return receipt_design





