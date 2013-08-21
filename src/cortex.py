#!/usr/bin/env python3
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0
import cortex.repl as _repl
import cortex.helpers as helpers

import sys
import os.path


def repl(file_like, env={}):
    """Repl code!

    This function serves to read commands from a file-like object
    (either an actual file when reading the Cortex config file or
    standard input when interacting with a user) and relay commands to
    their implementations in cortex.repl as needed.

    All this function implements and shall ever implement is
    persistance of the environment state between commands and the
    commands required to break _out_ of the repl loop.

    """
    retry = False
    while True:
        if(not retry):
            line = []
            if(file_like == sys.stdin):
                sys.stdout.write("->> ")
                sys.stdout.flush()
                line = file_like.readline()

            else:
                pos = file_like.tell()
                line = file_like.readline()
                if(pos == file_like.tell()):
                    break

            line = helpers.shell_read_str(line)
            line = [s.strip() for s in line]

        # case -1:
        #    deal with reading an empty line
        if(len(line) == 0):
            continue

        # case 0:
        #    exit code! gotta be able to quit...
        elif(line[0] in ["quit", "exit", ":wq", ":q"]):
            return 0

        # case 1:
        #    for when in development, be able to exit back to the REPL
        elif(line[0] == "break"):
            break

        # case 2:
        #    index through the _repl system to dispatch commands in a
        #    relatively modular and useful manner.
        new_env, code = {}, False
        new_env, code = _repl.dispatch(line, env=env)

        if(code):
            env = new_env
            continue

        elif(not code):
            # FIXME:
            #    look up line[0] from the alias table, set line[] and
            #    restart by setting the retry flag!
            #
            #    if the retry flag was already set, uset it.
            print("Unknown command!")
            continue

        # FINALLY
        #    this is where code that is intended to run after a
        #    successfull command goes. so if I add a history logger
        #    (which would be cool and kinda usefull) then this is
        #    where that write to file would go.


        # END FINALLY
        continue

    return env


if __name__ == '__main__':
    # Cortex
    #   a Warmachine strategery toolkit
    #
    #   Loads and interprets the file ~/.cortexrc as though all
    #   commands were being typed at the repl before dropping into
    #   read/eval/print mode for user IO.
    #
    _env = {'models':{}, 'model aliases':{}}

    file=helpers.unixpath("~/.cortexrc")

    if os.path.exists(file):
        print("loading config file...")
        _env = repl(open(file), env=_env)
    repl(sys.stdin, env=_env)
