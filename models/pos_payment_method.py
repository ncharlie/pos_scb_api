import json
import string
from datetime import datetime, timedelta
from random import choice

import requests
from odoo import models, fields, _
from odoo.exceptions import UserError


def _rand_str(length):
    return ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(length))


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    def get_scb_qr_fees(self, amount):
        if self.payment_method_type != "qr_code" or not self.qr_code_method:
            return {'success': False}

        domain = [('pos_payment_method_id', '=', self.id)]
        scb_config_id = self.env['scb.payment.configuration'].sudo().search(domain, limit=1)

        if scb_config_id:
            payment_amount = scb_config_id.fix_payment_fees + amount
            if (scb_config_id.min_price <= payment_amount <= scb_config_id.max_price) or (
                    scb_config_id.min_price == 0 and scb_config_id.max_price == 0):
                return {
                    'success': True,
                    'fix_payment_fees': scb_config_id.fix_payment_fees,
                    'fix_payment_product_id': scb_config_id.fix_payment_product_id.id
                }

        return {'success': False}

    def get_qr_code(
            self, amount, free_communication, structured_communication, currency, debtor_partner):
        self.ensure_one()
        default_qr = super(
            PosPaymentMethod, self).get_qr_code(
            amount=amount, free_communication=free_communication,
            structured_communication=structured_communication, currency=currency,
            debtor_partner=debtor_partner)
        check_token = True
        if self.payment_method_type != "qr_code" or not self.qr_code_method:
            raise UserError(_("This payment method is not configured to generate QR codes."))

        if not free_communication:
            return default_qr

        domain = [('pos_payment_method_id', '=', self.id)]
        scb_config_id = self.env['scb.payment.configuration'].sudo().search(domain, limit=1)
        if scb_config_id:
            if (scb_config_id.min_price <= amount <= scb_config_id.max_price) or (
                    scb_config_id.min_price == 0 and scb_config_id.max_price == 0):
                if scb_config_id.access_token and scb_config_id.last_token_generated_at:
                    current_time = datetime.now()
                    time_in_28_minutes = scb_config_id.last_token_generated_at + timedelta(
                        minutes=28)
                    if current_time <= time_in_28_minutes:
                        check_token = False
                if check_token and scb_config_id:
                    self._generate_token(scb_config_id)
                if scb_config_id.access_token:
                    qr_create_url = f"{
                        scb_config_id.api_base_url}/partners/sandbox/v1/payment/qrcode/create"
                    ref1 = _rand_str(20)
                    ref2 = _rand_str(20)
                    ref3 = f"{scb_config_id.reference_3_prefix}{_rand_str(7)}"
                    payload = json.dumps({
                        "qrType": "PP",
                        "ppType": "BILLERID",
                        "ppId": scb_config_id.ppid,
                        "amount": str(amount),
                        "ref1": ref1,
                        "ref2": ref2,
                        "ref3": ref3,
                    })
                    print(payload)
                    headers = {
                        'Content-Type': 'application/json',
                        'authorization': f'Bearer {scb_config_id.access_token}',
                        'resourceOwnerId': scb_config_id.api_key,
                        'requestUId': str(self.env.user.id),
                        'accept-language': 'EN',
                    }
                    response = requests.request("POST", qr_create_url,
                                                headers=headers, data=payload)
                    data = response.json()
                    if data and data.get('data') and data.get('data').get('qrImage'):
                        return {
                            'qrImage': data.get('data').get('qrImage'),
                            'qrRawData': data.get('data').get('qrRawData'),
                            'amount': amount,
                            'scb_config_id': scb_config_id.id,
                            'scb_config_name': scb_config_id.name,
                            'qr_timer': scb_config_id.qr_timer,
                            'fix_payment_fees': scb_config_id.fix_payment_fees,
                            'fix_payment_product_id': scb_config_id.fix_payment_product_id.id,
                            'ref1': ref1,
                            'ref2': ref2,
                            'ref3': ref3,
                        }
                    raise UserError(_(data.get('status', {}).get('description', False)))
                else:
                    raise UserError(_("Bank QR generation failed for this payment method"))
            else:
                raise UserError(f"Amount is not in the range of this payment method ({scb_config_id.min_price}-{scb_config_id.max_price})")
        else:
            return default_qr

    def _generate_token(self, scb_config_id):
        try:
            api_base_url = scb_config_id.api_base_url
            api_key = scb_config_id.api_key
            api_secret = scb_config_id.api_secret
            if api_base_url and api_key and api_secret:
                url = f"{api_base_url}/partners/sandbox/v1/oauth/token"
                payload = json.dumps({
                    "applicationKey": api_key,
                    "applicationSecret": api_secret
                })
                headers = {
                    'Content-Type': 'application/json',
                    'resourceOwnerId': api_key,
                    'requestUId': str(self.env.user.id),
                    'accept-language': 'EN',
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                data = response.json()
                if data and data.get('data') and data.get('data').get('accessToken'):
                    scb_config_id.write({
                        'access_token': data.get('data').get('accessToken'),
                        'last_token_generated_at': fields.Datetime.now()
                    })
                    self.env.cr.commit()
                    return {'success': True}
                return {'success': False, 'message': _('Something went wrong, Please try again')}
        except Exception as e:
            return {'success': False, 'message': str(_(e))}
