import { registry } from "@web/core/registry";
import { Base } from "@point_of_sale/app/models/related_models";

export class ScbPaymentConfiguration extends Base {
  static pythonModel = "scb.payment.configuration";

  setup(vals) {
    super.setup(...arguments);
    //        this.name = 1;
    //        this.qr_code_raw_data = "1234567890";
    //        this.amount = 0.01;
    //        this.bank_transaction_ref = "202411063LOAzyKZyzYm4a6";
    //        this.customer_bank_ref = "014";
    //        this.customer_acc_no = "0987654321";
    //        this.customer_acc_name = "TestBiller1730302219";
  }
}

registry
  .category("pos_available_models")
  .add(ScbPaymentConfiguration.pythonModel, ScbPaymentConfiguration);
