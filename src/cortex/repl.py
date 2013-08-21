#!/usr/bin/env python3
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0
import cortex.helpers as helpers
import cortex.wm as wm

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
        if(len(line) < 2):
            help(dispatch_load)
            return (env, False)

        # what are we loading?
        elif(line[1] == "models"):
            file = helpers.unixpath(line[2])
            if(os.path.exists(file)):
                new_models = {}
                try:
                    new_models = {m['name']:wm.Model(m)
                                  for m in json.load(open(file))}
                except ValueError as e:
                    print("Error parsing data file '%s':\n  %s" % (file, e))
                    return (env, True)

                _tmp = dict()
                _tmp.update(env['models'])
                _tmp.update(new_models)

                env['models'] = _tmp
                return (env, True)
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
        if(len(line) < 2):
            help(dispatch_alias)
            return (env, False)

        # what alias type are we creating?
        elif(line[1] == "model"):
            if(len(line) < 4):
                help(dispatch_alias)
                return (env, False)
            else:
                env['model aliases'][line[2]] = line[3]
                return (env, True)
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
        if(len(line) < 2):
            help(dispatch_ls)
            return (env, False)

        elif(line[1] == "models"):
            print("loaded models:")
            for k in env['models']:
                print("  %s" % k)

        elif(line[1] == "aliases"):
            print("loaded aliases:")
            for k in env['model aliases']:
                print("  %s -> %s" % (k, aliases[k]))

        else:
            print("Unknown ls subcommand '%s'!" % (" ".join(line[1:])))

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
    outcomes of such an attack. The <name> fields are resolved for
    aliases, so feel free to create shortcuts.

    Valid commands are:
        'attack <name> [with ([def|arm|pow|mat|rat|strength] [-|+|=]<number>)+ end]
                <name> [with ([def|arm|pow|mat|rat|strength] [-|+|=]<number>)+ end]'

    Examples:
        'attack Defender with mat +2 strength +5 end Lancer'
        'attack Defender Lancer'
        'attack estryker Defender'

    """
    if(line[0] == "attack"):
        if(len(line) < 3):
            help(dispatch_attack)
            return (env, False)

        else:
            a_model = line[1]
            a_with,i = helpers.parse_with(line, 2)
            d_model = line[i]
            i += 1
            d_with,i = helpers.parse_with(line, i)

            a_model = helpers.resolve_name(a_model,env['model aliases'])
            if a_model in env['models']:
                a_model = env['models'][a_model]
            else:
                print("ERROR: model %s was not found! aborting..." % a_model)
                return (env, False)

            d_model = helpers.resolve_name(d_model,env['model aliases'])
            if d_model in env['models']:
                d_model = env['models'][d_model]
            else:
                print("ERROR: model %s was not found! aborting..." % d_model)
                return (env, False)

            def update_fn(stat_map):
                def closured_fn(state):
                    """A semantic closure hack to implement a real lambda with an
                    environment. Friggin python man.

                    """
                    attr_aliases = {'str':'strength','def':'defense','arm':'armor'}
                    for key in stat_map:
                        tgt_key = key
                        # a little hack to get the str alias..
                        if key in attr_aliases:
                            tgt_key = attr_aliases[key]
                        # throw a warning and continue for weird keys..
                        if tgt_key not in state:
                            print("WARNING: modifier for %s ignored!" % key)
                            continue

                        # parse and apply the val!
                        val = stat_map[key]
                        if(val[0] == '-'):
                            state[tgt_key] -= int(val[1:])
                        elif(val[0] == '='):
                            state[tgt_key] = int(val[1:])
                        elif(val[0] == '+'):
                            state[tgt_key] += int(val[1:])
                        else:
                            state[tgt_key] += int(val)
                    return state
                return closured_fn

            a_id = a_model.addEffect(update_fn(a_with))
            d_id = d_model.addEffect(update_fn(d_with))

            # just for grins print the current stats..
            print("\nattacking:")
            print(str(a_model))
            print("\ndefending:")
            print(str(d_model))
            print("\n")

            # now go ahead and do the attack evaluation #
            wm.evaluate_attack(a_model, d_model)

            # remove those effects from the models..
            a_model.removeEffect(a_id)
            d_model.removeEffect(d_id)

            # and return!
            return (env, True)
    else:
        return (env, False)

_dispatch['attack']=dispatch_attack


def dispatch_help(line, env={}):
    """Help code!

    This code serves to inform users of what Cortex has to offer and
    assist users in understanding how to use Cortex effectively by
    providing command documentation and sample usages.

    Commands are parsed naively, splitting at spaces unless reading a
    quoted string, string escaping is not supported.

    Examples:
        'help foo bar baz'    -> ['help', 'foo', 'bar', 'baz']
        'help "foo bar" baz'  -> ['help', 'foo bar', 'baz']
        'help "foo 'bar' baz" -> ['help', 'foo \'bar\' baz']

    Stuff that will break:
        'help "foo bar baz'      <- all quotes must be matched
        'help "foo \"bar\" baz"' <- escaping is not permitted

    Valid commands are:
        'help'           - lists all commands
        'help <command>' - prints the help info for a command

    """
    if(line[0] == "help"):
        if(len(line) > 1):
            if line[1] in _dispatch:
                help(_dispatch[line[1]])
                return (env, True)
            else:
                print("No such command %s" % line[1])
                return (env, False)
        else:
            print("Valid commands are:")
            for fn in _dispatch:
                print("  %s" % fn)
            return (env, True)
    else:
        return (env, False)

_dispatch['help']=dispatch_help


def dispatch_stats(line, env={}):
    """Stat printing code!

    Because `ls card <card>` doesn't make any damn sense we have stats! Stats
    exists to print the stat line and weapons stats for some card, and operates
    by looking up the stats from the env object and then writing them to
    standard out.

    Valid commands:
        'stats <card>'

    """
    if(line[0] == "stats"):
        if(len(line) >= 2 and line[1] in env['models']):
            model = env['models'][helpers.resolve_name(line[1],
                                                       env['model aliases'])]
            print(str(model))
        return (env, True)

    else:
        return (env, False)

_dispatch['stats'] = dispatch_stats


################################################################################
################ now use the _dispatch table to execute commands ###############
################ below this point there should never be changes  ###############
################################################################################
def dispatch(line, env={}):
    if (line[0] in _dispatch):
        return _dispatch[line[0]](line, env=env)
    else:
        return (env, False)
