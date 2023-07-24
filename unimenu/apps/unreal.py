import unreal
from unimenu.apps._abstract import MenuNodeAbstract
import logging


class MenuNodeUnreal(MenuNodeAbstract):

    @property
    def _default_root_parent(self):
        if not self.parent_path:
            self.parent_path = "LevelEditor.MainMenu"

        unreal_menus = unreal.ToolMenus.get()
        parent_menu = unreal_menus.find_menu(self.parent_path)
        return parent_menu

    def setup(self, parent_app_node: unreal.ToolMenu = None, backlink=True) -> unreal.ToolMenu:
        backlink = False # todo, override to false unreal doesnt support backlink yet
        app_node = super().setup(parent_app_node=parent_app_node, backlink=backlink)

        # post setup
        unreal_menus = unreal.ToolMenus.get()
        unreal_menus.refresh_all_widgets()

        return app_node

    def _setup_sub_menu(self, parent_app_node: unreal.ToolMenu = None) -> unreal.ToolMenu:
        """
        add a submenu to the script menu

        parent_app_node: the Unreal parent menu to parent the new menu to
        """
        if not self.check_unique_name():
            raise Exception(f"Menu '{self.label}' already exists, stopping submenu setup")

        # self.kwargs for unreal.ToolMenu.add_sub_menu
        self.kwargs.setdefault("section_name", "PythonTools")

        return parent_app_node.add_sub_menu(
            owner=parent_app_node.menu_name,
            name=self.id,  # todo check if needs to be unique like in add_to_menu
            label=self.label,  # todo add label support
            tool_tip=self.tooltip,
            **self.kwargs,
        )

    def _setup_menu_item(self, parent_app_node: unreal.ToolMenu = None) -> unreal.ToolMenuEntry:
        """
        add a menu item to the script menu

        parent_app_node: the Unreal parent menu to parent the new menu to
        """
        if not self.check_unique_name():
            raise Exception(f"Menu item '{self.label}' already exists, stopping menu item setup")

        # self.kwargs default values for unreal.ToolMenuEntry
        self.kwargs.setdefault("type", unreal.MultiBlockType.MENU_ENTRY)
        self.kwargs.setdefault("insert_position", unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST))

        # convenient hack to support kwargs for both unreal.ToolMenuEntry,
        # and setting section_name for unreal.ToolMenu.add_sub_menu
        # same kwarg name as section_name kwarg from add_sub_menu
        section_name = self.kwargs.pop("section_name", "Scripts")
        style_set = self.kwargs.pop("style_set_name", "EditorStyle")

        # name kwarg needs to be unique! if not set, it's autogenerated
        entry = unreal.ToolMenuEntry(name=self.id, **self.kwargs)

        if self.label:
            entry.set_label(self.label)
        if self.command:
            entry.set_string_command(
                type=unreal.ToolMenuStringCommandType.PYTHON,
                string=self.command,
                custom_type=unreal.Name("_placeholder_"),
            )  # hack: unsure what custom_type does, but it's needed
        if self.tooltip:
            entry.set_tool_tip(self.tooltip)
        if self.icon:
            # it is not possible to register custom icons with Python, can only use the built-in icons
            # Icon's are here ...\Engine\Content\Editor\Slate\Icons - look for the icon name here
            # style_names can be found here ...\Engine\Source\Editor\EditorStyle\Private\SlateEditorStyle.cpp - look for the name here
            # e.g. Set( "BlueprintEditor.AddNewMacroDeclaration", new IMAGE_BRUSH( "Icons/icon_Blueprint_AddMacro_40px", Icon40x40) );
            #            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^         <--         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            entry.set_icon(style_set, style_name=self.icon)

        parent_app_node.add_menu_entry(section_name, entry)  # always returns None
        return entry

    def _setup_separator(self, parent_app_node: unreal.ToolMenu = None) -> None:
        """
        add a separator to the script menu

        parent_app_node: the Unreal parent menu to parent the new menu to
        """
        section_name = self.kwargs.pop("section_name", self.label + "_section")
        return parent_app_node.add_section(section_name=section_name, label=self.label, **self.kwargs)

    def teardown(self):
        """remove from menu"""
        raise NotImplementedError("not yet implemented")

    def check_unique_name(self):
        """check if menu exists already, return True if it does not exist"""
        # unreal_menus.find_menu("LevelEditor.MainMenu.Tools")
        unreal_menus = unreal.ToolMenus.get()
        #
        exists = unreal_menus.find_menu(self.get_name_path())
        if exists:
            logging.warning(f"Menu already exists: '{self.get_name_path()}'")
            parent_label = self.parent.label if self.parent else None
            logging.warning(f"Parent is '{parent_label}'")
            return False
        else:
            return True

    def get_name_path(self):
        # e.g. return 'LevelEditor.MainMenu.Tools' if self.id is 'Tools'
        if self.parent:
            return self.parent.get_name_path() + "." + self.id
        elif self.parent_path:
            return self.parent_path + "." + self.id
        else:
            return self.id