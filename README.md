## HRMulator

### Human Resource Machine

[Tomorrow Corporation](https://tomorrowcorporation.com/) makes a game called [Human Resource Machine](https://tomorrowcorporation.com/humanresourcemachine).  It's a game that teaches you a tiny drag-and-drop assembly language; and guides you to solving programming problems with that knowledge.  If you don't yet have this game, you should go buy it immediately :-).  It's adorable and really fun.

### HRMulator

As I was playing Human Resource Machine, and the problems started getting larger: I started craving my source code control tools.  Why can't I use Git on my little HRM programs?  I want to branch and experiment and try things without fear of not being able to get back to my old state.

HRMulator is simply a tool to help you play with Human Resource Machine programs in textual form, so you can apply source code control tools.  It's no good to you if you're not playing this game.  Go buy the game.  Tomorrow Corporation, please don't sue me.

These tools are really rough, but improving with time.  A simple program to copy from the inbox to the outbox looks like this:

~~~
START:
    move_from_inbox
    move_to_outbox
    jump_to START
~~~

If you saved that to a file named `simple_copy.hrm` you could then

~~~python
from HRMulator import Computer

computer = Computer()
computer.inbox = [1, 2, 3, 4, 5, 6, 7]
computer.memory[0] = 0
computer.memory[1] = 1
computer.print_run_program('simple_copy.hrm')
~~~

The output would be:

~~~
simple_copy.hrm

  000: move_from_inbox
  001: move_to_outbox
  002: jump_to 000

Inbox:
[1, 2, 3, 4, 5, 6, 7]
Outbox:
[1, 2, 3, 4, 5, 6, 7]

Program size: 3; Total steps executed: 21
~~~
