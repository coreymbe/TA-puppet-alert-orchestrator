# encoding = utf-8
import pie
import collections
import time

# alert['global']['puppet_enterprise_console'] = helper.get_global_setting("puppet_enterprise_console")
# alert['global']['puppet_read_user'] = helper.get_global_setting("puppet_read_user")
# alert['global']['puppet_read_user_pass'] = helper.get_global_setting("puppet_read_user_pass")
# alert['global']['splunk_hec_url'] = helper.get_global_setting("splunk_hec_url")
# alert['global']['splunk_hec_token'] = helper.get_global_setting("splunk_hec_token")
# alert['global']['bolt_user'] = helper.get_global_setting("bolt_user")
# alert['global']['bolt_user_pass'] = helper.get_global_setting("bolt_user_pass")
# alert['global']['puppet_bolt_server'] = helper.get_global_setting("puppet_bolt_server")
# alert['global']['puppet_action_hec_token'] = helper.get_global_setting("puppet_action_hec_token")
# alert['global']['puppet_db_url'] = helper.get_global_setting("puppet_db_url")

# alert['param']['transaction_uuid'] = helper.get_param("transaction_uuid")

# events = helper.get_events()
# for event in events:
#     alert['result'] = json.loads(event)


def build_report_query(uuid):
  report_elements = [
    'hash', 
    'status', 
    'puppet_version', 
    'report_format', 
    'catalog_uuid', 
    'job_id', 
    'cached_catalog_status', 
    'configuration_version', 
    'environment', 
    'corrective_change', 
    'noop', 
    'noop_pending', 
    'certname', 
    'transaction_uuid', 
    'code_id', 
    'resource_events', 
    'producer_timestamp', 
    'producer', 
    'start_time', 
    'end_time', 
    'receive_time', 
    'logs', 
    'metrics'
  ]

  joined_elements = ', '.join(report_elements)

  query_string = {}
  query_string['query'] = 'reports[{}] {{ transaction_uuid = "{}" }}'.format(joined_elements, uuid)

  return query_string

def parse_metrics(report_metrics):
  mdict = collections.defaultdict(dict)

  for m in report_metrics['data']:
    mdict[m['category']][m['name']] = m['value']
    
  return dict(mdict)

def run_report_generation(alert, transaction_uuids, helper):
  # Begin breaking down Alert dictionary
  # load our URLs, we generate possible ones assuming the console hostname is valid
  # however if a user provides their own pdb or bolt url it goes here
  # this also allows for us to add an int_proxy feature in the future
  endpoints = pie.util.getendpoints(alert['global']['puppet_enterprise_console'])
  rbac_url = endpoints['rbac']

  pdb_endpoint = pie.util.getendpoints(alert['global']['puppet_db_url'])
  pdb_url = pdb_endpoint['pdb']
  
  splunk_hec_url = alert['global']['splunk_hec_url']
  puppet_action_hec_token = alert['global']['puppet_action_hec_token']

  rbac_user = alert['global']['puppet_user']
  rbac_user_pass = alert['global']['puppet_user_pass']

  if alert['global']['timeout'] is not None and alert['global']['timeout'] is not '':
    task_timeout = alert['global']['timeout']
  else:
    task_timeout = 360

  try:
    token_lifetime = int(task_timeout) * 2
  except Exception as e:
    helper.log_error("Timeout must be an integer, '{}' was provided instead".format(task_timeout))

 # Check if the user is configured with an RBAC token or Password:
  if alert['global']['pe_token']:
    auth_token = rbac_user_pass
  else:
    auth_token = pie.rbac.genauthtoken(rbac_user,rbac_user_pass,'TA-puppet-alert-actions',rbac_url, timeout=token_lifetime)

  helper.log_info("Attempting to generate and submit {} detailed reports".format(len(transaction_uuids)))
  for uuid in transaction_uuids:
    pql = build_report_query(uuid['transaction_uuid'])
    
    detailed_report = {}
    
    helper.log_debug("Attempting to lookup transaction_uuid {} for {}".format(uuid['transaction_uuid'],uuid['host']))

    try:
      detailed_report = pie.pdb.query(pql, pdb_url, auth_token)[0]
    except Exception as e:
      helper.log_error("Puppet DB query {} returned no results: error = {}".format(pql, e))
    
    repo_hash = detailed_report['hash']
    detailed_report['url'] = 'https://{}/#/inspect/report/{}/events'.format(uuid['pe_console'],repo_hash)
    detailed_report['pe_console'] = uuid['pe_console']

    parsed_metrics = parse_metrics(detailed_report['metrics'])
    detailed_report['metrics'] = parsed_metrics

    helper.log_debug("Attempting to submit detailed report for {}".format(uuid['transaction_uuid']))
    pie.hec.post_report(detailed_report,splunk_hec_url,puppet_action_hec_token)
    # here we may want to sleep just to prevent from clobbering pdb
    time.sleep(2)
  
  helper.log_info("Finished submitting reports")

# this is our interactive load option
# assumes you're running this library directly from the command line
# cat example_alert.json | python $thisfile.py

if __name__ == "__main__":
  import sys
  import json
  
  alert = json.load(sys.stdin)
  
  #run_report_generation(alert)
