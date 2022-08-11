
[puppet_generate_detailed_report]
python.version = python3
param.puppet_enterprise_console = <string> Puppet Enterprise Console.
param.puppet_default_user = <string> User.
param.splunk_hec_url = <string> Splunk HEC URL.
param.splunk_hec_token = <string> Splunk HEC Token.
param.puppet_action_hec_token = <string> Action HEC Token.
param.puppet_db_url = <string> PuppetDB URL.
param.timeout = <string> Timeout.
param.pe_console = <string> PE Installation.

[puppet_run_task]
python.version = python3
param.action_target = <string> Host. Its a required parameter. Its default value is "$result.host$".
param.task_name = <string> Task. Its a required parameter.
param.task_parameters = <string> Task Parameters.
param.puppet_environment = <string> Puppet Environment. Its a required parameter. Its default value is production.
param.puppet_user = <string> Bolt User.
param.puppet_orch_server = <string> Orch. Services URL.
param.timeout = <string> Timeout.
param.splunk_hec_url = <string> Splunk HEC URL.
param.puppet_action_hec_token = <string> Action HEC Token.

[puppet_run_plan]
python.version = python3
param.plan_name = <string> Plan - Its a required parameter.
param.plan_parameters = <string> Plan Parameters.
param.puppet_environment = <string> Puppet Environment. Its a required parameter. Its default value is production.
param.puppet_user = <string> Bolt User.
param.puppet_orch_server = <string> Orch. Services URL.
param.timeout = <string> Timeout.
param.splunk_hec_url = <string> Splunk HEC URL.
param.puppet_action_hec_token = <string> Action HEC Token.

