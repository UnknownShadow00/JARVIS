# Consumer inventory

At production commit `fa8560c`, a scan of all other `app/**/*.py` files finds **zero** references to `registry_metadata`. `binding_projection.py` remains absent. `pipeline.py`, `server.py`, `app/tools/registry.py`, router, permissions, dispatcher, Hermes adapter, API and UI are unchanged. Tests are the only importers. No package export was added. The sentinel records `production_consumers=[]`.
