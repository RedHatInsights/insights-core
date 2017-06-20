import insights.client as client

'''
Get version
'''
print '================'
print 'Getting version'
print '---------------'
print client.get_version()
print ''


'''
Get options
'''
client_config, client_options = client.parse_options()
print '==============='
print 'Getting Config'
print '--------------'
print ''
for config in client_config.items('insights-client'):
    print config
print ''
print '================'
print 'Getting Options'
print '----------------'
print client_options
print ''

'''
Fetch the new egg
'''
new_egg = client.fetch('https://raw.githubusercontent.com/RedHatInsights/insights-client/master/insights-core.egg')
verification = client.verify(new_egg)
print '============'
print 'New egg'
print '------------'
print ''
print 'New egg path: %s' % (new_egg)
print 'New egg GPG: %s' % (verification)
print ''


'''
Fetching new rules
'''
new_rules = client.fetch_rules()
print '============'
print 'New rules'
print '---------'
print ''
print new_rules


'''
Collect stuff
'''
print '================'
print 'Collecting'
print '---------'
collection = client.collect(options={'verbose': True})
print collection
print ''


'''
Upload stuff
'''
print '==============='
print 'Uploading'
print '---------'
upload = client.upload(collection)
print upload
print ''
