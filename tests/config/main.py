import catstuff.config.config as config

path = 'sample.yml'
test = config.Config(path)

print('Raw dump')
print(test.raw_dump())

print('--------------------')
print('Groups')
print(test.groups)

print('--------------------')
print('Default group config')
print(test.get_group_config('default'))
print('--------------------')
print('group1.subgroup2 config')
try:
    print(test.get_group_config('group1.subgroup2'))
except KeyError as e:
    print(e)

print('--------------------')
print('imported configs')
test.import_config(r'C:\Users\S\PycharmProjects\catstuff\tests\config\sample.yml')  # file import
test.import_config(r'C:\Users\S\PycharmProjects\catstuff\tests\config')  # dir import
test.import_config(r'C:\Users\S\PycharmProjects\catstuff\tests\config', exclude=('sample.yml',))  # dir import -- exclude
test.import_config(r'C:\Users\S\PycharmProjects\catstuff\tests')  # dir import -- nothing found
test.import_config(r'C:\Users\S\PycharmProjects\catstuff\tests', max_depth=1)  # dir import -- may find more than one