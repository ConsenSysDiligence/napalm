# Workflows
*Run the right detectors at the right time.*

Napalms' basic unit of work is a detector / detection rule, written by security engineers and organised into collections, 
they're what you use to detect vulnerabilities in smart contracts. A problem that quickly arises when you start to use
napalm is that you'll quickly have a lot of collections, and you'll find yourself wanting to run a couple of them at 
the same time. This is where workflows come in!

A workflow is simply a set of collections that you want to run together, and napalm comes with three default workflows
that you can use out of the box: detect, direct, and inform.

However, you can create your own workflows that match your usecase better. Some ideas:
- audit
- hunt
- report

## Composing workflows

Setting up your own workflows is very easy, the following snippet walks you through the process:

```bash
# Let's create a new workflow called "report"
$ napalm workflows create report

# An empty workflow is boring, so lets add an existing collection to it:
$ napalm workflow report add napalm-base/detect

# Check if it works:
$ napalm workflow report list
workflow report contains:
  - napalm-base/detectors
```

You can now run your workflow like this:

```bash
$ napalm run report <contract>
```

## Default workflows & Collections
You often don't have to manually compose your workflows! This is because napalm comes with three default workflows that
are automatically loaded when you install napalm. These workflows are: detect, direct, and inform.

Each time you install a napalm package, napalm will check if it can find collections with the following names, and 
it will automatically add them to the corresponding workflows:
- detectors -> detect
- indicators -> direct
- optimisations -> inform

You'll notice this working if you install the napalm-base package! 

