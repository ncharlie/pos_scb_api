import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
  setShowQR(show_qr) {
    this.show_qr = show_qr;
  },
  getShowQR() {
    return this.show_qr;
  },
  setFixPaymentProductId(fix_payment_product_id) {
    this.fix_payment_product_id = fix_payment_product_id;
  },
  getFixPaymentProductId() {
    return this.fix_payment_product_id;
  },
  getCustomerDisplayData() {
    var res = super.getCustomerDisplayData();
    res.show_qr = this.getShowQR();
    res.qr_data = this.getQRdata() ? this.getQRdata().qrImage : false;
    res.qr_timer = this.getQRdata() ? this.getQRdata().qr_timer : false;
    res.scb_name = this.getQRdata() ? this.getQRdata().scb_config_name : false;
    res.qr_amount =
      this.getQRdata() && this.getQRdata().format_amount
        ? this.getQRdata().format_amount
        : false;
    res.qr_generate_time =
      this.getQRdata() && this.getQRdata().qr_generate_time
        ? this.getQRdata().qr_generate_time
        : false;
    return res;
  },
  setQRdata(qr_data) {
    this.qr_data = qr_data;
  },
  getQRdata() {
    return this.qr_data;
  },
  setTransactionDetails(scb_transaction_details) {
    this.scb_transaction_details = scb_transaction_details;
  },
  getTransactionDetails() {
    return this.scb_transaction_details;
  },
});
