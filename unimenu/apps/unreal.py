import unreal
from unimenu.apps._abstract import MenuNodeAbstract


class MenuNodeUnreal(MenuNodeAbstract):

    @property
    def _default_root_parent(self):
        # Default menu root
        parent_path = "LevelEditor.MainMenu"

        # Optional root
        if self.kwargs.get('root_menu'):
            # full list of ui names here https://dev.epicgames.com/community/snippets/exo/unreal-engine-editor-ui-menu-names
            parent_path = f"{self.kwargs['root_menu']}"

        # Extend the root
        if self.parent_path:
            parent_path = f"{parent_path}.{self.parent_path}"

        unreal_menus = unreal.ToolMenus.get()
        parent_menu = unreal_menus.find_menu(parent_path)
        return parent_menu

    def setup(self, parent_app_node=None, backlink=True):
        super().setup(parent_app_node=parent_app_node, backlink=backlink)

        # post setup
        unreal_menus = unreal.ToolMenus.get()
        unreal_menus.refresh_all_widgets()

    def _setup_sub_menu(self, parent_app_node=None) -> unreal.ToolMenu:
        # Default Section
        target_section_name = "PythonTools"

        if self.kwargs.get('menu_section'):
            # change target section
            target_section_name = self.kwargs['menu_section']

        return parent_app_node.add_sub_menu(
            owner=parent_app_node.menu_name,
            section_name=target_section_name,
            name=self.id,  # todo check if needs to be unique like in add_to_menu
            label=self.label,  # todo add label support
            tool_tip=self.tooltip
        )

    def _setup_menu_item(self, parent_app_node=None) -> unreal.ToolMenuEntry:
        """add a menu item to the script menu"""
        entry = unreal.ToolMenuEntry(
            name=self.id,  # this needs to be unique! if not set, it's autogenerated
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST),
        )
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
            entry.set_icon(self.icon)  # naive implementation todo improve

        parent_app_node.add_menu_entry("Scripts", entry)  # always returns None
        return entry

    def _setup_separator(self, parent_app_node=None):
        # todo not working yet
        """add a separator to the script menu"""
        # see https://docs.unrealengine.com/4.27/en-US/PythonAPI/class/ToolMenu.html
        # todo what is diff with dynamic section?
        return parent_app_node.add_section(section_name=self.label + "_section", label=self.label + "_label")

    def teardown(self):
        """remove from menu"""
        raise NotImplementedError("not yet implemented")
