# Adding filters to workflows

Sometimes collections don't provide you with your desired granularity. For example, you might want to focus
on high confidence detectors, while your favourite collection has a few more low confidence ones.

You can use filters to achieve the exact results that you want:
1. filter by confidence
2. filter by severity
3. filter by category ( e.g. only show gas optimisations )


## Adding and removing filters

Adding and removing filters is easy:
```bash
# you can use an allow list to only include certain detectors
napalm workflow detect include confidence HIGH

# of course you can also use a deny list to exclude certain detectors
napalm workflow detect exclude confidence LOW

# you can also reset filters
napalm workflow detect reset confidence
```

> Don't try to mix allow and deny lists, it will not work as expected.


## Available filters
You can filter a range of different properties:
```bash
napalm workflow detect include confidence HIGH
napalm workflow detect include severity CRITICAL
napalm workflow detect include category gas
```

## Tool standards

Keep in mind that different tools like to use different naming conventions.

For example, slither has HIGH/MEDIUM/LOW/INFO, while semgrep has INFO/MEDIUM/ERROR. Furthermore, tools like to use
different names in their output when compared to what you use to program the modules.

Napalm will use the original names of the tools, not the sarif output!

