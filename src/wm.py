#!/usr/bin/env python
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0

# imports first
import json
import copy
import os
import stats
import uuid

# class decls
class Model():
    """Model is the relatively abstract base class for most models in the
    Warmachine tabletop game. The concept of a Model is that it is an active
    piece on the board, and is consequently required to exhibit the following
    basic attributes common to all pieces.

    Models are inteded to be serialized into and from a JSON object as so:
    {"name":<string name>,
     "type":<one of ["solo", "warcaster", "warjack", "unit", "construct"]>,
     "size":<base size of model>,
     "attrs":{"spd":<speed value>,
              "str":<strength value>,
              "mat":<mele attack base>,
              "rat":<ranged attack base>,
              "def":<defense base>,
              "arm":<armor base>,
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
    [// present only in "type":"unit" records
     "models":[{"name":<name of model in unit>,
                "min":{"pc":<point cost for bringing min models>,
                       "count":<count of models to bring at cost>},
                "max":<see min for structure>},
               ... <for other models>]]
    }

    Note: "model" relatively nicely provides not only for single
        models such as casters, but also for model groups thus
        allowing a squad of stormblades to be represented as the
        compose of the individuals.

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

    """

    def __init__(self, serialized_form):
        """Initializes a Model object from a serialized representation.

        Sets the name, type, size, weapons and effects fields, then
        updates the model.

        """
        # preserve the serialized form...
        self._attrs = serialized_form

        # set some fields for ease of access
        self.name = self._attrs['name']
        self.type = self._attrs['type']
        self.size = self._attrs['size']
        self.weapons = self._attrs['weapons']
        self.effects = {}

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
        for key in ["spd","str","mat","rat","def","arm","cmd","focus",
                    "jack points","boxes","pc"]:
            self.__dict__[key] = attrs[key] or 0

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


class Unit():
    """Unit is the basic representation for a group of models. Fundimentally it
    is a list of models, being unit members, commanders, attachments and other
    such Model type pieces.

    FIXME: How exactly do Models interact with the Unit? What purpose
           does Unit serve? How is Unit serialized & read differently
           from Model?

    """


# helper fns..


# and now for main
if __name__ == "__main__":
    print("Cortex doesn't do anything yet!")
