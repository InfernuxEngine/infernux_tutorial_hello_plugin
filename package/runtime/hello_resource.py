from pathlib import Path

import infernux as inx


class HelloResource(inx.InxComponent):
    def start(self) -> None:
        path = inx.Application.package_path(
            "chenlizheme/tutorial_hello_plugin", "runtime/data/message.txt"
        )
        message = Path(path).read_text(encoding="utf-8").strip()
        inx.Debug.log(message, self)
