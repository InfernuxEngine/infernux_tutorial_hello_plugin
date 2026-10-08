from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "package"
manifest = json.loads((PACKAGE / "inx_package.json").read_text(encoding="utf-8"))
required = {"reference", "name", "version", "engine"}
missing = sorted(required - manifest.keys())
if missing:
    raise SystemExit("Missing manifest fields: " + ", ".join(missing))
unsupported = sorted({"dependencies", "requirements"} & manifest.keys())
if unsupported:
    raise SystemExit("Unsupported manifest fields: " + ", ".join(unsupported))
for path in ("README.md", "README.zh-CN.md", "LICENSE", "package", "package.py"):
    if not (ROOT / path).exists():
        raise SystemExit(f"Missing template entry: {path}")


def module_names(root):
    names = set()
    for path in root.rglob("*.py"):
        parts = path.relative_to(root).with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        if parts:
            names.add(".".join(parts))
    return names


runtime_root = PACKAGE / "runtime"
editor_root = PACKAGE / "editor"
# Namespace directories alone do not execute editor code and may be shared.
editor_only_modules = module_names(editor_root) - module_names(runtime_root)
editor_imports = {"infernux.engine.ui", "Infernux.engine.ui"} | editor_only_modules

for path in sorted((*runtime_root.rglob("*.py"), *editor_root.rglob("*.py"))):
    source = path.read_text(encoding="utf-8")
    compile(source, str(path), "exec")
    if not path.is_relative_to(runtime_root):
        continue
    tree = ast.parse(source, filename=str(path))
    package_parts = path.relative_to(runtime_root).parent.parts
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if node.level > len(package_parts):
                    continue  # An invalid relative import is a Python runtime error.
                prefix = package_parts[:len(package_parts) - node.level + 1]
                suffix = node.module.split(".") if node.module else ()
                module = ".".join((*prefix, *suffix))
            else:
                module = node.module or ""
            imports = [module, *(f"{module}.{alias.name}" for alias in node.names)]
        else:
            continue
        if any(
            name == editor or name.startswith(editor + ".")
            for name in imports for editor in editor_imports
        ):
            raise SystemExit(f"Runtime source imports Editor code: {path.relative_to(PACKAGE)}:{node.lineno}")
for english in PACKAGE.joinpath("plugin_pages").glob("*.md"):
    if english.name.endswith(".zh-CN.md"):
        continue
    localized = english.with_name(f"{english.stem}.zh-CN.md")
    if not localized.is_file():
        raise SystemExit(f"Missing zh-CN page: {localized.name}")
print("Package layout and Python sources are valid.")
