#!/usr/bin/env python3
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0
import stats

# imports first
import json
import copy
import os
import uuid
import re


# class decls
class Model():
    """Model is the relatively abstract base class for most models in the
    Warmachine tabletop game. The concept of a Model is that it is an active
    piece on the board, and is consequently required to exhibit the following
    basic attributes common to all pieces.

    Models are inteded to be serialized into and from a JSON object as so:
    {"name":<string name>,
     "type":<one of ["solo", "warcaster", "warjack", "construct", "model"]>,
     "size":<base size of model>,
     "attrs":{"speed":<speed value>,
              "strength":<strength value>,
              "mat":<mele attack base>,
              "rat":<ranged attack base>,
              "defense":<defense base>,
              "armor":<armor base>,
              "cmd":<command value>,
              "boxes":<list of boxes per column>,

              // other meaningful keys
              ["fist":<fist count>,]
              ["focus":<focus value>,]
              ["pc":<point cost>,]

              // boolean flag keys
              // presence requires that they have the value of true,
              // absence means they will get the value of false.
              ["abomination":<bool>,            // invokes terror rules]
              ["advanced deployment":<bool>,    // deploys farther]
              ["aggressive":<bool>,             // charges & runs for free]
              ["arc node":<bool>,               // can relay spells]
              ["buckler":<bool>,                // has a shield (+1 arm)]
              ["character":<bool>,              // model is unique]
              ["cma":<bool>,                    // can participate in a cma]
              ["conductor":<bool>,              // counts as a stormcaller]
              ["cra":<bool>,                    // can participate in a cra]
              ["extended control range":<bool>, // double ctrl radius]
              ["fearless":<bool>,               // ignores terror rules]
              ["follow up":<bool>,              // can advance after slamming]
              ["immunity":{ ... },              // ignores typed damage]
              ["officer":<bool>,                // is considered an officer]
              ["parry":<bool>,                  // no free strikes]
              ["pathfinder":<bool>,             // ignores terain]
              ["set defense":<bool>,            // cannot be slammed]
              ["shield":<bool>,                 // has a shield (+2 arm)]
              ["shock field":<bool>,            // slamming models are hit]
              ["standard bearer":<bool>,        // has a flag]
              ["warjack marshal":<bool>,        // can marshal a jack]
              },
    "weapons":[{"name":<string name>,
                "type":<one of ["ranged", "mele"]>,
                "rng":<0.25 or 2 if "type":"mele", else range>,
                "pow":<integer power, mele weapons should use P not P+S >,
                ["rof":<integer rof if "type":"ranged">,]
                "attrs":{// boolean flags
                         ["magical":<bool>,]
                         ["disruption":<bool>,]
                         ["cold":<bool>,]
                         ["corrosion":<bool>,]
                         ["electricity":<bool>,]
                         ["fire":<bool>,]
                        }}
               ....]
    "allowance":<max field allowance for the model,
                 inf if not present>,
    }

    FIXME: The only issue with this representation is that it provides
        no nice way to represent spells and effects. Some effects are
        entirely unique which would mean that implementing a new card
        would require a patch of some sort to the engine core, but
        others (such as the Cygnar Snipe) are relatively common and
        could be reused rather than repeated.

        On the one hand I'm loath to allow for the use of (eval) to
        load code from what should strictly be a configuration file,
        but on the other hand especially for complicated cards I see
        no other reasonable way to provide for potentially piece
        behavior.

    FIXME: This provides no reasonable way to represent a collection
        of singular models, such as Stormblade Infantry (as a block of
        6/9 or Trencher Infantry). How to represent a group of models?

    """

    def __init__(self, serialized_form):
        """Initializes a Model object from a serialized representation.

        Sets the name, type, size, weapons and effects fields, then
        updates the model.

        """
        # preserve the serialized form...
        self._attrs = serialized_form
        #print(serialized_form)

        # set some fields for ease of access
        self.name = self._attrs['name']
        self.type = self._attrs['type']
        self.size = self._attrs['size']
        self.weapons = self._attrs['weapons']
        self.effects = {}

        # compute an ID value which uniquely identifies this model
        self.id = uuid.uuid4()

        # compute update for the other fields
        self.update()

    def update(self):
        """Recomputes the Model's attrs from the statline and effects. Note
        that this function side effects the spd, str, mat, rat, def,
        arm, cmd, focus, 'jack points', boxes and pc fields. Returns
        None.

        """

        # take basic attributes
        attrs = copy.deepcopy(self._attrs['attrs'])

        # compute updates on the basis of effects
        for key,e in self.effects:
            attrs = e(attrs)

        # set fields in self for ease of access defaulting to 0
        for key in ["speed","strength","mat","rat","defence","armor","cmd","focus",
                    "jack points","boxes","pc"]:
            v = None
            try:
                v = attrs[key]
            except KeyError:
                v = 0

            self.__dict__[key] = v

    def addEffect(self, fn, id=None):
        """Adds an effect fn to the Model's effects map. The key is the id
        argument if it is set, otherwise a uuid will be generated and
        used. The used key is the only value returned.

        """
        id = id or uuid.uuid4()
        self.effects[id] = fn
        return id

    def removeEffect(self, id):
        """Removes an effect from the Model's effects map by uuid/id. Returns
        None, side effecting the effects map.

        """
        self.effects.pop(id)


class Army():
    """The basic representation for a whole bunch of units"""
    def __init__(self, name=None):
        self.list = {}
        self.name = name
        self.points = 0

    def simpleLoad(self, models, file, aliases=None):
        """Reads a simple text file army listing and returns a list of Model
        objects constututing the list as described in the read file. Aliases
        is a map of nicknames to a "real" names and is just a hack to let
        people write stuff like pCaine and eHaley in their army lists and let
        Cortex understand what they "really" mean.

        Army file grammar is '<number> [xX]? <name> \n?\r?,?'.
        Lines starting with # are comments and are ignored.

        FIXME: This code does not currently check model counts against
               field allowance. This is a bug and should be fixed,
               exceeding field allowance should generate at least some
               warning prints.
        """

        army = {}
        pattern = re.compile("([0-9]+) [xX]? ([^\n\r,]+)((\r?\n\r?)|,)")
        for line in file.readlines():
            if line[0] == '#':
                continue
            else:
                num,name,_ = re.match(pattern,line)
                model = None
                # try to just load the model...
                if name in models:
                    model = models[name]
                    # fall back to aliases...
                elif name in aliases:
                    model = models[aliases[name]]
                    # bitch loudly
                else:
                    raise Exception("Unknown model '%s'!" % name)

                m = Model(model._attrs)
                army[m.id] = m

        self.list = army
        self.update()
        return None

    def simpleDump(self, file):
        """Serializes an Army back out to a file in the same format that
        armies are read in. Realisticaly this should use a real
        serialization system rather than a custon reader/writer pair
        but we'll go with this for now because it's dead simple and a
        real human could write an army file.

        """

        count = {}
        for k,m in self.list:
            count[m.name] = (count[m.name] or 0) + 1

        f.write("# automaticly dumped army\n")
        f.write("# name %s\n" % self.name)
        for name,c in count:
            f.write("%s x %s\n" % (c, name))
        return None

    def jsonLoad(self, models, file, aliases=None):
        """Load an army from a JSON file!

        Loads a JSON file presumed to have a .name and .list, where
        .list is a list of string names or abbreviations for model
        names. After rendering the json object to a map, this code
        then renders the list of model names into the Army standard
        {id:instance} map, and finally side effects the self object
        into the constructed object.

        Usage:
            >>> foo = Army()
            >>> open("myarmy.txt").read()
            "{'name':'myarmy','list':['Squire', 'Lutenant Allister Caine']}"
            >>> foo.jsonLoad(open("myarmy.txt"))
            >>> foo.name
            "myarmy"
            >>> map(lambda (k,v): v.name, foo.list)
            ["Squire", "Lutenant Allister Caine"]

        """
        inbj = json.loads(file.read(),
                          object_hook=lambda x: Army(Object(), x))
        army = {}
        for name in inbj.list:
            model = None
            # try to just load the model...
            if name in models:
                model = models[name]
                # fall back to aliases...
            elif name in aliases:
                model = models[aliases[name]]
                # bitch loudly
            else:
                raise Exception("Unknown model '%s'!" % name)

            m = Model(model._attrs)
            army[m.id] = m

        inbj.list = army
        self = inbj
        return None

    def jsonDump(self, file):
        """Dump an army to a JSON file!

        Naively sanitizes the self object by reducing the list map to
        a list of Model .name fields, then blindly dumps the result to
        a file. Only the .list field is guranteed, all others are up
        in the air. Care should be taken so that this does not leak
        weird runtime specific data such as UUID maps and lists.

        """

        outbj = copy.copy(self)
        outbj.list = map(lambda k,v: v.name, self.list)
        json.dump(outbj, file)
        return None

    def update(self):
        """Recomputes the point value of an army. Intended use after loading
        an army list or as part of an AI for evaluating effective
        strength of an army after resolving some effects or attack.

        """

        pointval = 0
        warcaster = false
        for id,m in self.list:
            if(m['type'] == "warcaster"):
                pointval -= m['jack points']
                if not warcaster:
                    warcaster = true
                else:
                    pointval += m['pc']
            else:
                pointval += m['pc']
        self.points = pointval
        return None


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

