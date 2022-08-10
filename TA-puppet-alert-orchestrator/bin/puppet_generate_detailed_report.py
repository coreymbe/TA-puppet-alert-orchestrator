
# encoding = utf-8
# Always put this line at the beginning of this file
import ta_puppet_alert_actions_declare

import os
import sys

from alert_actions_base import ModularAlertBase
import modalert_puppet_generate_detailed_report_helper

class AlertActionWorkerpuppet_generate_detailed_report(ModularAlertBase):

    def __init__(self, ta_name, alert_name):
        super(AlertActionWorkerpuppet_generate_detailed_report, self).__init__(ta_name, alert_name)

    def validate_params(self):

        if not self.get_global_setting("puppet_enterprise_console"):
            self.log_error('puppet_enterprise_console is a mandatory setup parameter, but its value is None.')
            return False

        if not self.get_global_setting("puppet_default_user"):
            self.log_error('puppet_default_user is a mandatory setup parameter, but its value is None.')
            return False

        if not self.get_global_setting("splunk_hec_url"):
            self.log_error('splunk_hec_url is a mandatory setup parameter, but its value is None.')
            return False

        if not self.get_global_setting("splunk_hec_token"):
            self.log_error('splunk_hec_token is a mandatory setup parameter, but its value is None.')
            return False
        return True

    def process_event(self, *args, **kwargs):
        status = 0
        try:
            if not self.validate_params():
                return 3
            status = modalert_puppet_generate_detailed_report_helper.process_event(self, *args, **kwargs)
        except (AttributeError, TypeError) as ae:
            self.log_error("Error: {}. Please double check spelling and also verify that a compatible version of Splunk_SA_CIM is installed.".format(str(ae)))
            return 4
        except Exception as e:
            msg = "Unexpected error: {}."
            if e:
                self.log_error(msg.format(str(e)))
            else:
                import traceback
                self.log_error(msg.format(traceback.format_exc()))
            return 5
        return status

if __name__ == "__main__":
    exitcode = AlertActionWorkerpuppet_generate_detailed_report("TA-puppet-alert-actions", "puppet_generate_detailed_report").run(sys.argv)
    sys.exit(exitcode)
