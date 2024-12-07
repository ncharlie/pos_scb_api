import { PosStore } from "@point_of_sale/app/store/pos_store";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { QRPopup } from "@point_of_sale/app/utils/qr_code_popup/qr_code_popup";
import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { ConnectionLostError } from "@web/core/network/rpc";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
  async showQR(payment) {
    var self = this;
    let qr;
    let res;
    var qr_time_update = false;
    try {
      if (!this.isClicked) {
        this.isClicked = true;
      } else {
        return;
      }
      const current_order = this.get_order();
      var old_qr_info = current_order.getQRdata();
      var remaining_duration = false;
      if (old_qr_info && old_qr_info.qr_generate_time) {
        remaining_duration = Math.floor(
          old_qr_info.qr_generate_time - new Date()
        );
      }
      if (remaining_duration <= 0) {
        old_qr_info = {};
      }
      if (
        old_qr_info &&
        old_qr_info.amount == payment.amount &&
        old_qr_info.qrImage &&
        old_qr_info.qrRawData
      ) {
        res = old_qr_info;
      } else {
        res = await this.data.call("pos.payment.method", "get_qr_code", [
          [payment.payment_method_id.id],
          payment.amount,
          payment.pos_order_id.name,
          payment.pos_order_id.name,
          this.currency.id,
          payment.pos_order_id.partner_id?.id,
        ]);
        qr_time_update = true;
      }
      if (typeof res == "string") {
        qr = res;
        current_order.setQRdata({
          qrImage: res,
          format_amount: this.chrome.env.utils.formatCurrency(payment.amount),
        });
      } else if (typeof res == "object") {
        if (qr_time_update) {
          var currentDate = new Date();
          Object.assign(res, {
            format_amount: this.chrome.env.utils.formatCurrency(payment.amount),
            qr_generate_time: currentDate.setSeconds(
              currentDate.getSeconds() + res.qr_timer
            ),
          });
        }
        current_order.setQRdata(res);
        qr = res.qrImage;
      }
      this.isClicked = false;
      this.chrome.sendOrderToCustomerDisplay(current_order, false);
    } catch (error) {
      console.log("error found");
      console.log(error);
      this.isClicked = false;
      qr = payment.payment_method_id.default_qr;
      if (!qr) {
        let message;
        if (error instanceof ConnectionLostError) {
          message = _t(
            "Connection to the server has been lost. Please check your internet connection."
          );
        } else {
          message = error.data.message;
        }
        this.env.services.dialog.add(AlertDialog, {
          title: _t("Failure to generate Payment QR Code"),
          body: message,
        });
        return false;
      }
    }
    payment.pos_order_id.chrome = this.chrome;
    return await ask(
      this.env.services.dialog,
      {
        title: payment.name,
        line: payment,
        order: payment.pos_order_id,
        qrCode: qr,
      },
      {},
      QRPopup
    );
  },
});
