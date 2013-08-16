#!/usr/bin/env python3
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0
import helpers
import wm

import os.path
import json

_dispatch = {}


def dispatch_load(line, env={}):
    """Load code! gotta be able to read in datafiles...  

    This function takes responsability for loading models and when
    they are implemented aliases and armies from long term storage in
    serialized forms to Cortex's runtime for analysis.

    As this is a refactored block out of cortex/repl, the invocation
    is simply (line, env={ .. }). As with the other dispatch_*
    functions this function returns an (env, code) pair, where code is
    true if this was the correct function and it ran, else false.

    Valid commands are:
        'load models <filename>'

    """
    if(line[0] == "load"):
        # what are we loading?
        if(line[1] == "models"):
            if(os.path.exists(os.path.abspath(line[2]))):
                new_models = {}
                try:
                    new_models = {m['name']:wm.Model(m)
                                  for m in json.load(open(line[2]))}
                except ValueError as e:
                    print("Error parsing data file '%s':\n  %s" % (line[2], e))
                    return (env, True)

                env['models'] = dict(env['models'].items() + new_models.items())
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
        return (env, True)
    else:
        return (env, False)

_dispatch['load'] = dispatch_load


def dispatch_alias(line, env={}):
    """Alias code! I want to be able to create aliases for models...

    This function takes responsability for 

    As this is a refactored block out of cortex/repl, the invocation
    is simply (line, env={ .. }). As with the other dispatch_*
    functions this function returns an (env, code) pair, where code is
    true if this was the correct function and it ran, else false.

    Valid commands are:
        'alias model <alias> <model name>'

    Note that no checking is done to prevent the creation of circular
    aliases!

    """
    if(line[0] == "alias"):
        # what alias type are we creating?
        if(line[1] == "model"):
            env['model aliases'][line[2]] = line[3]
        else:
            print("Aliases are not supported for '%s'" % line[1])
        return (env, True)
    else:
        return (env, False)

_dispatch['alias']=dispatch_alias


def dispatch_ls(line, env={}):
    """Inspection code! 
    
    this code allows a user to inspect the list of models and aliases
    which have been loaded thus far and hopefully verify that the
    loading commands are behaving as intended.

    As this is a refactored block out of cortex/repl, the invocation
    is simply (line, env={ .. }). As with the other dispatch_*
    functions this function returns an (env, code) pair, where code is
    true if this was the correct function and it ran, else false.

    Valid commands are:
        'ls models'
        'ls aliases'

    """
    if(line[0] == "ls"):
        if(line[1] == "models"):
            print("loaded models:")
            for k in env['models']:
                print("  %s" % k)

        elif(line[1] == "aliases"):
            print("loaded aliases:")
            for k in env['model aliases']:
                print("  %s -> %s" % (k, aliases[k]))

        else:
            print("Unknown ls subcommand '%s'!" % (apply(str, line[1:])))
        return (env, True)
    else:
        return (env, False)

_dispatch['ls']=dispatch_ls


def dispatch_reset(line, env={}):
    """Reset code!

    If something goes horribly wrong, this is how you reset cortex
    back to normal! This command allways succeeds if it is the
    intended command, and returns an empty env map thus clobbering any
    weirdness a user or a rogue config file could perpetrate.

    As this is a refactored block out of cortex/repl, the invocation
    is simply (line, env={ .. }). As with the other dispatch_*
    functions this function returns an (env, code) pair, where code is
    true if this was the correct function and it ran, else false.

    Valid commands are:
        'reset'

    """
    # FIXME:
    #    This code relies on a hard coded "basic env" object which
    #    should be shared with the code in the cortex core so that
    #    changes to the minimum state of the env only have to occur in
    #    one place.
    if(line[0] == "reset"):
        print("Hard resetting models and aliases...")
        return ({'models':{}, 'model aliases':{}}, True)
    else:
        return (env, False)

_dispatch['reset']=dispatch_reset


def dispatch_attack(line,env={}):
    """Attack code! 

    This is what this entire tool was built for... It parses an attack
    description, being one model vs another, then computes and dumps a
    stats table projecting the success likelyhoods and average
    outcomes of such an attack.

    Valid commands are:
        'attack <name> [with ([def|arm|pow|mat|rat] [-|+]<number>)+ end] \
                <name> [with ([def|arm|pow|mat|rat] [-|+]<number>)+ end]'

    """
    if(line[0] == "attack"):
        a_model = line[1]
        a_with,i = helpers.parse_with(line, 2)
        d_model = line[i]
        i += 1
        d_with,i = helpers.parse_with(line, i)

        a_model = env['models'][helpers.resolve_name(a_model, env['model aliases'])]
        d_model = env['models'][helpers.resolve_name(d_model, env['model aliases'])]

        # FIXME
        #    apply the stat changes to a_model as specified

        # FIXME
        #    apply the stat changes to d_model as specified

        #############################################
        # now go ahead and do the attack evaluation #
        #############################################
        wm.evaluate_attack(a_model, d_model)

        return (env, True)
    else:
        return (env, False)

_dispatch['attack']=dispatch_attack


################################################################################
################ now use the _dispatch table to execute commands ###############
################ below this point there should never be changes  ###############
################################################################################
def dispatch(line, env={}):
    if (line[0] in _dispatch):
        return _dispatch[line[0]](line, env=env)
    else:
        return (env, False)
