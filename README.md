## HRMulator

### Human Resource Machine

[Tomorrow Corporation](https://tomorrowcorporation.com/) makes a game called [Human Resource Machine](https://tomorrowcorporation.com/humanresourcemachine).  It's a game that teaches you a tiny drag-and-drop assembly language; and guides you to solving programming problems with that knowledge.  If you don't yet have this game, you should go buy it immediately :-).  It's adorable and really fun.

### HRMulator

As I was playing Human Resource Machine, and the problems started getting larger: I started craving my source code control tools.  Why can't I use Git on my little HRM programs?  I want to branch and experiment and try things without fear of not being able to get back to my old state.

HRMulator is simply a tool to help you play with Human Resource Machine programs in textual form, so you can apply source code control tools.  It's no good to you if you're not playing this game.  Go buy the game.  Tomorrow Corporation, please don't sue me.

These tools are really rough, but improving with time.  Simple program to copy from the inbox to the outbox looks like this:

~~~~~~~~
START:
    copy_from_inbox
    copy_to_outbox
    jump_to START
~~~~~~~~

