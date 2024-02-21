# Testing

As with normal development, testing is a quintessential aspect of developing detection modules.


## Setting Up
Good news! You don't need to do anything to set up testing, napalm automatically sets up a simple test structure for you.

```
your_napalm_project/
├── your_napalm_project/
├── test/
│   ├── corpus/
│   │   ├── example.sol
```

The `corpus` directory is where you should place your test files. Test files are simple solidity files which exhibit
the desired vulnerability. You'll note that corpus is initialised as a foundry project. 
This allows us to set up more complicated test scenarios that require importing smart contracts.

## Running Tests
To run tests, simply run the following command from the root of your project:

```bash
$ napalm-dev test
```

## Writing Tests
The default tests that come with napalm won't help much in testing your own fancy detection modules. 
You'll need to write your own tests. To do this, simply create a new solidity file in the `corpus` directory.

In this file, you should exhibit the vulnerability you are trying to detect, you should also annotate the locations
in the file that you want your detector to find an issue for.

You can do this by writing simple annotations:
1. `// napalm-detect: <detector-id>`
2. `// napalm-ok: <detector-id>`

while you're still developing a rule you can add `wip` to indicate so:
1. `// napalm-wip-detect: <detector-id>`
2. `// napalm-wip-ok: <detector-id>`

Here is an example of a test file:
```solidity
// example.sol
pragma solidity ^0.8.0;

contract Example {
    function example() public {
        // napalm-detect: unprotected-selfdestruct
        selfdestruct(msg.sender);
    }
}
```