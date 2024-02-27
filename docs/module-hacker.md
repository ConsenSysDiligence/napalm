This getting started guide will get you from 0 to 60 on using napalm to manage your own detection modules.

### Install Napalm

Your first step on the road to becoming a napalm module hacker is installing the napalm python package (if you haven’t already).

```bash
pip3 install napalm-toolbox
```

> 💡 Napalm uses python 3.12 (or higher), make sure you’ve got a recent version installed!


### Setup Your Project

Now set up a new and empty directory where you want to set up your napalm project.

```bash
$ cd ~/Development
$ mkdir my_napalm_modules
$ cd my_napalm_modules
$ napalm-dev init
```

Congratulations! You’ve set up a napalm project.

It should look somewhat like this:

```bash
README.md         
my_napalm_modules/ 
	detectors/
	indicators/
	napalm.py          <- don't change this file!
	__init__.py
pyproject.toml    
venv/
```

> 💡 Napalm automatically initialises a new git repository for you!
>
> Not familiar with git? Check out this [tutorial](https://docs.github.com/en/get-started/quickstart/hello-world) to learn about git & GitHub 🐙.

**Virtual Environments**

Napalm automatically sets up a new virtual environment for you.

This allows you to keep your WIP detection module isolated. Something which will end up being very useful if you ever want to run a napalm scan without interference from WIP detection modules.

Your detection modules are automatically loaded into napalm within the virtual environment! Just run `source venv/bin/activate` and enjoy!

It’s also possible to do a global installation of your project! Just add `--global` when you’re initialising the project. If you want to do a global installation of your, previously initialised, project just run `napalm-dev install --global`.

All installations are editable, meaning that you can edit your detection modules, and even add new ones without having to re-install!

**Napalm Project Structure**

Napalm comes pre-loaded with three basic collections: detectors, indicators, optimisations.

You’ll find these in `my_napalm_modules/` , where you can also add your own collections by simply creating new directories!

This top level structure is the only thing *mandated* by napalm. Within collection directories you’re allowed to structure things however you like! Napalm has routines to automatically explore your directory structure to find and load all your detection modules!

There is a benefit to using the three basic collections, as these will automatically be added to the three basic workflows: detect, direct and inform (detectors → detect, indicators → direct, optimisations → inform). Other collections will require manual configuration, like this: `napalm workflow detect add your_custom_collection`. 

### Your first modules

You’ll already find two example plugins pre-loaded in the detectors collection, change these or drop in some new modules to experience the smooth experience of napalm development!

Napalm currently supports two main tools, which complement each other very well.

**semgrep -** Semgrep is an amazing static analysis tool that’s perfect for rapid development of new analysis modules. Got an idea for something that you want to automate? With semgrep you’ll have a demo detection module up and running!

**slither -** Slither is a more powerful static analysis tool. You get access to the full (and familiar) language Python to write your analysis rules in, allowing you to add precision where semgrep isn’t able to provide it.

We recommend checking out each tools own guides on developing detection modules.

- [semgrep](https://semgrep.dev/docs/writing-rules/overview/)
- [slither](https://github.com/crytic/slither/wiki/Adding-a-new-detector)

**AI False Positives**

Napalm adds LLM-based false positive scanning to your analysis capabilities. 

To leverage this technique all you need to do is add false positive prompts to your detection modules. Just describe the cases when your rule returns false positives, and napalm takes care of the rest!

Here is how you add false positive prompts to your rules:

*semgrep*

```yaml
rules:
  - id: example-rule
    ...
    metadata:
      false_positive_prompt: >
          This is a false positive when XYZ is the case.
```

*slither*

```python
class SampleDetector(AbstractDetector):
    """
    Sample detector for napalm
    """

    FALSE_POSITIVE_PROMPT = """
        This is a false positive when XYZ is the case.
    """
```

**Reporting**

It’s very important to have a good overview of your detection modules. `napalm-dev info` will provide you with exactly that!

```bash
$ napalm-dev info
napalm-core summary:
  - 3 collections installed
  - 2 detectors

napalm-core collections:
  - optimisations (0 detectors)
  - indicators (0 detectors)
  - detectors (2 detectors)

optimisations modules:

indicators modules:

detectors modules:
  - int-cast-block-timestamp - [INFO] Consider not casting block timestamp to ensure future functionality of the contract.
  - napalm-sample-detector - [LOW] This is a sample detector for napalm
```

### Running your rules

Running your rules is very easy!

```bash
$ source venv/bin/activate # only necessary when not installed globally
$ napalm workflow detect list # answer yes when asked to automatically add to detect collection
$ napalm run detect your_contract.sol # profit!
```

### Sharing your Rules

Sharing your rules is easy, and there are two recommended methods:

1. **git (recommended for private ) -** You can easily use GitHub to distribute your detection modules, simply use pip as follows: `pip install git+ssh://git@github.com/...` .
2. **pypi (recommended for public ) -** Use a tool like `poetry` to upload your package to pypi, where others will be able to install it using `pip install package_name`. ****

> ⚠️ Make sure to check out the pyproject.toml file and fill out the relevant details before publishing to pypi.


### Let’s gooo 🚀

You now know enough to go and find tons of bugs. 

Good Luck.
