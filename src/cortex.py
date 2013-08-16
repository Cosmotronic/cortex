#!/usr/bin/env python3
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0
import cortex.repl as _repl
import cortex.helpers as helpers

import sys
import os.path


def repl(file_like, env={}):

    """Implemented Commands:
     "load models <filename>"
        loads a model descriptor file, being a list of Model compatible
        JSON objects and enters them into the interpreter's model table.

     "alias model <alias> <name>"
        creates an alias for a model, hopefully something easier to type
    
     "ls models"
        enumerates the loaded models by name
    
     "ls aliases"
        enumerates the loaded aliases by abbrev -> real name
    
     "attack <model name> [with modifiers...] <model name> [with modifiers...]"
        enumerates and evaluates all attack options for one model
        against another, evaluating every weapon the attacking model
        has against the target at range and in charge. Attacking
        warcasters and warjacks will compute the probable outcomes of
        different boosting strategies as well.
    
     "reset"
        clears out all the state of the repl, essentially restarting
        it without quitting and reloading
    
     "quit" | "exit" | ":q"
        exits the Cortex program

    """

    retry = False
    while True:
        if(not retry):
            line = []
            if(file_like == sys.stdin):
                sys.stdout.write("->> ")
                sys.stdout.flush()
                line = file_like.readline()
                line = helpers.shell_read_str(line)
                line = [s.strip() for s in line]

        # case -2:
        #    deal with reading an empty line
        if(len(line) == 0):
            continue

        # case -1:
        #    help code! gotta help t3h pplz out!
        if(line[0] == "help"):
            help(repl)

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
        #
        # FIXME:
        #    it's awesome that I've now done away with all the inline
        #    control code and abstracted it out to a load time
        #    computed jump table but the issue of having to update the
        #    docstrings, especially for this top level repl function
        #    persists. How to keep help usable when I only have a
        #    hashmap of fns that I can update quickly?
        new_env, code = {}, False
        try:
            new_env, code = _repl.dispatch(line, env=env)

        except Exception as e:
            print("Command failed: '%s'" % e)
            continue

        if(code):
            env = new_env
            continue

        else:
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
    env = {'models':{}, 'model aliases':{}}
    if os.path.exists(os.path.abspath("~/.cortexrc")):
        #print("loading config file...")
        env = repl(open("~/.cortexrc"))
    repl(sys.stdin, env=env)
        
