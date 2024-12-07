import { Dialog } from "@web/core/dialog/dialog";
import { useState, Component, onWillStart, onWillDestroy } from "@odoo/owl";

export class CustomerDisplayQRPopup extends Component {
  static template = "pos_scb_api.CustomerDisplayQRPopup";
  static components = { Dialog };
  static props = {
    qr_details: { type: Object, optional: true },
  };
  static defaultProps = {
    qr_details: null,
  };
  setup() {
    super.setup();
    var remaining_duration = false;
    if (this.props.qr_details.qr_generate_time) {
      remaining_duration = Math.floor(
        this.props.qr_details.qr_generate_time - new Date()
      );
    }
    this.state = useState({
      qr_details: this.props.qr_details,
      duration: remaining_duration
        ? Math.floor(remaining_duration / 1000)
        : false,
      scb_name: this.props.qr_details.scb_name || false,
      qr_amount: this.props.qr_details.qr_amount,
    });
    onWillStart(async () => {
      if (this.state.duration) {
        this._runTimer();
      }
    });
    onWillDestroy(() => clearTimeout(this.timer));
  }
  _runTimer() {
    this.timer = setTimeout(() => {
      if (this.state.duration != 0) {
        this.state.duration -= 1;
        this._runTimer();
      } else {
        this.props.close();
      }
    }, 1000);
  }
}
