import json
from odoo import http
from odoo.http import request


class SCBPaymentIntegration(http.Controller):

    @http.route(['/scb/payment/status'], type='json', auth='none')
    def scb_payment_callback(self, **kw):
        data = request.httprequest.data
        print("\n\n SCB: Callback: data", data)
        request.env["bus.bus"]._sendone(
            f"scb_payment_callback", "PAYMENT_CALLBACK", data
        )
        result = json.loads(data.decode('utf-8'))
        return {
            "resCode": "00",
            "resDesc ": "success",
            "transactionId": result.get('transactionId'),
        }

    @http.route(['/pos_qr/notification'], type='http', auth='public', methods=['POST'], csrf=False)
    def payment_callback(self, **kw):
        data = request.httprequest.data
        print("\n\n SCB: Callback: data", data)
        request.env["bus.bus"]._sendone(
            f"scb_payment_callback", "PAYMENT_CALLBACK", data
        )
        result = json.loads(data.decode('utf-8'))

        headers = {'Content-Type': 'application/json'}
        response = {
            "resCode": "00",
            "resDesc ": "success",
            "transactionId": result.get('transactionId'),
        }

        return http.Response(json.dumps(response), headers=headers)
