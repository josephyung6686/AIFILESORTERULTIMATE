"""The read surface, composed. P13's screens joined to the parts that fill them.

`src/review_surface/` is a DATA AND CONTRACT layer by its own declaration: it
imports no producer, holds no connection it did not receive, and takes every
policy as an injected argument with no default. That is why twenty-one of its
twenty-seven modules were reachable from nothing a person could type -- a
contract layer needs somebody to hold both ends, and nobody did.

This package is that somebody, for the screens a person READS. It is the same
shape `apply_run` already has for the screens a person ACTS on: it imports the
producing parts and P13 together, it returns lines, and `src/cli.py` -- the sole
composition root -- prints them and picks every number and every policy.

**Nothing here decides anything either.** P13's rule that it presents and never
decides is not weakened by being wired: a seam that answered a question P13
refuses to answer would simply move the invention one file over. Where a screen
needs a policy, the function takes it as a required keyword and the composition
root supplies it, and where a screen cannot be built the seam raises rather than
rendering a shorter one.

**No numeric literal beyond 0 and 1 lives in this package.** Page sizes,
truncation limits and depth caps are the composition root's, for the same reason
the ceilings are P1's: a number chosen here is a policy chosen by whoever last
edited a part package.
"""
