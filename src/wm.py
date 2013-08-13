#!/usr/bin/env python
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0

import json


class Model():
    """Model is the relatively abstract base class for most models in the
    Warmachine tabletop game. The concept of a Model is that it is an active
    piece on the board, and is consequently required to exhibit the following
    basic attributes common to all pieces.

    Models are inteded to be serialized into and from a JSON object as so:
    {"name":<string name>,
     "type":<one of ["solo", "warcaster", "warjack", "unit"]>,
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
              ["pc":<point cost>,]
              ["focus":<focus value>,]

              // boolean flag keys
              // presence requires that they have the value of true,
              // absence means they will get the value of false.
              ["cra":<bool>,             // can participate in a cra]
              ["cma":<bool>,             // can participate in a cma]
              ["warjack marshal":<bool>, // can marshal a jack]
              ["officer":<bool>,         // is considered an officer]
              ["standard bearer":<bool>, // has a flag]
              ["shield":<bool>,          // has a shield (+2 arm)]
              ["fearless":<bool>,        // ignores terror rules]
              ["abomination":<bool>,     // invokes terror rules]
              ["immunity":{ ... },       // ignores typed damage]
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

    Note:
        "model" relatively nicely provides not only for single models
        such as casters, but also for model groups thus allowing a
        squad of stormblades to be represented as the compose of the
        individuals.

    FIXME:
        The only issue with this representation is that it provides no
        nice way to represent spells and effects. Some effects are
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
