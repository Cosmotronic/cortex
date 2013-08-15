#!/usr/bin/env python3
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0
import stats
import wm

import sys
import json
import os
import os.path


def evaluate_attack(src_model, tgt_model):
    mele_weps = [w for w in src_model.weapons if w['type'] == "melee"]
    ranged_weps = [w for w in src_model.weapons if w['type'] == "ranged"]

    # compute boosted/unboosted hit odds
    unboosted_ranged_hit = stats.odds_of_beating(2, (tgt_model.defence - src_model.rat))
    boosted_ranged_hit = stats.odds_of_beating(3, (tgt_model.defence - src_model.rat))
    print("Hit odds with ranged weapons:\n  unboosted: %f\n  boosted: %f"
          % (unboosted_ranged_hit, boosted_ranged_hit))

    unboosted_melee_hit = stats.odds_of_beating(2, (tgt_model.defence - src_model.mat))
    boosted_melee_hit = stats.odds_of_beating(3, (tgt_model.defence - src_model.mat))
    print("Hit odds with melee weapons:\n  unboosted: %f\n  boosted: %f"
          % (unboosted_melee_hit, boosted_melee_hit))

    print("Damage options:")
    # compute the boosted/unboosted damage outcomes
    for w in src_model.weapons:
        print("  using weapon %s:" % w['name'])
        unboosted_dmg = stats.avg_damage(2, (w['pow'] - tgt_model.armor))
        boosted_dmg = stats.avg_damage(3, (w['pow'] - tgt_model.armor))

        print("    unbooosted: %d\n    boosted: %d"
              % (unboosted_dmg, boosted_dmg))


def shell_read_str(line):
    """Reads a line the same way BASH would, grouping and stripping
    quotes, splitting at spaces and soforth.

    """
    split = []
    buff = ''
    quote = None
    for c in line:
        # reading a quoted block...
        if quote:
            if c == quote:
                split.append(buff)
                buff = ''
                quote = None

            else:
                buff += c
                continue

        # enter a quoted block
        if c == '"' or c == "'":
            quote = c
            continue

        # split at spaces
        if len(buff.strip()) != 0 and c == ' ':
            split.append(buff)
            buff = ''

        else:
            buff += c

    if(len(buff.strip()) != 0):
        split.append(buff)

    return split


def repl(file_like, aliases={}, models={}):
    # Implemented Commands:
    #
    # "load models <filename>"
    #    loads a model descriptor file, side effecting the current
    #    state of the interpreter to add more models.
    #
    # "load aliases <filename>"
    #    loads a file which describes a mapping fom abbreviated names
    #    to official model names, so as to make life easiser for the
    #    user.
    #
    # "load army [-j|-s] <name> <filename>"
    #    loads an army from a file using the simple army format if -s,
    #    and json by default or with -j.
    #
    # "alias cmd <alias> <name>"
    #    creates a command alias
    #
    # "alias model <alias> <name>"
    #
    # "ls models"
    #    enumerates the loaded models by name
    #
    # "ls aliases"
    #    enumerates the loaded aliases by abbrev -> real name
    #
    # "attack <model name> [with modifiers...] <model name> [with modifiers...]"
    #    enumerates and evaluates all attack options for one model
    #    against another, evaluating every weapon the attacking model
    #    has against the target at range and in charge. Attacking
    #    warcasters and warjacks will compute the probable outcomes of
    #    different boosting strategies as well.
    #
    # "reset"
    #    clears out all the state of the repl, essentially restarting
    #    it without quitting and reloading
    #
    # "quit" | "exit" | ":q"
    #    exits the Cortex program

    retry = False
    while True:
        if(not retry):
            line = []
            if(file_like == sys.stdin):
                sys.stdout.write("->> ")
                line = file_like.readline()
                line = shell_read_str(line)
                line = [s.strip() for s in line]

        # case 0:
        #    exit code! gotta be able to quit...
        if(line[0] in ["quit", "exit", ":wq", ":q"]):
            return 0

        elif(line[0] == "break"):
            break

        # case 1:
        #    load code! gotta be able to read in datafiles...
        elif(line[0] == "load"):
            # what are we loading?
            if(line[1] == "models"):
                if(os.path.exists(line[2])):
                    new_models = {m['name']:wm.Model(m)
                                  for m in json.load(open(line[2]))}
                    models = dict(models.items() + new_models.items())
                else:
                    print("Error: no such file %s" % line[2])

            elif(line[1] == "aliases"):
                # FIXME
                print("Alias loading isn't supported yet!")

            elif(line[1] == "army"):
                # FIXME
                print("Army loading isn't supported yet!")

            else:
                pass

        # case 2:
        #    alias code! I want to be able to create aliases...
        elif(line[0] == "alias"):
            # what alias type are we creating?
            if(line[1] == "model"):
                aliases[line[2]] = line[3]

            else:
                print("Aliases are not supported for '%s'" % line[1])

        # case 3:
        #    attack code! this is what this entire tool was built for...
        #    grammar is as follows:
        #    "attack <name> [with ([def|arm|pow|mat|rat] [-|+]<number>)+ end] \
        #            <name> [with ([def|arm|pow|mat|rat] [-|+]<number>)+ end]"
        #
        #    This structure allows for attacks to be computed both against
        #    basic stats and against modified stats, such as a +5 arm
        #    effect (Stryker's ult), a shield spell or soforth.
        elif(line[0] == "attack"):
            a_model = line[1]
            
            a_with = 2
            i = 2
            if(i < len(line) and line[i] == "with"):
                while(line[i] != "end" and i < len(line)):
                    i += 1
                if(i == len(line)):
                    print("Error, no 'end' found in the attacker modifier list!")
                else:
                    i += 1
            a_with = line[a_with:i]
                    
            d_model = line[i]

            i += 1
            d_with = i
            if(i < len(line) and line[i] == "with"):
                while(line[i] != "end" and i < len(line)):
                    i += 1
                if(i == len(line)):
                    print("Error, no 'end' found in the defender modifier list!")
                else:
                    i += 1
            d_with = line[d_with:i]

            # pull a_model's real name out of aliases
            while(not a_model in models and a_model in aliases):
                a_model = aliases[a_model]
            a_model = models[a_model]

            # pull d_model's real name out of aliases
            while(not d_model in models and d_model in aliases):
                d_model = aliases[d_model]
            d_model = models[d_model]

            print(a_model, a_with)
            print(d_model, d_with)

            # FIXME:
            #
            #    figure out how to apply the modifier list before
            #    evaluating the attack...
            evaluate_attack(a_model, d_model)

        # case 4:
        #   inspection code! this code allows a user to inspec the
        #   list of models and aliases which have been loaded thus far
        #   and hopefully verify that the commands are behaving as
        #   intended.
        elif(line[0] == "ls"):
            if(line[1] == "models"):
                print("loaded models:")
                for k in models:
                    print("  %s" % k)

            elif(line[1] == "aliases"):
                print("loaded aliases:")
                for k in aliases:
                    print("  %s -> %s" % (k, aliases[k]))

            else:
                print("Unknown ls subcommand '%s'!" % (apply(str, line[1:])))

        elif(line[0] == "reset"):
            print("Hard resetting models and aliases...")
            models = {}
            aliases = {}

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

    return (aliases, models)


if __name__ == '__main__':
    # Cortex
    #   a Warmachine strategery toolkit
    #
    #   Loads and interprets the file ~/.cortexrc as though all
    #   commands were being typed at the repl before dropping into
    #   read/eval/print mode for user IO.
    #
    aliases = {}
    models = {}

    if os.path.exists(os.path.abspath("~/.cortexrc")):
        #print("loading config file...")
        aliases, models = repl(open("~/.cortexrc"),
                               aliases=aliases,
                               models=models)

    repl(sys.stdin,
         aliases=aliases,
         models=models)