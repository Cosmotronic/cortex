#!/usr/bin/env python3
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0
import cortex.stats as stats
import cortex.wm as wm
import cortex.repl as repl

import sys
import json
import os
import os.path


def evaluate_attack(src_model, tgt_model):
    """Takes a pair of Model objects and computes the first's options to
    damage the second, printing a reasonable English table to Standard
    Out. Intended for REPL use, not yet suited for use by an AI in
    computing weapon selection.

    """

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
    if(len(src_model.weapons) > 0):
        for w in src_model.weapons:
            print("  using %s: (%s:%f)" % (w['name'], w['type'], w['rng']))
            pow = w['pow'] + (src_model.strength if w['type'] == 'melee' else 0)
            unboosted_dmg = stats.avg_damage(2, (pow - tgt_model.armor))
            boosted_dmg = stats.avg_damage(3, (pow - tgt_model.armor))
            
            print("    unbooosted: %d\n    boosted: %d"
                  % (unboosted_dmg, boosted_dmg))
    else:
        print("  No weapons on this model!")

    # FIXME
    #    This function should store the weapon damage and hit numbers
    #    and return it in a reasonable structure that an AI could make
    #    use of rather than barfing it to standard out and promptly
    #    forgetting about it.
    return None


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


def chunks(l, n):
    """Takes a sequence l and breaks it into length n chunks.

    Usage:
    >>> chunks([1, 2, 3, 4], 2)
    [[1, 2], [3, 4]]

    """
    return [l[i:i+n] for i in range(0, len(l), n)]

def parse_with(line, i):
    """Reads a 'with ... end' block out of an arguments list, given a
    start index and a list this returns a k:v map of the with params
    and the i at 'end' token.

    """
    with_list = []
    j = i
    if(i < len(line) and line[i] == "with"):
        while(line[i] != "end" and i < len(line)):
            print(i, line[i])
            if(i == len(line)):
                print("Error, no 'end' found in the attacker modifier list!")
            else:
                i += 1
        with_list = line[j+1:i]
    i += 1

    return ({a:int(b) for a,b in chunks(with_list,2)}, i)


def resolve_name(start, aliases):
    """Given an initial name and an aliases table, this function attempts
    to resolve a "final" or terminal name in the aliases sequence. If
    at any point the aliases table entry for the current name is None
    then the current name is returned.

    Note: This code does _not_ check for or prevent circular aliases.

    """
    while start in aliases:
        start = aliases[start]
    return start


def repl(file_like, aliases={}, models={}):

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
                line = shell_read_str(line)
                line = [s.strip() for s in line]

        # case -1:
        #    help code! gotta help t3h pplz out!
        if(line[0] == "help"):
            help(repl)

        # case 0:
        #    exit code! gotta be able to quit...
        elif(line[0] in ["quit", "exit", ":wq", ":q"]):
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
            a_with,i = parse_with(line, 2)
            d_with,i = parse_with(line, i)

            a_model = models[resolve_name(a_model, aliases)]
            d_model = models[resolve_name(d_model, aliases)]
            

            # FIXME
            #    apply the stat changes to a_model as specified

            # FIXME
            #    apply the stat changes to d_model as specified

            #############################################
            # now go ahead and do the attack evaluation #
            #############################################
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
