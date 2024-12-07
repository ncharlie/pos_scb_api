import { CustomerDisplay } from "@point_of_sale/customer_display/customer_display";
import { CustomerDisplayQRPopup } from "@pos_scb_api/app/utils/customer_display_qr_popup/customer_display_qr_popup";

import { patch } from "@web/core/utils/patch";

patch(CustomerDisplay.prototype, {
  showQR() {
    if (this.order.scb_name) {
      this.dialog.add(CustomerDisplayQRPopup, {
        qr_details: {
          qr_code: "data:image/png;base64," + this.order.qr_data,
          qr_timer: this.order.qr_timer,
          scb_name: this.order.scb_name,
          qr_amount: this.order.qr_amount,
          qr_generate_time: this.order.qr_generate_time,
        },
      });
    }
  },
  hidePopup() {
    this.dialog.closeAll();
  },
});
