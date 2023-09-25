1) สินค้าคงคลัง
2) ภาษีซื้อ และ ภาษีขาย
3) รายงาน Journal รายการของสมุดรายวันซื้อ ขาย รับ จ่าย ละเอียด รายสมุด ตามช่วงเวลา และ แบบสรุปบัญชีที่เกี่ยวกับ Journal นั้น
4) A4 Format (TOP,Botoom, Right, Left)
5) หนังสือรับรองการหัก ณ ที่จ่าย ภ.ง.ด.53 หน้า Account Invoice
6) หนังสือรับรองการหัก ณ ที่จ่าย ภ.ง.ด.53 หน้า Account Move
7) หนังสือรับรองการหัก ณ ที่จ่าย ภ.ง.ด.3 หน้า Account Invoice
8) หนังสือรับรองการหัก ณ ที่จ่าย ภ.ง.ด.3 หน้า Account Move
9) สมุดรายวันซื่อ
10) สมุดรายวันขาย
11) ใบสำคัญรับ
12) ใบสำคัญจ่าย
13) ใบสำคัญทั่วไป
14) รายงานรายชื่อลุกค้า
15) รายงานรายชื่อเจ้าหนี้ (Supplier)
---------------------------------------------------
17/03/2018 - Update รายงานเจ้าหนี้ และ รายงานลูกหนี้ให้แสดงส่วนของลดหนี้ด้วย และ มีสถานะให้เลือกทั้ง Draft, Open และ Paid
17/03/2018 - Update รายงานเจ้าหนี้ และ รายงานลูกหนี้ให้แสดงส่วนของยอดค้างจ่าย และสถานะ
17/03/2018 - Update รายงานเจ้าหนี้ ให้แสดงส่วนของ Analytic Account ระดับ Line ให้แสดงต่อ Bill
22/03/2018 - แก้ไขการทำใบวางบิลให้รวมรายการลดหนี้ไปด้วย
---------------------------------
29/03/2018 - แก้ไขเพิ่ม Option ใน Company cofiguration ให้เลือกว่าจะแสดงยอมรวมในรายงานภาษีซื้อ และ ขาย ด้วยหรือไม่ (เฉพาะ Version PDF)
29/03/2018 - แก้ไขรายงานภาษีซื้อ และ ขาย ไม่ต้องแสดงเลขที่สาขา ถ้าเป็นสำนักงานใหญ่
29/03/2018 - ปรับ เอกสาร ใบสำคัญรับ จ่าย ให้มีตำแหน่ง Logo ที่รองรับขนาดต่างๆ ได้มากขึ้น
29/03/2018 - ปรับ ขนาดตัวอักษรของเอกสาร หัก ณ ที่จ่าย เพื่อรองรับลุกค้าที่มีที่อยู่ยาวเกินไป
29/03/2018 - แก้ไขเรื่องแผนกเมื่อทำการชำระเงินแบบมี Deduction
29/03/2018 - แก้ไขรายงานภาษีซื้อ ให้เรียงรายการตามวันที่ใบกำกับภาษีที่ได้รับ (สรรพากรให้เรียงตามการได้มาของเอกสาร)
29/03/2018 - แก้ไขไม่ให้แสดงปุ่ม "พิพม์ใบกำกับภาษี" แบบครั้งเดียว เนื่องจากรายงานใบกำกับของแต่ละบริษัทเป็นคนตัวกัน
29/03/2018 - แก้ไขรายงานภาษีซื้อ ให้รองรับการปิดภาษีประจำเดือน
29/03/2018 - แก้ไขเรื่อง Credit Note ของ Supplier
29/03/2018 - แก้ไขเรื่อง รายงานภาษีขาย ทั้ง Excel และ PDF Version (จะต้องมาจาก Invoice เท่านั้น) ให้สามารถเลือกแยกระหว่างภาษีหลัก และ ภาษีอื่นๆ (แต่ภาษีอื่นจะต้องสรุปภาษีแยก) เช่น บางบริษัทมีภาษีเป็น 0 แต่กรณีที่เป็นภาษียังไม่ถึงกำหนด สุดท้ายจะอยู่ในกลุ่มภาษีหลัก
29/03/2018 - แก้ไขเรื่อง รายงานภาษีขาย ทั้ง Excel และ PDF Version (จะต้องมาจาก Invoice เท่านั้น) ให้สามารถรองรับแบบ Multi-Currency
04/03/2018 - แก้ไขเรื่องสิทธิ์การมองเห็นเมนู Cheque รับ และ จ่าย
---------------------------------------------------------------------------------
09/04/2018 - แก้ไขให้ระบบไม่สามารถยกเลิกหรือลบ Customer billing ได้ถ้าไม่ใช่ "draft" หรือ "cancel"
26/04/2018 - เอา model stock picking ออกจาก thai_accounting เพราะจะรวมใน stock_extended อยู่แล้ว
26/04/2018 - เอา model stock land cost ออกจาก thai_accounting เพราะจะรวมใน stock_extended อยู่แล้ว
---------------------------------------------------------------------------------
29/04/2018 - แก้ไขการกด "Register Payment" จากหน้า Customer Billing โดยจะขึ้นเตือนหาก Invoice นั้นถูก Paid ไปแล้ว
29/04/2018 - แก้ไขให้ Customer Billing เปลี่ยนสถานะเป็น Paid หาก Invoice ถูก paid ไปแล้ว
29/04/2018 - แก้ไขให้ payment_id ใน invoice ไม่ถูก copy
29/04/2018 - แก้ไขให้ Refund ระบุวันที่ได้
29/04/2018 - แก้ไขการทำใบลดหนี้ เนื่องจากเหตุผลไม่ไปแสดงในเอกสารใบลดหนี้ และ วันที่ใบกำกับเก่าไม่ไปด้วย
29/04/2018 - แก้ไขให้ Check Sequence อิงจากวันที่ระบุในการ Issue Date
-----------------------------------------------------------------
29/04/2018 - ให้การคิดหัก ณ ที่จ่ายคำนวนจำนวนเงิน จากยอดก่อน VAT และ % ได้
29/04/2018 - ตัวเลขก่อน VAT และ ตัวเลขหัก ณ ที่จ่าย เปลี่ยนจาก Monetary เป็น Float
29/04/2018 - คำนวนว่าต้องการ Write off account กรณีที่มีสกุลเงินต่างประเทศ
29/04/2018 - ผั่งรับเงิน หากสกุลเงินต่างประเทศได้เงินเกินมาจากที่ควรจะเป็นในหน้า Payment Diff จะเป็นติดลบ แต่จะลงบัญชีถูกต้อง
********************29/04/2018 - Customer Billing, Multi Register Payment ยังมีปัญหาเรื่องการเปลี่ยนสกุลเงิน**********
09/05/2018 - แก้ไขเรื่องสิทธิ์การเห็นราคาขาย และ ราคาต้นทุน
-------------------------------------
16/06/2018 - remove payment_id ใน account.invoice เนื่องจากมี payment_ids ที่รวมทุก Payment มาแสดงแล้ว
16/06/2018 - แก้ไขเงื่อนไขในการแสดงผลของ multi-write-off ถึงแม้จะเป็น การจ่ายแบบมียอดค้างก็ให้แสดงผล Multi-write-off ไว้ด้วย
16/06/2018 - ยกเลิก Credit Note เมนู เนื่องจาก Version 11 แยก Credit Note ให้อยู่แล้ว
16/06/2018 - เพื่อเงื่อนไขให้อะิบายหากเลือก CN Other Reason
16/06/2018 - เพิ่มข้อมูล Account ปลายทางของเช็ค user สามารถเปล่ียนเป็น Account อื่นก่อน Confirm ได้
16/06/2018 - เพิ่มข้อมูล Account ปลายทางของเช็ค Payment Voucher สามารถเปล่ียนเป็น Account อื่นก่อน Post ได้
16/06/2018 - แยก .py ของ payment เป้น billing, payment and register payment
---------------------------------------
Error or Warning List:
Warning 030 : Only one cheque can be create
Warning 031 : Cheque already exist
Warning 032 : Please assign line with account for Cheque
----------------------------------------------------------------
# 15.0.1.0
# Pending for invoice back date sequence

# add function to create receipt check and payment cheque from payment
# add function to post, cancel, set_to_draft, validate, reject
# add function to post from payment including cheque creation
#      account.journal
# add journal property for adjust for tax
# add journal property for adjust for bank and cheque, bank revese for cheque
# add journal property for debit sequence
# add journal property for tax_invoice sequence
# add journal property for payment sequence
#      account.move
# add field function for invoice and tax invoice process, adjust_move_id
# add field function for invoice and tax invoice process
# add field function for payment with cheque to have detail on account move
# add field function for supplier manual info
# add function action_invoice_generate_tax_invoice()
# add function create_reverse_tax()
# add function roundup()
# add model for account.wht.type
# inherit model for account.move.line for wht_tax,wht_type, wht_reference, amount_before_tax,invoice_date,is_debit with get_is_debit_credit()
# add function for account.move.line roundup(), roundupto()
#      account.payment
# add field for payment, write off account, cheque payment
# add function for cancel
#      account.tax
# add field for wht and tax default property,
#      customer.billing
# for customer billing process without register directly from here
#      account.move
#-----------------------------------------------------------
# 13.0.1.1
# clean view file and remove un-use file
# clean models file and remove un-use file
#-----------------------------------------------------------
# 13.0.1.2
# fix generate or reverse tax for invoice and bill with "generate tax/reverse tax" button
# 13.0.1.3
# add invoice multiple register with deduction
# 13.0.1.4
# change cheque validate sequence number
# 13.0.1.5
# fix payment_new_change_account
# fix write_off_with_open invoice
# 13.0.1.6
# fix write_off_with_open invoice and final invoice
# fix amount before tax when add deduct item
#------------------------------------------------------------
#13.0.1.7
# gen seq wht_reference for witholding tax
#-----------------Well Known Issue---------------#
# register payment from customer billing issue when has credit note
#13.0.1.8
# Move button gen tax (invoice) to itaas_gen_tax_invoice_date
#13.0.1.9 - 24/04/2021
# fix payment with keep open on multiple invoice payment
# record payment with multiple write-off account
#13.0.2.0 - 26/04/2021
#fix payment normal, deduction and possible to change from payment, validate and auto reconcile both ar and ap
#fix payment name will assign correctly both register from invoice and directly from payment journal
#13.0.2.1 - 02/05/2021 - remove partner bank id to group payment
#fix - partial payment and with
#fix - full and partial payment with grouping and not-group
#fix - add multiple-cheque validation
#13.0.2.2 - 20/05/2021 - fix onchange deduction item
#13.0.2.3 - 31/05/2021 Edit field Ref in model account.move and account.move.line
#13.0.3.1 - 08/06/2021 By Jeng Create Chequne in Journal Entry
#13.0.3.2 - 08/08/2021 by JA
# Create field for CN manual reference
# update view for partner manual
# add credit note reason and menu
# fix customer billing multi company
# fix cheque rec and pay for multi company
# fix billing sequence on supplier billing
# change receipt date to due date on customer billing and supplier billing
# add payment method
# add note for accounting
# change ref from sale tab to before name
#13.0.3.3 - 10/06/2021 - disable create check if not manual check is checked on journal entry
#13.0.3.4 - 15/06/2021 - fix confirm check need to add 'type' : 'entry'
#13.0.3.5 - 19/06/2021
#add manual CN for bill
#add multiple confirm cheque on cheque payment
#13.0.3.6 - 19/06/2021
#add customer no vat
#13.0.3.7 - 21/06/2021
#Edit Cheque /// reject /// cancel
#13.0.3.8 - 23/08/2021 - remove don't use .py
#13.0.3.9 - 23/08/2021 - fix confirm multiple check payment - fix check_multiple_confirm.py
#13.0.4.5 - fix difference payment can be done for multi invoice payment, work with htc_payment_difference_account
#13.0.4.6 - fix customer billing only not paid invoice
#13.0.4.7 - partial payment for single invoice and multiple invoice and wht (done)
#13.0.4.8 - change invoice type for "out_invoce,out_refund" are incoming, "in_invoice,in_refund" are outgoing, assume that normal more than refund
#13.0.4.9 - change default group payment = False, for case of ONETIME
#--------------------------------------------------------------------#
#15.0.1.2 - fix ไม่สามารถทำจ่ายได้ เนื่องจาก CODE เกี่ยวกับ WHT #############
#15.0.1.4 - 15.0.1.6  Update Seqeunce Payment #############





