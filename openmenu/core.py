import json
import warnings
from pathlib import Path
from collections import namedtuple
import importlib
import pkgutil

# class DCC:
#     name = None
#     module = None
#     callback = None

# name: the name of the dcc, and also the name of the menu module
# name of module: a unique python module only available in that dcc
# callback: not sure if we need this
DCC = namedtuple('DCC', ['name', 'module'])


class DCCs:
    """DCCs supported by this module"""
    # dcc -> digital content creation (software)
    # dcc name = unique dcc module name

    BLENDER = DCC('blender', 'bpy')
    MAYA = DCC('maya', 'maya')  # pymel can be slow to import
    UNREAL = DCC('unreal', 'unreal')
    MAX = DCC('max', 'pymxs')
    KRITA = DCC('krita', 'krita')
    SUBSTANCE_DESIGNER = DCC('substance_designer', 'pysbs')
    SUBSTANCE_PAINTER = DCC('substance_painter', 'substance_painter')
    MARMOSET = DCC('marmoset', 'mset')

    ALL = [BLENDER, MAYA, UNREAL, KRITA, SUBSTANCE_PAINTER, MAX, MARMOSET]


def detect_dcc():
    for dcc in DCCs.ALL:
        try:
            __import__(dcc.module)
            print(f"OPENMENU: detected {dcc.name}")
            return dcc
        except ImportError:
            pass
    print("OPENMENU: no supported DCC detected")


def config_setup(path: (str, Path), dcc=None):
    """setup menu"""
    data = get_json_data(path) or get_yaml_data(path)
    return setup(data, dcc)


def setup(data, dcc=None):
    dcc = dcc or detect_dcc()
    module = importlib.import_module(f'openmenu.{dcc.name}')
    return module.setup_menu(data)


def get_json_data(config_path):
    path = str(config_path)
    if not path.lower().endswith('.json'):
        return

    with open(config_path) as file:
        data = json.load(file)
    return data


def get_yaml_data(config_path):
    path = str(config_path)
    if not path.lower().endswith('.yaml'):
        return

    import yaml

    with open(config_path) as file:
        data = yaml.load(file, Loader=yaml.SafeLoader)
    return data


def breakdown():
    """remove from menu"""
    raise NotImplementedError("not yet implemented")




# load all modules in a folder
# let user choose a function name to run on these modules
# hookup module and function name as callback to menu item
def module_setup(parent_module_name, parent_menu_name='', function_name='main', dcc=None):
    """
    create a menu for all modules in a folder,
    automatically keep your menu up to date with all tools in that folder

    note: ensure the folder is importable and in your environment path

    Args:
    parent_module: the module that contains all tools. e.g.:
                   cool_tools
                   ├─ __init__.py   (import cool_tools)
                   ├─ tool1.py      (import cool_tools.tool1)
                   └─ tool2.py      (import cool_tools.tool2)
    function_name: the function name to run on the module, e.g.: 'run', defaults to 'main'
                   if empty, call the module directly
    dcc: the dcc that contains the menu. if None, will try to detect dcc

    """

    parent_module = importlib.import_module(parent_module_name)

    # create dict for every module in the folder
    # label: the name of the module
    # callback: the function to run

    # todo support recursive folders -> auto create submenus

    items = []
    for module_finder, submodule_name, ispkg in pkgutil.iter_modules(parent_module.__path__):
        # skip private modules
        if submodule_name.startswith('_'):
            continue

        # to prevent issues with late binding
        # https://stackoverflow.com/questions/3431676/creating-functions-or-lambdas-in-a-loop-or-comprehension
        # first arg might be self, e.g. operator wrapped in blender
        def callback(self=None, _submodule_name=submodule_name, _function_name=function_name, *args, **kwargs):

            # todo only import the module after clicking in the menu
            submodule = module_finder.find_spec(_submodule_name).loader.load_module()

            # run the function on the module
            if _function_name:

                # same as getattr(submodule, function_name)(), but recursive:
                # if the dev provides attr.attr function name, recursively get the function
                attribute_names = _function_name.split('.')
                function = None
                _parent = submodule
                for attribute_name in attribute_names:
                    function = getattr(_parent, attribute_name)
                    _parent = function

                function()
            else:
                submodule()

        submodule_dict = {}
        submodule_dict['label'] = submodule_name
        submodule_dict['command'] = callback

        items.append(submodule_dict)

    data = {}
    if parent_menu_name:
        data['parent'] = parent_menu_name

    data['items'] = [{
        'label': parent_module.__name__ ,
        'items': items
    }]

    return setup(data, dcc)


