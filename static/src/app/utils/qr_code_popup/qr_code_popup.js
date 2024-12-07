import { QRPopup } from "@point_of_sale/app/utils/qr_code_popup/qr_code_popup";
import { patch } from "@web/core/utils/patch";
import { useState, onWillStart, onWillDestroy } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

// this will patch static properties!!!
patch(QRPopup, {
  defaultProps: {
    ...QRPopup.defaultProps,
    title: _t("Mobile Banking"),
  },
});

// this is probably the usual case: patching a class method
patch(QRPopup.prototype, {
  setup() {
    super.setup(...arguments);
    var self = this;
    var remaining_duration = false;
    this.props.order.get_selected_paymentline().isCancelled = false;
    this.props.order.get_selected_paymentline().isTimerExpired = false;
    this.props.order.get_selected_paymentline().isConfirmed = false;
    if (this.props.order.getQRdata().qr_generate_time) {
      remaining_duration = Math.floor(
        this.props.order.getQRdata().qr_generate_time - new Date()
      );
    }
    this.state = useState({
      timerExpired: false,
      duration: remaining_duration
        ? Math.floor(remaining_duration / 1000)
        : false,
      scb_name: this.props.order.getQRdata()
        ? this.props.order.getQRdata().scb_config_name
        : false,
    });
    onWillStart(async () => {
      if (this.state.duration) {
        this._runTimer();
      }
    });
    onWillDestroy(async () => {
      clearTimeout(this.timer);
      this.props.order.setShowQR(false);
      this.props.order.chrome.sendOrderToCustomerDisplay(
        this.props.order,
        false
      );
    });
    this.env.services.bus_service.addChannel("scb_payment_callback");
    this.env.services.bus_service.subscribe("PAYMENT_CALLBACK", (data) => {
      if (this.props.order.getQRdata().scb_config_id) {
        var json_data = JSON.parse(data);
        console.log("QR POPUP json_data >>>>>>> ", json_data);
        if (
          this.props.order.getQRdata().ref1 == json_data.billPaymentRef1 &&
          this.props.order.getQRdata().ref2 == json_data.billPaymentRef2 &&
          this.props.order.getQRdata().ref3 == json_data.billPaymentRef3
        ) {
          this.props.order.getQRdata().qr_status = "paid";
          this._confirm();
          //                    this.props.order.get_selected_paymentline().set_payment_status("done");
          //                    this.props.close();
        }
      }
    });
    this.env.services.bus_service.start();
    this.props.order.setShowQR(true);
  },
  _runTimer() {
    this.timer = setTimeout(() => {
      if (this.state.duration != 0) {
        this.state.duration -= 1;
        this._runTimer();
      } else {
        this.props.order.get_selected_paymentline().isTimerExpired = true;
        this.props.close();
        this.props.order.setShowQR(false);
        this.callCancelApiRequest();
      }
    }, 1000);
  },
  async _cancel() {
    this.props.order.get_selected_paymentline().isCancelled = true;
    await this.callCancelApiRequest();
    this.props.order.setShowQR(false);
    this.props.order.setQRdata({});
    return super._cancel();
  },
  _confirm() {
    if (this.props.order && this.props.order.get_selected_paymentline()) {
      this.props.order.get_selected_paymentline().isCancelled = false;
      this.props.order.get_selected_paymentline().isConfirmed = true;
      var qr_data = this.props.order.getQRdata();
      if (
        !this.props.order.getTransactionDetails() &&
        qr_data &&
        qr_data.scb_config_name
      ) {
        qr_data["billPaymentRef1"] = qr_data["ref1"];
        qr_data["billPaymentRef2"] = qr_data["ref2"];
        qr_data["billPaymentRef3"] = qr_data["ref3"];
        qr_data["amount"] = this.props.line.amount;
        qr_data["qr_status"] = "confirmed_manually";
        delete qr_data["ref1"];
        delete qr_data["ref2"];
        delete qr_data["ref3"];
        this.props.order.setTransactionDetails(qr_data);
      }
    }
    return super._confirm();
  },
  callCancelApiRequest() {
    this.env.services.orm.call("pos.order", "cancel_api_request", []);
  },
});
