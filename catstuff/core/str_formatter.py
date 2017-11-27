from catstuff.core.manager import CSPluginManager
import re

def CSStrConstructor(remap=None):
    """
    Constructs the CSStr object for string formatting
    :param remap: if multiple classes contain the same attribute, use this to specify which class to inherit from
    {'attr': 'plugin_name'}
    :type dict
    :return:
    :rtype: CSStr
    """
    if remap is None:
        remap = {}
    assert isinstance(remap, dict)
    manager = CSPluginManager()
    base_list = []
    dict_ = {}

    # Construct the base settings
    for plugin in manager.getPluginsOfCategory('StrMethod'):
        base_list.append(plugin.plugin_object.__class__)
        dict_.update(plugin.plugin_object.__class__.__dict__)
    # Manual attribute inheritance specification
    for attr, plugin_name in remap.items():
        plugin = manager.getPluginByName(plugin_name, 'StrMethod')
        try:
            value = plugin.plugin_object.__class__.__dict__[attr]
            dict_.update({attr: value})
        except AttributeError:
            # TODO: raise "plugin does not exist"
            raise
        except KeyError:
            print("{plugin} does not have {attr} attribute".format(plugin=plugin_name, attr=attr))

    bases = tuple(base_list)
    return type('CSStr', bases, dict_)

# TODO: allow functions to operate on literal strings
# TODO: allow python formatter to be used on templates

class Template:
    """ Custom string template parser"""
    '''
    string.Template wont work since it uses regex which creates the largest possible substring
    This won't work when parsing a statement like
        $foo.func(arg, space_after_comma, 'string_argument') $var2.f1().f3()
    since arguments can be anything
    '''

    def __init__(self, template: str):
        var_parser = re.compile('\$[a-z][_a-zA-Z]*')

        self.template = template
        vars = var_parser.finditer(template)

        self._vars = []
        self._func = {}
        for var in vars:
            self._vars.append(var.group())

            func_list = []
            for func, args in find_funcs(template[var.start():])

            self._func.update({var: func_list})

def find_funcs(substring):
    """ Finds all the functions on a template substring"""
    '''
    Templates are defined by 
        $var_name.f1(f1_args).f2(f2_args)
    where '$' is the template delimeter and functions operate on the variable
    and are dot separated.
    Functions operate left to right
    '''
    assert substring[0] == '$', 'substring must start with $ delimeter'
    

test = Template('$foo.f1() $bar')
print(test)
print(test._vars)
print(test._func)