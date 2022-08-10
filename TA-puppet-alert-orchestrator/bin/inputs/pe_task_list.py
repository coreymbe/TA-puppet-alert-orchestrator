import sys
import os

PATHS = ['/opt/splunk/etc/apps/TA-puppet-alert-actions/bin/ta_puppet_alert_actions/aob_py3','/opt/splunk/etc/apps/TA-puppet-alert-actions/bin/ta_puppet_alert_actions']

for path in PATHS:
  sys.path.append(path)

from splunk_aoblib.setup_util import Setup_Util
import pie
import orch_utils

account_list = orch_utils.list_accounts()
sk = sys.stdin.readline().strip()
uri = "https://localhost:8089"

#f = open("splunk_account_creds.txt", "w")
#f.write(sk)
#f.close()

helper = Setup_Util(uri,sk)

inputs = {}
inputs['hec_token'] = helper.get_customized_setting("splunk_hec_token")
inputs['hec_url'] = helper.get_customized_setting("splunk_hec_url")
inputs['pe_console'] = helper.get_customized_setting("puppet_enterprise_console")

try:
  for user in account_list:
    account = helper.get_credential_by_username(user)
    try:
      tasklist = pie.bolt.get_tasklist(inputs['pe_console'],account['password'])
      for task in tasklist:
        id = task['id']
        prmtr = pie.bolt.get_actionparams(id,account['password'])
        message = {
          'permitted': task['permitted'],
          'task_meta': None,
          'task_name': task['name'],
          'task_params': [],
          'user': user,
        }
        pmessage = message
        try:
          pmessage['task_meta'] = prmtr['metadata']['parameters']
          for param in pmessage['task_meta']:
            pmessage['task_params'].append(param)
          try:
            host = inputs['pe_console'].replace("https://", "")
            hec_url = inputs['hec_url']
            hec_token = inputs['hec_token']
            r = pie.hec.post_action(pmessage,host,hec_url,hec_token)
          except Exception as e:
            sys.stderr.write("TA-puppet-alert-actions: {}".format(e))
        except Exception as e:
          sys.stderr.write("TA-puppet-alert-actions: {}".format(e))
    except Exception as e:
      sys.stderr.write("TA-puppet-alert-actions: {}".format(e))
except Exception as e:
  sys.stderr.write("TA-puppet-alert-actions: {}".format(e))
