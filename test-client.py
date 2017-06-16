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
Collect stuff
'''
print '================'
print 'Collecting'
print '---------'
collection = client.collect()
print collection
print ''