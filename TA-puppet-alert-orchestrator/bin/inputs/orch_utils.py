import configparser

def list_accounts():
  config = configparser.ConfigParser()
  config.read('/opt/splunk/etc/apps/TA-puppet-alert-actions/local/ta_puppet_alert_actions_account.conf')
  userlist = []

  for stanza in config:
    if config.has_option(stanza,"username"):
      account = config[stanza]['username']
      userlist.append(account)

  return userlist
