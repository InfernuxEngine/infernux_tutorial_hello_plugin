from importlib import import_module

import infernux as inx


class HelloPluginEditorPreload(inx.InxPreload):
    def preload(self, context: inx.PreloadContext) -> None:
        import_module("my_studio.hello_plugin_editor.panel")

    def unload(self) -> None:
        pass
