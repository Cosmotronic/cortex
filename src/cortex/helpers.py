#!/usr/bin/env python3
# Authored by Reid "arrdem" McKenzie, 10/09/2013
# Licenced under the terms of the EPL 1.0


import os.path


def unixpath(p):
    return os.path.expanduser(os.path.expandvars(p))


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
