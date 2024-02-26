This guide helps you set up Napalm to suit your workflow perfectly.

Using napalm you can bring your own detectors, or easily install packages with detectors built by others! 

Just take ***2 minutes*** to follow this guide and get started!

### Install Napalm

Your first step on the road to becoming a napalm module hacker is installing the napalm python package (if you haven’t already).

```bash
pip3 install napalm-toolbox
```

> 💡 Napalm uses python 3.12 (or higher), make sure you’ve got a recent version installed!

### Packages

Just napalm on it’s own is very boring. You’ve got to install some detection modules!

Luckily, we have a couple ready for you in the `napalm-base` package. You can install it using pip:

```bash
$ pip3 install napalm-base
```

Now, let’s see what you get from this package:

```bash
$ napalm collections show
<installation prompt>
Installed collections:
  - napalm-base/optimisations
  - napalm-base/indicators
  - napalm-base/detectors
```

Awesome, we’ve got three collections installed! Also, notice the tool asked us whether we want to add them to the default workflows. Go ahead and agree, we’ll get to this later.

To see the detection modules that come in each collection you can use the `list` command:

```bash
$ napalm collections show napalm-base/detectors
int-cast-block-timestamp - [INFO] Consider not casting block timestamp to ensure future functionality of the contract.
dumb_overflow_rule - [INFO] This addition can overflow
napalm-sample-detector - [LOW] This is a sample detector for napalm

napalm-base/detectors summary:
  - 2 semgrep rules
  - 1 slither detectors
```

### Your workflows

In napalm, workflows are central to running scans. Pre-loaded with *detect, direct* and *inform*, but configurable to your hearts content, you’ll be able to set up napalm just to your liking.

Workflows, simply put, are simply combinations of collections that you will want to run at different times. Here are the three default ones:

- detect → this workflow often contains collections with rules that are aimed at detecting vulnerabilities
- direct → this workflow often contains collections with rules aimed at finding indicators of potential vulnerabilities, rather than high-confidence findings.
- inform → this workflow often contains all your collections with informational and optimisation rules

You can create and manage your own using `napalm workflow <workflow name> add/remove/show` and `napalm workflows create/ delete <workflow name>`.

When we executed the `napalm collections show` command we automatically added the detectors in the napalm-base package to your workflows. You can also do this manually, like this:

```bash
$ napalm workflow detect add napalm-base/detectors
# you can create your own workflows too!
$ napalm workflows create audit
$ napalm workflow audit add napalm-base/detectors
$ napalm workflow audit add napalm-base/optimisations
$ napalm workflow audit list
workflow audit contains:
  - napalm-base/detectors
	- napalm-base/optimisations
```

### Run a scan

Let’s run some analyses!

```bash
$ napalm run detect <your_contract.sol/your_contracts/directory>

<your findings will be printed here>
```

### Upgrade

Using napalm is truly empowering when you start writing your own modules! 

Checkout our getting started page for becoming a napalm module dev [here](/module-hacker.md).
