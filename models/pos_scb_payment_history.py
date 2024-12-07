from odoo import fields, models, api


class POSSCBPaymentHistory(models.Model):
    _name = 'pos.scb.payment.history'
    _description = 'POS QR30 Payment History'

    @api.model
    def _load_pos_data_domain(self, data):
        return []

    @api.model
    def _load_pos_data_fields(self):
        return ['id', 'qr_code_raw_data', 'amount', 'bank_transaction_ref', 'customer_bank_ref',
                'customer_acc_no', 'customer_acc_name']

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields()
        data = self.search_read(domain, fields, load=False)
        return {
            'data': data,
            'fields': fields,
        }

    name = fields.Many2one('pos.payment.method', string='QR30 Payment Method')
    order_id = fields.Many2one('pos.order', string='POS Order')
    currency_id = fields.Many2one(related='order_id.currency_id')
    qr_code_raw_data = fields.Text('QR Code RAW Data')
    qr_status = fields.Selection([
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('timeout', 'Timeout'),
        ('confirmed_manually', 'Confirmed Manually'),
        ('paid', 'Paid')
    ], string='QR Status')
    amount = fields.Monetary()
    bank_transaction_ref = fields.Char('Bank Transaction ID (Ref.)')
    customer_bank_ref = fields.Char('Customer Bank ID (Ref.)')
    customer_acc_no = fields.Char('Customer Account No.')
    customer_acc_name = fields.Char('Customer Account Name')
    ref1 = fields.Char(string='Ref1')
    ref2 = fields.Char(string='Ref2')
    ref3 = fields.Char(string='Ref3')
