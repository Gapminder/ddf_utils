# -*- coding: utf-8 -*-
"""string functions for ddf files"""

import re
import numpy as np
from unidecode import unidecode


# TODO: make the sub parameter just a list of string, not expr
# using re.escape()
def to_concept_id(s, sub='[/ -\.\*";]+', sep='_'):
    '''convert a string to lowercase alphanumeric + underscore id for concepts'''
    if s is np.nan:
        return s

    s1 = re.sub(sub, sep, s.strip())
    s1 = s1.replace('\n', '')

    # remove the first/last underscore
    if s1[-1] == sep:
        s1 = s1[:-1]
    if s1[0] == sep:
        s1 = s1[1:]

    return unidecode(s1.lower())
