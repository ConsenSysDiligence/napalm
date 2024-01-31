
Projects can have multiple collections in them.

How to deal with name collisions?
    maybe we can use github? / maybe we use the python package name 


## Collection Projects
A collection project is a python project that uses entry points to register itself with napalm


## Napalm <> slither / mythril integration
Napalm itself registers an entry point for slither and mythril to use. 

On execution of the tool, it will use the entry point to find all napalm plugins and load them into the current context.

Napalm will use the current environment variable "NAPALM_META_COLLECTION" to determine which collections to actually load. 
Allowing for two methods of running the tools with napalm:

```bash
# Run the tool through napalm itself
napalm run detect

# Run slither/mythril directly with a specific meta-collection
NAPALM_META_COLLECTION=detect slither ...
NAPALM_META_COLLECTION=detect mythril ...
```

The second option will allow you to run the tools directly, and use their own printers.


### pytoml

```toml
[tool.poetry.plugins."napalm.collection"] 
"napalm collection"= "path.to.top_module"
```

### project structure

```
project/
    project/
        __init__.py
        collection_one/
        collection_two/
    pyproject.toml
```


## Semgrep rules
Semgrep rules are yaml files. 

The entry point provided to napalm will provide an interface to load all semgrep rules from all collections.

```python
from typing import List, Tuple

def get_semgrep_configurations() -> List[Tuple[str, str]]:
    """Returns a list of tuples containing the name of the collection and the yaml configuration for it."""
    pass    
```