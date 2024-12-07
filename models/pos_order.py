import ast

from odoo import fields, models, api


class POSOrder(models.Model):
    _inherit = 'pos.order'

    @api.depends('scb_payment_history_ids.qr_code_raw_data')
    def _compute_is_visible_void_button(self):
        for record in self:
            record.is_visible_void_button = True if len(
                record.scb_payment_history_ids) > 0 else False

    def action_refund_payment(self):
        print("\n\n Call Action Refund Payment Button >>>>> ", self)

    @api.model
    def cancel_api_request(self):
        print("\n\n Cancel API Request CALL")

    @api.model
    def _process_order(self, order, existing_order):
        order_id = super()._process_order(order=order, existing_order=existing_order)
        order_id = self.browse(order_id)
        # print("order.get('scb_transaction_details') >>>>>>> ", order.get('scb_transaction_details'))
        if order.get('scb_transaction_details'):
            scb_transaction_details = ast.literal_eval(order.get('scb_transaction_details'))
            order_id.write({
                'scb_payment_history_ids': [(0, 0, {
                    'name': scb_transaction_details.get('scb_config_id'),
                    'order_id': order_id.id,
                    'amount': scb_transaction_details.get('amount'),
                    'bank_transaction_ref': scb_transaction_details.get('transactionId'),
                    'customer_bank_ref': scb_transaction_details.get('sendingBankCode'),
                    'customer_acc_no': scb_transaction_details.get('payerAccountNumber'),
                    'customer_acc_name': scb_transaction_details.get('payerName'),
                    'qr_code_raw_data': scb_transaction_details.get('qrRawData'),
                    'qr_status': scb_transaction_details.get('qr_status') if scb_transaction_details.get(
                        'qr_status') else False,
                    'ref1': scb_transaction_details.get('billPaymentRef1'),
                    'ref2': scb_transaction_details.get('billPaymentRef2'),
                    'ref3': scb_transaction_details.get('billPaymentRef3'),
                })]
            })
        return order_id.id

    scb_transaction_details = fields.Json(string="SCB Transaction Details")
    scb_payment_history_ids = fields.One2many(
        'pos.scb.payment.history', 'order_id', string='SCB Payment History')
    is_visible_void_button = fields.Boolean(string="Is visible void button?",
                                            compute="_compute_is_visible_void_button", store=True)
