# Infernux tutorial: Hello Plugin

A minimal plugin for the [plugin-authoring tutorial](https://infernux-engine.com/learn/plugin-authoring.html).
It reads a packaged text resource in Editor Play and exported Player, and adds a localized Editor panel.
Requires Infernux >=0.4.1,<0.5. The package reference is `chenlizheme/tutorial_hello_plugin`.

Build: `python package.py build dist/plugin.inxpkg`.
Validate: `python .infernux-dev/validate.py` and `python -m unittest discover -s tests`.
The template workflow publishes immutable archives and release metadata from matching version tags.
Version 0.1.11 changes the message resource; existing asset GUIDs remain stable.
This demonstration is not registered in the official plugin catalog.
