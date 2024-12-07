import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
  setup() {
    super.setup();
    this.env.services.bus_service.addChannel("scb_payment_callback");
    this.env.services.bus_service.subscribe("PAYMENT_CALLBACK", (data) => {
      var qr_data = this.currentOrder.getQRdata();
      if (qr_data && qr_data.scb_config_id) {
        var json_data = JSON.parse(data);
        console.log("PAYMENT SCREEN json_data >>>>>>> ", json_data);
        if (
          qr_data.ref1 == json_data.billPaymentRef1 &&
          qr_data.ref2 == json_data.billPaymentRef2 &&
          qr_data.ref3 == json_data.billPaymentRef3
        ) {
          json_data["qrRawData"] = qr_data.qrRawData;
          json_data["scb_config_id"] = qr_data.scb_config_id;
          json_data["qr_status"] = "paid";
          this.currentOrder.setTransactionDetails(json_data);
          if (this.selectedPaymentLine) {
            this.selectedPaymentLine.set_payment_status("done");
            this.validateOrder(false);
          }
        }
      }
    });
    this.env.services.bus_service.start();
  },
  async addNewPaymentLine(paymentMethod) {
    var result = await this.pos.data.call(
      "pos.payment.method",
      "get_scb_qr_fees",
      [[paymentMethod.id], this.currentOrder.get_due()]
    );
    if (result && result.fix_payment_product_id && result.fix_payment_fees) {
      let product = this.pos.models["product.product"].get(
        result.fix_payment_product_id
      );
      if (!product) {
        product = await this.pos.data.searchRead("product.product", [
          ["id", "=", result.fix_payment_product_id],
        ]);
        product = product.length > 0 && product[0];
      }
      let line = this.currentOrder.lines.find(
        (line) => line.product_id.id === product.id
      );
      if (line) {
        line.set_unit_price(result.fix_payment_fees);
      } else {
        await this.pos.addLineToCurrentOrder(
          {
            product_id: product,
            price_unit: result.fix_payment_fees,
          },
          {}
        );
      }
      this.currentOrder.setFixPaymentProductId(result.fix_payment_product_id);
    }
    return await super.addNewPaymentLine(paymentMethod);
  },
  deletePaymentLine(uuid) {
    const line = this.paymentLines.find((line) => line.uuid === uuid);
    if (line.payment_method_id.payment_method_type === "qr_code") {
      this.currentOrder.setShowQR(false);
      if (this.currentOrder.getFixPaymentProductId()) {
        let line = this.currentOrder.lines.find(
          (line) =>
            line.product_id.id === this.currentOrder.getFixPaymentProductId()
        );
        if (line) {
          line.delete();
          this.currentOrder.setFixPaymentProductId(false);
        }
      }
    }
    super.deletePaymentLine(uuid);
  },
});
