## `hrmulator`

### Human Resource Machine

[Tomorrow Corporation](https://tomorrowcorporation.com/) makes a game called [Human Resource Machine](https://tomorrowcorporation.com/humanresourcemachine).  It's a game that teaches you a tiny drag-and-drop assembly language; and guides you to solving programming problems with that knowledge.  If you don't yet have this game, you should go buy it immediately :-).  It's adorable and really fun.

### `hrmulator`

As I was playing Human Resource Machine, and the problems started getting larger: I started craving my source code control tools.  Why can't I use Git on my little HRM programs?  I want to branch and experiment and try things without fear of not being able to get back to my old state.

`hrmulator` is simply a tool to help you play with Human Resource Machine programs in textual form, so you can apply source code control tools.  It's no good to you if you're not playing this game.  Go buy the game.  Tomorrow Corporation, please don't sue me.

These tools are really rough, but improving with time.  A simple program to copy from the inbox to the outbox looks like this:

~~~Assembly
START:
    move_from_inbox
    move_to_outbox
    jump_to START
~~~

If you saved that to a file named `simple_copy.hrm` you could then

~~~Python
from hrmulator import Computer

computer = Computer()
computer.print_run_program('simple_copy.hrm', inbox=[1, 2, 3, 4, 5, 6, 7])
~~~

The output would be:

~~~console
simple_copy.hrm

START:
  001: move_from_inbox
  002: move_to_outbox
  003: jump_to START

Inbox:
[1, 2, 3, 4, 5, 6, 7]
Outbox:
[1, 2, 3, 4, 5, 6, 7]

Program size: 3; Total steps executed: 21
~~~

You can simplify the world a little by putting `simple_copy`s code right in your Python file:

~~~Python
from hrmulator import Computer

simple_copy = """
START:
    move_from_inbox
    move_to_outbox
    jump_to START
"""

computer = Computer()
computer.print_run_program(program_text=simple_copy, inbox=[1, 2, 3, 4, 5, 6, 7])
~~~

### Installing `hrmulator`

`hrmulator` is packaged in the standard Python scheme (but not available on PyPI --- and probably never will be).  Just download it or clone it, as you like; and

~~~Bash
cd hrmulator
python setup.py install
~~~

...from that point forward, `hrmulator` is available for import wherever you are working, including into `IPython`.  If you're thinking of working on `hrmulator` itself, consider saying `python setup.py develop` instead as that installs symlinks that lead back to your clone.

### The Instruction Set

~~~
no_op
move_from_inbox
move_to_outbox
copy_from tile
copy_to tile
add tile
subtract tile
bump_up tile
bump_down tile
jump_to place
jump_if_zero_to place
jump_if_negative_to place
~~~

`tile` may be a number (like `5`) or a label (like `hello`) you applied to one of the numbered tiles.  `place` may be a step number (like `12`) or a label you inserted into the program (like `START`).  Here's an example using both memory and place labels:

~~~Python
from hrmulator import Computer, Memory


program_text = """
START:
    copy_from zero
    copy_to sum
ADD:
    move_from_inbox
    jump_if_zero_to DONE
    add sum
    copy_to sum
    jump_to ADD
DONE:
    copy_from sum
    move_to_outbox
    jump_to START
"""


c = Computer()
c.print_run_program(
    program_text=program_text,
    inbox=[2, 4, 0, 0, 4, 0],
    memory=Memory(labels={'sum':0, 'zero':5}, values={'zero':0})
)
assert(c.outbox == [6, 0, 4])
~~~

You can actually do it all within the `print_run_program` call:

~~~Python
import hrmulator


c = hrmulator.Computer()
c.print_run_program(
    memory=hrmulator.Memory(
        labels={'sum':0, 'zero':5},
        values={'zero':0}
    ),

    inbox=[2, 4, 0, 0, 4, 0],

    program_text="""
        START:
            copy_from zero
            copy_to sum
        ADD:
            move_from_inbox
            jump_if_zero_to DONE
            add sum
            copy_to sum
            jump_to ADD
        DONE:
            copy_from sum
            move_to_outbox
            jump_to START"""
)
assert(c.outbox == [6, 0, 4])
~~~

For some fun, replace the instantiation of `Computer()` with `Debugger()`.  That will load up the program in the debugger, stop at address `0`, and give you a `debug> ` prompt.
