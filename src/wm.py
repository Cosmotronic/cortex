#!/usr/bin/env python

def roll_combinatons(n_dice, val):
    if(n_dice == 0):
        return 0

    elif(n_dice == 1 and val > 0 and val < 7):
        return 1

    else:
        combos = 0
        for i in range(1, 7):
            if(val > i):
                combos += roll_combinatons(n_dice - 1, val - i)
        return combos


def odds_of_beating(dice, threshold):
    integ = 0

    for i in range(threshold, 6 * dice + 1):
        integ += roll_combinatons(dice, i)

    return float(integ) / (6.0 ** dice)


def avg_damage(dice, modifier):
    dmg = 0
    combos = 0

    for i in range(dice, 6 * dice + 1):
        tmp_c = roll_combinatons(dice, i)
        combos += tmp_c

        if(i + modifier > 0):
            dmg += (i + modifier) * tmp_c

    return float(dmg) / float(combos)


def damage(r1, r2):
    mat,d1,defence = r1
    pow,d2,arm = r2

    return ("%f%% to hit, %f average dmg dealt" 
            % (odds_of_beating(d1, (defence - mat)),
               avg_damage(d2, (pow - arm))))
    
