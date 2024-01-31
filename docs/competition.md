A good way to make sure that you're staying competitive with your analysis modules is to see if anyone is able to detect
issues that you can't. 

To keep track of vulnerabilities that you're able to detect you can add some simple info to your detectors like this:

Semgrep:
```yaml
rules:
  - id: example-rule
    ...
    metadata:
      competitors:
        - name: name/of/competitor
          title: Title used by the competitive tool!
```

Slither:
```python
class SampleDetector(AbstractDetector):
    """
    Sample detector for napalm
    """

    COMPETITORS = [
        {
            "name": "name/of/competitor",
            "title": "Title used by the competitive tool!"
        }
    ]
```

## Twins

Semgrep:
```yaml
rules:
  - id: example-rule
    ...
    metadata:
      twins:
        - id: detector_id
```

Slither:
```python
class SampleDetector(AbstractDetector):
    """
    Sample detector for napalm
    """

    COMPETITORS = [
        detector_id,
    ]
```


## Limitations

### Coverage
It's possible that the competition has a more precise / extensive detection module, leading to a false sense of coverage.

To resolve this it's necessary to build benchmarks, this is a planned feature for napalm.
