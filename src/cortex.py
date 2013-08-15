#!/usr/bin/env python3
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0
import stats
import wm


def evaluate_attack(src_model, tgt_model):
    mele_weps = [w for w in src_model.weapons if w.type == "melee"]
    ranged_weps = [w for w in src_model.weapons if w.type == "ranged"]
    
    # compute boosted/unboosted hit odds
    unboosted_ranged_hit = stats.odds_of_beating(2, (tgt_model.defence - src_model.rat))
    boosted_ranged_hit = stats.odds_of_beating(3, (tgt_model.defence - src_model.rat))
    print("  Hit odds with ranged weapons:\n  unboosted: %f\n  boosted: %f"
          % (unboosted_ranged_hit, boosted_ranged_hit))
        
    unboosted_melee_hit = stats.odds_of_beating(2, (tgt_model.defence - src_model.mat))
    boosted_melee_hit = stats.odds_of_beating(3, (tgt_model.defence - src_model.mat))
    print("  Hit odds with melee weapons:\n  unboosted: %f\n  boosted: %f"
          % (unboosted_melee_hit, boosted_melee_hit))

    print("  Damage options:")
    # compute the boosted/unboosted damage outcomes
    for w in src_model.weapons:
        print("  using weapon %s:" % w.name)
        unboosted_dmg = stats.avg_damage(2, (w['pow'] - arm))
        boosted_dmg = stats.avg_damage(3, (w['pow'] - arm))

        print("    unbooosted: %d\n    boosted: %d" 
              % (unbooosted_dmg, boosted_dmg))


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


if __name__ == '__main__':
    # Cortex
    #   a Warmachine strategery toolkit
    #
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
    # "alias model <alias> <name>
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
    
    while True:
        line = []
        line = raw_input("->> ")
        line = shell_read_str(line)
        
        # case 0: 
        #    exit code! gotta be able to quit...
        if(line[0] in ["quit", "exit", ":wq", ":q"]):
            return 0
            
        # case 1:
        #    load code! gotta be able to read in datafiles...
        elif(line[0] == "load"):
            # what are we loading?
            if(line[1] == "models"):
                pass
                
            elif(line[1] == "aliases"):
                pass
                
            else:
                pass
                
        # case 2:
        #    alias code! I want to be able to create aliases...
        elif(line[0] == "alias"):
            # what alias type are we creating?
            if(line[1] == "cmd"):
                pass
            elif(line[1] == "model"):
                pass
                
            else:
                pass
                
        # case 3 
        #    attack code! this is what this entire tool was built for...
        #    grammar is as follows:
        #    "attack <name> [with [def|arm|pow|mat|rat]:[-|+]<number>+ end] \
        #            <name> [with [def|arm|pow|mat|rat]:[-|+]<number>+ end]"
        #
        #    This structure allows for attacks to be computed both against
        #    basic stats and against modified stats, such as a +5 arm
        #    effect (Stryker's ult), a shield spell or soforth.
        elif(line[0] == "attack"):
            pass

        elif(line[0] == "reset"):
            pass
    
        else:
            print("Unknown command!")
        
    
