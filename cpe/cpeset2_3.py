#! /usr/bin/env python
# -*- coding: utf-8 -*-


'''
This file is part of cpe package.

This module is an implementation of name matching
algorithm in accordance with version 2.3 of CPE (Common Platform
Enumeration) specification.

Copyright (C) 2013  Alejandro Galindo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

For any problems using the cpe package, or general questions and
feedback about it, please contact: galindo.garcia.alejandro@gmail.com.
'''

from cpe import CPE
from cpe2_3 import CPE2_3
from cpe2_3_wfn import CPE2_3_WFN


class CPESet2_3(object):
    """
    Represents a set of CPEs.

    This class allows:
    - create set of CPE elements.
    - match a CPE element against a set of CPE elements.
    """

    ###############
    #  CONSTANTS  #
    ###############

    # Possible set relations between a source WFN and a target WFN:
    # - The source is a SUPERSET of the target
    # - The source is a SUBSET of the target
    # - The source and target are EQUAL
    # - The source and target are mutually exclusive or DISJOINT
    # - The target has wild cards and the result is undefined
    LOGICAL_VALUE_SUPERSET = 1
    LOGICAL_VALUE_SUBSET = 2
    LOGICAL_VALUE_EQUAL = 3
    LOGICAL_VALUE_DISJOINT = 4
    LOGICAL_VALUE_UNDEFINED = 5

    ###################
    #  CLASS METHODS  #
    ###################

    @classmethod
    def cpe_disjoint(cls, source, target):
        """
        Compares two WFNs and returns True if the set-theoretic relation
        between the names is DISJOINT.

        Input
            - Two WFNs: source WFN y target WFN
        Output
            - Returns True if the set relation between source and target
            is DISJOINT, otherwise False.
        """

        result_dict = CPESet2_3.compare_wfns(source, target)

        # If any pairwise comparison returned DISJOINT  then
        # the overall name relationship is DISJOINT
        for att in CPE2_3_WFN.wfn_part_keys:
            result = result_dict[att]

            isDisjoint = result == CPESet2_3.LOGICAL_VALUE_DISJOINT
            if isDisjoint:
                return True
        return False

    @classmethod
    def cpe_equal(cls, source, target):
        """
        Compares two WFNs and returns True if the set-theoretic relation
        between the names is EQUAL

        Input
            - Two WFNs: source WFN y target WFN
        Output
            - Returns True if the set relation between source and target
            is EQUAL, otherwise False.
        """

        result_dict = CPESet2_3.compare_wfns(source, target)

        # If any pairwise comparison returned EQUAL then
        # the overall name relationship is EQUAL
        for att in CPE2_3_WFN.wfn_part_keys:
            result = result_dict[att]

            isEqual = result == CPESet2_3.LOGICAL_VALUE_EQUAL
            if not isEqual:
                return False
        return True

    @classmethod
    def cpe_subset(cls, source, target):
        """
        Compares two WFNs and returns True if the set-theoretic relation
        between the names is (non-proper) SUBSET.

        Input
            - Two WFNs: source WFN y target WFN
        Output
            - Returns True if the set relation between source and target
            is SUBSET, otherwise False.
        """

        result_dict = CPESet2_3.compare_wfns(source, target)

        # If any pairwise comparison returned something other than SUBSET
        # or EQUAL, then SUBSET is False.
        for att in CPE2_3_WFN.wfn_part_keys:
            result = result_dict[att]

            isSubset = result == CPESet2_3.LOGICAL_VALUE_SUBSET
            isEqual = result == CPESet2_3.LOGICAL_VALUE_EQUAL
            if (not isSubset) and (not isEqual):
                return False
        return True

    @classmethod
    def cpe_superset(cls, source, target):
        """
        Compares two WFNs and returns True if the set-theoretic relation
        between the names is (non-proper) SUPERSET.

        Input
            - Two WFNs: source WFN y target WFN
        Output
            - Returns True if the set relation between source and target
            is SUPERSET, otherwise False.
        """

        result_dict = CPESet2_3.compare_wfns(source, target)

        # If any pairwise comparison returned something other than SUPERSET
        # or EQUAL, then SUPERSET is False.
        for att in CPE2_3_WFN.wfn_part_keys:
            result = result_dict[att]

            isSuperset = result == CPESet2_3.LOGICAL_VALUE_SUPERSET
            isEqual = result == CPESet2_3.LOGICAL_VALUE_EQUAL
            if (not isSuperset) and (not isEqual):
                return False

        return True

    @classmethod
    def compare_wfns(cls, source, target):
        """
        Compares two WFNs and returns a list of pairwise attribute-value
        comparison results. It provides full access to the individual
        comparison results to enable use-case specific implementations
        of novel name-comparison algorithms.

        Compare each attribute of the Source WFN to the Target WFN:
        Input
            - Two WFNs: source WFN y target WFN
        Output
            - List of pairwise attribute comparison results
        """

        # Create a new associative array table implemented as a dictionary
        result = dict()

        # Compare results using the get() function in WFN
        for att in CPE2_3_WFN.wfn_part_keys:
            result[att] = CPESet2_3.compare(source.get_value(att), target.get_value(att))

        return result

    @classmethod
    def compare(cls, source, target):
        """
        Compares two values associated with a attribute of two WFNs.
        This function is a support function for compare_WFNs.

        Input
            - A pair of attribute values, which may be logical values
             (ANY or NA) or string values.
        Output
            - The attribute comparison relation.

        - TEST:
        >>> CPESet2_3.compare("a", "a")
        3

        - TEST:
        >>> CPESet2_3.compare("Adobe", "ANY")
        2

        - TEST:
        >>> CPESet2_3.compare("ANY", "Reader")
        1

        - TEST:
        >>> CPESet2_3.compare("9.*", "9.3.2")
        1

        - TEST:
        >>> CPESet2_3.compare("ANY", "NA")
        1

        - TEST:
        >>> CPESet2_3.compare("PalmOS", "NA")
        4

        - TEST:
        >>> CPESet2_3.compare("8\.\*", "8\.\*")
        3
        """

        if (CPESet2_3.is_string(source)):
            source = source.lower()
        if (CPESet2_3.is_string(target)):
            target = target.lower()

        # In this specification, unquoted wildcard characters in the target
        # yield an undefined result

        if (CPESet2_3.is_string(target) and
           CPESet2_3.contains_wildcards(target)):
            return CPESet2_3.LOGICAL_VALUE_UNDEFINED

        # If source and target attribute values are equal,
        # then the result is EQUAL
        if (source == target):
            return CPESet2_3.LOGICAL_VALUE_EQUAL

        # If source attribute value is ANY, then the result is SUPERSET
        if ((source == CPE2_3_WFN.VALUE_ANY_VALUE) or
           (source == CPE2_3_WFN.VALUE_NULL)):
            return CPESet2_3.LOGICAL_VALUE_SUPERSET

        # If target attribute value is ANY, then the result is SUBSET
        if ((target == CPE2_3_WFN.VALUE_ANY_VALUE) or
           (target == CPE2_3_WFN.VALUE_NULL)):
            return CPESet2_3.LOGICAL_VALUE_SUBSET

        # If either source or target attribute value is NA
        # then the result is DISJOINT
        isSourceNA = source == CPE2_3_WFN.VALUE_NOT_APPLICABLE
        isTargetNA = target == CPE2_3_WFN.VALUE_NOT_APPLICABLE

        if (isSourceNA or isTargetNA):
            return CPESet2_3.LOGICAL_VALUE_DISJOINT

        # If we get to this point, we are comparing two strings
        return CPESet2_3.compareStrings(source, target)

    @classmethod
    def compareStrings(cls, source, target):
        """
        Compares a source string to a target string,
        and addresses the condition in which the source string
        includes unquoted special characters.

        It performs a simple regular expression match,
        with the assumption that (as required) unquoted special characters
        appear only at the beginning and/or the end of the source string.

        It also properly differentiates between unquoted and quoted
        special characters.

        - TEST:
        >>> CPESet2_3.compareStrings("and", "not") == CPESet2_3.LOGICAL_VALUE_DISJOINT
        True

        - TEST:
        >>> CPESet2_3.compareStrings("mac*", "not") == CPESet2_3.LOGICAL_VALUE_DISJOINT
        True

        - TEST:
        >>> CPESet2_3.compareStrings("mac*", "mac") == CPESet2_3.LOGICAL_VALUE_SUPERSET
        True
        """

        start = 0
        end = len(source)
        begins = 0
        ends = 0

        # Reading of initial wildcard in source
        if source.startswith(CPE2_3_WFN.WILDCARD_MULTI):
            # Source starts with "*"
            start = 1
            begins = -1
        else:
            while ((start < len(source)) and
                   source.startswith(CPE2_3_WFN.WILDCARD_ONE, start, start)):
                # Source starts with one or more "?"
                start += 1
                begins += 1

        # Reading of final wildcard in source
        if (source.endswith(CPE2_3_WFN.WILDCARD_MULTI) and
           CPESet2_3.isEvenWildcards(source, end - 1)):

            # Source ends in "*"
            end -= 1
            ends = -1
        else:
            while ((end > 0) and
                   source.endswith(CPE2_3_WFN.WILDCARD_ONE, end - 1, end - 1) and
                   CPESet2_3.isEvenWildcards(source, end - 1)):

                # Source ends in "?"
                end -= 1
                ends += 1

        source = source[start: end]
        index = -1
        leftover = len(target)

        while (leftover > 0):
            index = target.find(source, index + 1)
            if (index == -1):
                break
            escapes = target.count("\\", 0, index)
            #escapes = countEscapeCharacters(target, 0, index)
            if ((index > 0) and (begins != -1) and
               (begins < (index - escapes))):

                break

            escapes = target.count("\\", index + 1, len(target))
            #escapes = countEscapeCharacters(target, index+1, len(target))
            leftover = len(target) - index - escapes - len(source)
            if ((leftover > 0) and ((ends != -1) and (leftover > ends))):
                continue

            return CPESet2_3.LOGICAL_VALUE_SUPERSET

        return CPESet2_3.LOGICAL_VALUE_DISJOINT

    @classmethod
    def is_string(cls, arg):
        """
        Return True if arg is a string value,
        and False if arg is a logical value (ANY or NA).

        This function is a support function for compare().

        - TEST:
        >>> CPESet2_3.is_string("ANY")
        False

        - TEST:
        >>> CPESet2_3.is_string("NA")
        False

        - TEST:
        >>> CPESet2_3.is_string("otherValue")
        True
        """

        isAny = arg == CPE2_3_WFN.VALUE_ANY_VALUE
        isNa = arg == CPE2_3_WFN.VALUE_NOT_APPLICABLE
        isNull = arg == CPE2_3_WFN.VALUE_NULL

        return not (isAny or isNa or isNull)

    @classmethod
    def contains_wildcards(cls, s):
        """
        Return True if the string contains any unquoted special characters
        (question-mark or asterisk), otherwise False.

        This function is a support function for compare().

        Ex: contains_wildcards("foo") => FALSE
        Ex: contains_wildcards("foo\?") => FALSE
        Ex: contains_wildcards("foo?") => TRUE
        Ex: contains_wildcards("\*bar") => FALSE
        Ex: contains_wildcards("*bar") => TRUE

        - TEST:
        >>> CPESet2_3.contains_wildcards("foo")
        False

        - TEST:
        >>> CPESet2_3.contains_wildcards("foo\\\?")
        False

        - TEST:
        >>> CPESet2_3.contains_wildcards("foo*")
        True

        - TEST:
        >>> CPESet2_3.contains_wildcards("\\\*bar")
        False

        - TEST:
        >>> CPESet2_3.contains_wildcards("?bar")
        True

        - TEST:
        >>> CPESet2_3.contains_wildcards("8\.\*")
        False
        """

        idx = s.find("*")
        if idx != -1:
            if idx == 0:
                return True
            else:
                if s[idx - 1] != "\\":
                    return True

        idx = s.find("?")
        if idx != -1:
            if idx == 0:
                return True
            else:
                if s[idx - 1] != "\\":
                    return True

        return False

    @classmethod
    def isEvenWildcards(cls, str, idx):
        """
        Returns True if an even number of escape (backslash) characters
        precede the character at index idx in string str.

        - TEST:
        >>> CPESet2_3.isEvenWildcards("lin\ux", 4)
        False

        - TEST:
        >>> CPESet2_3.isEvenWildcards("lin\\ux", 5)
        True
        """

        result = 0
        while ((idx > 0) and (str[idx - 1] == "\\")):
            idx -= 1
            result += 1

        isEvenNumber = (result % 2) == 0

        return isEvenNumber

    ####################
    #  OBJECT METHODS  #
    ####################

    def __init__(self):
        """
        Create an empty set of CPEs.
        """
        self.K = []

    def __len__(self):
        """
        Returns the count of CPE elements of set.

        - TEST: empty set
        >>> s = CPESet2_3()
        >>> len(s)
        0

        - TEST: set with two CPE elements
        >>> wfn1 = 'wfn:[part="a", vendor="hp", product="insight_diagnostics", version="8\.*", sw_edition="?", target_sw=ANY, target_hw="x32"]'
        >>> wfn2 = 'wfn:[part="a", vendor="hp", product="nvidia", version="8\.*", sw_edition="?", target_sw=ANY, target_hw="x32"]'
        >>> c1 = CPE2_3_WFN(wfn1)
        >>> c2 = CPE2_3_WFN(wfn2)
        >>> s = CPESet2_3()
        >>> s.append(c1)
        >>> s.append(c2)
        >>> len(s)
        2

        - TEST: set with three CPE elements and one repeated
        >>> wfn1 = 'wfn:[part="a", vendor="hp", product="insight_diagnostics", version="8\.*", sw_edition="?", target_sw=ANY, target_hw="x32"]'
        >>> wfn1 = 'wfn:[part="a", vendor="hp", product="insight_diagnostics", version="8\.*", sw_edition="?", target_sw=ANY, target_hw="x32"]'
        >>> c1 = CPE2_3_WFN(wfn1)
        >>> c2 = CPE2_3_WFN(wfn2)
        >>> c3 = CPE2_3_WFN(wfn2)
        >>> s = CPESet2_3()
        >>> s.append(c1)
        >>> s.append(c2)
        >>> s.append(c3)
        >>> len(s)
        2
        """

        return len(self.K)

    def __unicode__(self):
        """
        Returns CPE set as string.

        - TEST: empty set
        >>> s = CPESet2_3()
        >>> s.__unicode__()
        'Set contains 0 elements'
        """

        len = self.__len__()

        str = "Set contains %s elements" % len
        if len > 0:
            str += ":\n"

            for i in range(0, len):
                str += "    %s" % self.K[i].__unicode__()

        return str

    def __getitem__(self, i):
        """
        Returns the i'th CPE element of set.
        """

        return self.K[i]

    def append(self, cpe):
        """
        Adds a CPE element to the set if not already.
        Only WFN CPE names are valid.
        """

        if cpe.version != CPE.VERSION_2_3:
            msg = "CPE name version %s not valid, version 2.3 expected" % cpe.version
            raise ValueError(msg)

        if cpe.style != CPE2_3.STYLE_WFN:
            msg = "Only WFN CPE names are valid"
            raise TypeError(msg)

        for k in self.K:
            if cpe.str == k.str:
                return None

        self.K.append(cpe)

    def name_match(self, wfn):
        """
        Accepts a set of CPE Names K and a candidate CPE Name X. It returns
        'True' if X matches any member of K, and 'False' otherwise.

        Inputs:
            - self: A list of m CPE Names K = {K1, K2, …, Km}.
            - cpe: A candidate CPE Name X.
        Output:
            - True if X matches K, False otherwise.

        - TEST: matching (identical cpe in set)
        >>> wfn1 = 'wfn:[part="a", vendor="microsoft", product="internet_explorer", version="8\.0\*", update="beta", edition=ANY]'

        >>> wfn2 = 'wfn:[part="o", vendor="microsoft", product="windows", version="8\.0\*", update="sp2", edition=ANY]'

        >>> c1 = CPE2_3_WFN(wfn1)
        >>> c2 = CPE2_3_WFN(wfn2)
        >>> m = CPE2_3_WFN(wfn2)
        >>> s = CPESet2_3()
        >>> s.append(c1)
        >>> s.append(c2)
        >>> s.name_match(m)
        True

        - test: matching with any values (cpe in set)
        >>> wfn1 = 'wfn:[part="a", vendor="microsoft", product="internet_explorer", version="8\.0\.6", update="beta", edition=ANY]'

        >>> wfn2 = 'wfn:[part="o", vendor="microsoft", product="windows", version="8\.0\*", update="sp2", edition=ANY]'
        >>> wfn3 = 'wfn:[part="a", vendor="microsoft", product="internet_explorer", version="8\.0*"]'
        >>> c1 = CPE2_3_WFN(wfn1)
        >>> c2 = CPE2_3_WFN(wfn2)
        >>> m = CPE2_3_WFN(wfn3)
        >>> s = CPESet2_3()
        >>> s.append(c1)
        >>> s.append(c2)
        >>> s.name_match(m)
        True

        - test: not matching
        >>> wfn1 = 'wfn:[part="a", vendor="microsoft", product="internet_explorer", version="8\.0\*", update="beta", edition=ANY]'

        >>> wfn2 = 'wfn:[part="o", vendor="microsoft", product="windows", version="8\.0*", update="sp2", edition=ANY]'
        >>> wfn3 = 'wfn:[part="h", vendor="hp", product="compact"]'
        >>> c1 = CPE2_3_WFN(wfn1)
        >>> c2 = CPE2_3_WFN(wfn2)
        >>> m = CPE2_3_WFN(wfn3)
        >>> s = CPESet2_3()
        >>> s.append(c1)
        >>> s.append(c2)
        >>> s.name_match(m)
        False
        """

        for N in self.K:
            if CPESet2_3.cpe_superset(wfn, N):
                return True
        return False

if __name__ == "__main__":

    import doctest
    doctest.testmod(optionflags=doctest.IGNORE_EXCEPTION_DETAIL)