# Collections

Collections are sets of detection modules, built be automators to be used with NAPALM.

Collections often have a thematic focus. Examples:
- gas optimization
- detectors for high/medium/low severity vulnerabilities
- indication detectors for high/medium/low severity vulnerabilities
- (indication) detectors for specific vulnerabilities (e.g. reentrancy)

As a user you'll likely set up 3 meta-collections that aggregate the detectors you want to use in three main workflows:
- detect: run detectors
- indicate: run indication detectors
- optimize: run gas optimization detectors / informational detectors

```bash
# show information of a specific collection
napalm collection show <collection_name>

# show which collections are currently installed
napalm collection list
```
## Installing a collection
Napalm collections are installed with pip.
```bash 
# install a collection
pip install <collection_package_name>
```

## Meta-collections
Meta-collections are collections that aggregate other collections. They're used to group collections together for
specific workflows. For example, you might have a meta-collection that contains all the collections that are used for
detecting vulnerabilities, and another meta-collection that contains all the collections that are used for gas
optimization.

There are 3 meta-collections that are used by default:
- detect: contains all collections that are used for detecting vulnerabilities
- indicate: contains all collections that are used for indicating vulnerabilities
- optimize: contains all collections that are used for gas optimization

You can use these meta-collections as follows:
```bash
# run the detect workflow
napalm run detect
```

## Developer
_Collections as a developer._

Collections serve as a way to organise your detection modules, they're the top level hierarchy to introduce method
to the madness. Collections are not the only way to organise and label your detection modules. Tools such as Slither,
and Semgrep allow for the addition of metadata to your detection modules. Napalm also has access to these features, 
allowing for all the customisation and organisation you need.

> :bulb: Keep in mind: collections are commonly used in the detect/indicate/optimize workflow. It's a good idea to
> structure your collections in a way that makes sense for these workflows.


### Entry Points
Napalm recognizes collections through entry points. 

Example pyproject.toml
```toml
[tool.poetry]
name = "napalm-modules"
version = "0.1.0"
description = "Napalm managed detection modules"
license = "MIT"
readme = "README.md"
authors = []
packages = [
    { include = "napalm_modules" },
    { include = "detectors" }
]

[tool.poetry.dependencies]
python = "^3.10"
slither-analyzer = "^0.9.6"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.plugins."napalm.collections"]
"package_name"= "package.module.napalm_helper:entry_point"
```

The helper is a simple stub that handles everything you need to do to register your collection with napalm.
```python
# package/module/napalm_helper.py
from typing import List, Tuple
from napalm.package import get_collections()

def entry_point() -> List[Tuple[str, str]]:
    """Returns a list of tuples containing the name of the collection and the yaml configuration for it."""
    return get_collections(module)
```

This will assume you have a project structure like this:

```
project/
    project/
        __init__.py
        collection_one/
            module_one.py
        collection_two/
            module_two.py
            semgrep_config.yaml
    pyproject.toml
```

It will automatically scan, fetch, recognise and structure all slither, mythril and semgrep detectors and provide them
to napalm.