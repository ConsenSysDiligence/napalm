Napalm provides advanced false positive filtering techniques using LLMs.

### Users
To enable false positive filtering simply provide your open ai api key using environment variables:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

When you run your scans add the --ai-filter option to enable the false positive filtering engine.
```bash
# example
napalm run detect contract.sol --ai-filter
```

### Rule Developers
It's incredibly easy to add AI based false positive filtering to your rules and modules, simply add a false positive
prompt that describes when your rule is a false positive. Napalm takes care of the rest!

Semgrep:
```yaml
rules:
  - id: example-rule
    ...
    metadata:
      false_positive_prompt: >
          This is a false positive when XYZ is the case.
```

Slither:
```python
class SampleDetector(AbstractDetector):
    """
    Sample detector for napalm
    """

    FALSE_POSITIVE_PROMPT = """
        This is a false positive when XYZ is the case.
    """
```
