{
    "name": "POS SCB Payment",
    "version": "1.0",
    "category": "Sales/Point of Sale",
    'author': "Chanuwat na Chiengmai",
    "license": "LGPL-3",
    'installable': True,
    'application': False,
    "auto_install": False,
    "depends": ["base", "point_of_sale", "pos_online_payment"],
    "summary": "Integrate your POS with SCB bill payment API",
    "description": """
        SCB Payment Integration
    """,
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/scb_payment_configuration_view.xml",
        "views/pos_scb_payment_history_view.xml",
        "views/pos_order_view.xml"
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            'pos_scb_api/static/src/app/pos_app.js',
            'pos_scb_api/static/src/app/models/pos_order.js',
            'pos_scb_api/static/src/app/models/pos_payment.js',
            'pos_scb_api/static/src/app/models/scb_payment_configuration.js',
            'pos_scb_api/static/src/app/utils/qr_code_popup/qr_code_popup.js',
            'pos_scb_api/static/src/app/screens/payment_screen/payment_screen.js',
            'pos_scb_api/static/src/app/screens/payment_screen/payment_line/payment_lines.xml',
            'pos_scb_api/static/src/app/utils/qr_code_popup/qr_code_popup.xml',
            'pos_scb_api/static/src/app/store/pos_store.js',
        ],
        'point_of_sale.customer_display_assets': [
            'pos_scb_api/static/src/customer_display/customer_display.js',
            'pos_scb_api/static/src/customer_display/customer_display.xml',
            'pos_scb_api/static/src/app/utils/customer_display_qr_popup/customer_display_qr_popup.js',
            'pos_scb_api/static/src/app/utils/customer_display_qr_popup/customer_display_qr_popup.xml',
        ],
    },
}
