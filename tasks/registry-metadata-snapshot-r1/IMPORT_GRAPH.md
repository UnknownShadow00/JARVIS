# Import graph

Static AST inventory of `registry_metadata.py`: `__future__`, `ast`, `dataclasses`, `hashlib`, `json`, `pathlib`. There are no imports of `app.tools.registry`, handlers, dispatcher, server, Hermes, provider, audit or provenance. The fixed file path points to canonical `app/tools/{registry,apps,browser}.py` source bytes; reading/parsing them never imports their modules. The sentinel forbids such imports during construction and observed none. No dynamic import, `eval`, `exec`, service locator or registry instance appears.
