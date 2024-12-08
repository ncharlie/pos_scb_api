import json
from odoo import http
from odoo.http import request


class SCBPaymentIntegration(http.Controller):

    @http.route(['/pos_qr/notification'], type='http', auth='public', methods=['POST'], csrf=False)
    def payment_callback(self, **kw):
        data = request.httprequest.data
        # print(request.httprequest.host)
        # print(request.httprequest.host_url)
        # print(request.httprequest.remote_addr)
        # print(request.httprequest.remote_user)

        result = json.loads(data.decode('utf-8'))

        if result.get('transactionId'):
            # print("\n\n SCB: Callback: data", data)
            request.env["bus.bus"]._sendone(
                f"scb_payment_callback", "PAYMENT_CALLBACK", data
            )

        headers = {'Content-Type': 'application/json'}
        response = {
            "resCode": "00",
            "resDesc ": "success",
            "transactionId": result.get('transactionId'),
        }

        return http.Response(json.dumps(response), headers=headers)
