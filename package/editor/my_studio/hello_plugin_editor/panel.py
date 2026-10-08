import infernux as inx


@inx.editor.editor_panel(
    "Hello Plugin",
    type_id="my_studio.hello_plugin.panel",
    title_key="my_studio.hello_plugin.panel_title",
    menu_path="Extensions/Hello Plugin/Tools/Diagnostics/Live",
    menu_path_keys=(
        "menu.extensions",
        "my_studio.hello_plugin.menu_root",
        "my_studio.hello_plugin.menu_tools",
        "my_studio.hello_plugin.menu_diagnostics",
        "my_studio.hello_plugin.menu_live",
    ),
    interaction=inx.editor.PanelInteractionDescriptor(),
)
class HelloPluginPanel(inx.editor.EditorPanel):
    def __init__(self) -> None:
        super().__init__("Hello Plugin", "my_studio.hello_plugin.panel")

    def _initial_size(self) -> tuple[float, float]:
        return 420.0, 240.0

    def on_render_content(self, ctx) -> None:
        ctx.text_wrapped(inx.editor.translate("my_studio.hello_plugin.panel_message"))
