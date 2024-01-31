# 🔥 Napalm

Napalm is a project management utility for custom solidity vulnerability detectors. 

If you're an auditor you've probably played around with various static analysis tools, maybe even written a couple of 
custom modules. If so, you'll have noticed that you're reaching for different tools all the time, and that
organising your 100+ custom modules is starting to become a hassle.

Napalm to the rescue!

With Napalm you can manage, and easily run your custom detection modules for multiple tools, all from one place.

- reporting - Napalm takes care of building a comprehensive report for you, so you can focus on writing your modules.
- installation - Zero hassle installation of your modules, and their dependencies, in a clean virtual environment.
- batch processing - Run your modules against multiple contracts, or multiple versions of the same contract, in one go.

## Installation

Napalm is available on PyPi, so you can install it with pip:

```bash
pip install napalm-toolbox[slither]
```

## 💣 Running scans with Napalm
Using napalm is simple, you've got two main concepts to keep in mind:
1. **Collection** - A collection is a group of detection rules / modules.
2. **Workflow** - A workflow is a set of collections that you commonly want to use together when analyzing a contract.

You've got three default workflows:
- **detect** - This is likely your main workflow, and is commonly used to run all high-confidence detectors.
- **direct** - Direct is a workflow commonly used by bounty hunters, it's detectors provide suggestions on where to look for bugs. Usually focused on high-impact.
- **inform** - This workflow has all your common optimisations, suggestions, informational modules.

### Running a workflow
To run a workflow, simply run the following command:

```bash
napalm run <workflow> <contract>
# or
napalm run <workflow> <directory>
```

## 💼 Installing Napalm packages
When you first install Napalm, things might seem a little boring. That's because you haven't installed any packages yet!

Napalm packages are simply python packages that contain Napalm collections. Here is the napalm base package that comes
pre-loaded with tons of useful detection modules!
```bash
pip install napalm-base
```

Next time you run napalm it will automatically prompt you to add the collections in this package to your default workflows!

> 💡 **Note:** Try re-running `napalm run detect` now that you've got some collections installed!

---

## 🧑‍💻 Using Napalm as a module dev

To start a new Napalm project, run the following command in an empty directory:

```bash
napalm-dev init
```

This will automatically set up a napalm project for you that takes care of everything! The only thing you need to do is 
write detection modules and rules.

You'll see that the default project structure comes with two collections pre-loaded, `detectors` and `indicators`. Add
your detection modules to either of these collections, and they'll be automatically loaded when you run napalm! Of course,
if you'd like to add more collections, you can do so by just creating a new directory!

> Note: the project acts like a python project so don't forget to add __init__.py files!

