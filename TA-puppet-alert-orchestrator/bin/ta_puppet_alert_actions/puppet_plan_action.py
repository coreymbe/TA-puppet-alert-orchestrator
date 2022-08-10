# encoding = utf-8

import pie
import json

# # create our alert object to build the actual report
# helper.log_info("Assembling alert data")
# alert = {}
# alert['global'] = {}
# alert['param'] = {}
# alert['global']['puppet_enterprise_console'] = puppet_enterprise_console
# alert['global']['splunk_hec_url'] = splunk_hec_url
# alert['global']['bolt_user'] = puppet_bolt_user
# alert['global']['bolt_user_pass'] = puppet_bolt_user_pass
# alert['global']['puppet_bolt_server'] = notnone(puppet_enterprise_console, puppet_bolt_server, helper)
# alert['global']['puppet_action_hec_token'] = notnone(splunk_hec_token, puppet_action_hec_token, helper)
# alert['global']['timeout'] = timeout

# # Load the alert specific settings that are really the plan we're running
# alert['param']['bolt_target'] = bolt_target
# alert['param']['plan_name'] = plan_name
# alert['param']['plan_parameters'] = plan_parameters
# alert['param']['puppet_environment'] = puppet_environment


def run_puppet_plan(alert, helper):
  # load our URLs, we generate possible ones assuming the console hostname is valid
  # however if a user provides their own pdb or bolt url it goes here
  # this also allows for us to add an int_proxy feature in the future
  endpoints = pie.util.getendpoints(alert['global']['puppet_enterprise_console'])
  rbac_url = endpoints['rbac']
  orch_url = endpoints['bolt']
  pe_console = endpoints['console_hostname']

  puppet_environment = alert['param']['puppet_environment']
  splunk_hec_url = alert['global']['splunk_hec_url']
  puppet_action_hec_token = alert['global']['puppet_action_hec_token']
  plan_name = alert['param']['plan_name']
  plan_parameters = alert['param']['plan_parameters']

  message = {
    'message': 'Running plan {} on {} '.format(plan_name,pe_console),
    'action_type': 'plan',
    'action_name': plan_name,
    'action_parameters': plan_parameters,
    'action_state': 'starting',
    'pe_console': pe_console,
  }

  helper.log_debug(message)
  pie.hec.post_action(message, pe_console, splunk_hec_url, puppet_action_hec_token)

  rbac_user = alert['global']['puppet_user']
  rbac_user_pass = alert['global']['puppet_user_pass']

  if alert['global']['timeout'] is not None and alert['global']['timeout'] is not '':
    plan_timeout = alert['global']['timeout']
  else:
    plan_timeout = 600

  try:
    token_lifetime = int(plan_timeout) * 2
  except Exception as e:
    helper.log_error("Timeout must be an integer, '{}' was provided instead".format(plan_timeout))

 # Check if the user is configured with an RBAC token or Password:
  if alert['global']['pe_token']:
    auth_token = rbac_user_pass
  else:
    auth_token = pie.rbac.genauthtoken(rbac_user,rbac_user_pass,'TA-puppet-alert-actions',rbac_url, timeout=token_lifetime)

  # note: parameters is expected as a text string, not json, so in sample alert json must be represented as:
  # "plan_parameters": "{ \"target\": \"puppet.angrydome.org\", \"service\": \"puppet\"}"

  try:
    jobid = pie.orch.reqplan(plan_name,auth_token,puppet_environment,orch_url,parameters=plan_parameters)
    helper.log_debug('Puppet plan successfully requested with ID of {}'.format(jobid))
  except Exception as e:
    helper.log_error('Unable to request Puppet plan before {}'.format(e))

  try:
    jobresults = pie.orch.getplanresult(jobid, auth_token, orch_url, timeout=plan_timeout)
    helper.log_debug('Puppet plan successfully retrieved with state of {}'.format(jobresults['state']))
  except Exception as e:
    helper.log_error('Plan failed before {}'.format(e))

  # While plans can be run against multiple targets the TargetSpec is typically a parameter named either 'target(s)' or 'nodes'. Although it can be named something entirely different.
  # As such, we are currently reporting on the overall status of the Plan (i.e. If it succeeds on 2 nodes and fails on 1 it will be considered a 'failure').
  # This also means that rmessage['message'] will include the PE Console hostname as opposed to each target the Plan was ran against.
  rmessage = message
  rmessage['action_state'] = jobresults['state']
  rmessage['joburl'] = 'https://{}/#/orchestration/plans/plan/{}'.format(pe_console,jobid)
  rmessage['pe_console'] = pe_console
  rmessage['result'] = jobresults['result']
  rmessage['start_timestamp'] = jobresults['created_timestamp']
  rmessage['duration'] = jobresults['duration']
  rmessage['finish_timestamp'] = jobresults['finished_timestamp']

  if rmessage['action_state'] == 'success':
    rmessage['message'] = 'Successfully ran plan {} on {} '.format(plan_name,pe_console)
    helper.log_debug(rmessage['message'])
  elif jobresults['state'] == 'failure':
    rmessage['message'] = 'Failed to run plan {} on {} '.format(plan_name,pe_console)
    helper.log_error(rmessage['message'])
  else:
    rmessage['message'] = 'Something happened to plan {} on {} that we have no idea about'.format(plan_name,pe_console)
    helper.log_error(rmessage['message'])

  pie.hec.post_action(rmessage, pe_console, splunk_hec_url, puppet_action_hec_token)

# this is our interactive load option
# assumes you're running this library directly from the command line
# cat example_alert.json | python $thisfile.py

if __name__ == "__main__":
  import sys
  import json

  alert = json.load(sys.stdin)
  try:
    run_puppet_plan_custom(alert)
  except KeyError:
    run_puppet_plan(alert)
