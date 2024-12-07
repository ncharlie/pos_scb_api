from odoo import api, fields, models, _


class SCBPaymentConfiguration(models.Model):
    _name = 'scb.payment.configuration'
    _inherit = ['mail.thread']
    _description = 'QR30 Payment Configuration'
    _order = 'sequence, id'

    def _default_payment_status_webhook_url(self):
        return f"{
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')} /scb/payment/status"

    def action_test_connection(self):
        try:
            result = self.env['pos.payment.method']._generate_token(self)
            if result and result.get('success'):
                message = _('Connection Test Successful!')
            else:
                message = _(result.get('message'))
        except Exception as e:
            message = str(_(e)) if e else _("Something went wrong, please try again")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    sequence = fields.Integer(default=1, tracking=True)
    name = fields.Char(tracking=True)
    pos_payment_method_id = fields.Many2one(
        'pos.payment.method', string="Pos Payment Method", tracking=True)
    journal_id = fields.Many2one(related='pos_payment_method_id.journal_id', string='Journal')
    api_key = fields.Char('Key')
    api_secret = fields.Char('Secret')
    ppid = fields.Char(
        'Biller ID', help="Partners can get on merchant profile of their application")
    api_environment = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('production', 'Production')
    ], default='sandbox', string='Environment')
    api_base_url = fields.Char('Base URL')
    min_price = fields.Float(tracking=True)
    max_price = fields.Float(tracking=True)
    fix_payment_fees = fields.Float(tracking=True)
    fix_payment_product_id = fields.Many2one('product.product', string="Fix Payment Product")
    active = fields.Boolean(default=True, tracking=True)
    payment_status_webhook_url = fields.Char(
        'Payment Status Webhook URL', readonly=True,
        store=False,
        default=lambda self: f"{self.get_base_url()}/pos_bank_api/notification")
    last_token_generated_at = fields.Datetime(string='Last Token Generated')
    access_token = fields.Char('Access Token')
    qr_timer = fields.Integer(string='QR Timer(Seconds)', default=600)
    reference_3_prefix = fields.Char('Reference 3 Prefix')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name must be unique!')
    ]

    @api.onchange('api_environment')
    def _onchange_api_environment(self):
        if self.api_environment == 'sandbox':
            self.api_base_url = 'https://api-sandbox.partners.scb'
        elif self.api_environment == 'production':
            self.api_base_url = 'https://api.partners.scb'
