# -*- coding: utf-8 -*-
'''
Declarations defining patterns to be asserted upon MARC files to generate linked data
in the form of a Versa output model

BFLITE_TRANSFORMS is an example of a speification designed to be understood
by moderately tech-savvy librarians, and even overridden to specialize the
MARC -> BIBFRAME conversion by the more adventurous.

A few examples of entries to help communicate the nature and power of the pattern
specification language

    '001': oninstance.link(rel=BL+'controlCode'),

The left hand side defines the data to be matched from the MARC input in MARC terms
(tags, values, indicators and subfields). In this case match any 001 tag field.

The right hand side expresses the output in terms of BIBFRAME. For each processed
MARC record pybibframe assumes and materializes (creates)¹ one Work resource output,
and one or more Instance resource output. In this case create an output "link"² from
the materialized instance, using a relationship property IRI of
`http://bibfra.me/vocab/lite/controlCode`. `BL` is the IRI stem to which the term
`controlCode` is concatenated. The link target (a string data item in this case)
is the value of the 001 tag field.

¹The idea of materialization is that it is the process of converting "strings"
from MARC into "things" as Linked Data resources.
²The Versa concept of a link is analogous to the RDF concept of a statement.
The target of a Versa link can be a data item as well as a resource

In the following case

    '010$a': onwork.link(rel=MARC+'lccn'),

what's matched is any MARC 010 tag field which has an `a` subfield.
The generated link originates with the materialized work resource rather than
than the instance. The link relationship IRI is `http://bibfra.me/vocab/marc/lccn`.
The link target value comes form the value of the `a` subfield.

    '100': onwork.materialize(
                BL+'Person', BL+'creator',
                unique=[
                    (BL+'name', subfield('a')),
                    (MARC+'numeration', subfield('b')),
                    (MARC+'titles', subfield('c'))
                ],
                links={
                    BL+'name': subfield('a'),
                    MARC+'numeration': subfield('b'),
                    MARC+'titles': subfield('c'),
                    BL+'date': subfield('d'),
                    BL+'authorityLink': subfield('0')
                }),

In this case a new resource is materialized, of type Person, and related to the
main materialized work. The link from the work to the Person resource has
relationship IRI `http://bibfra.me/vocab/lite/creator`. The ID of the new Person
resource is derived and rendered unique based on the value of the `a`, `b` and `c`
MARC subfields. The new person resource is further characterized with additional
links derived from other subfields. For example a link is created originating on
the person, with a rel IRI of `http://bibfra.me/vocab/lite/name` and a link target
value from the MARC subfield `a` value.

    '100': onwork.materialize(
                BL+'Person', values(BL+'creator',
                relator_property(subfield('e'), prefix=REL),
                relator_property(subfield('4'), prefix=REL)),
                unique=[
                    (BL+'name', subfield('a')),
                    (MARC+'numeration', subfield('b')),
                    (MARC+'titles', subfield('c'))
                ],
                links={
                    BL+'name': subfield('a'),
                    MARC+'numeration': subfield('b'),
                    MARC+'titles': subfield('c'),
                    BL+'date': subfield('d'),
                    BL+'authorityLink': subfield('0')
                }),

In this case, more than one main link is generated from the work to the newly
materialized person. in addition to `http://bibfra.me/vocab/lite/creator` there
are links based on any MARC subfield `e` and `4` values, treated as relators.

    '260': oninstance.materialize(
                BL+'ProviderEvent', MARC+'publication',
                unique=[
                    (BL+'name', subfield('a')),
                    (MARC+'numeration', subfield('b')),
                    (MARC+'titles', subfield('c'))
                ],
                links={
                    ifexists(subfield('a'), BL+'providerPlace'):
                        materialize(BL+'Place', unique=subfield('a'),
                                    links={BL+'name': subfield('a')}),
                    foreach(target=subfield('b')):
                        materialize(BL+'Agent', BL+'providerAgent', unique=target(),
                                    links={BL+'name': target()}),
                    BL+'providerDate': subfield('c')
                },

This case illustrates that any number of resources can be generated from a single
MARC field. When generating links from the new provider event resource,
subfield `a` is checked, and if it exists create a providerPlace link to yet
another materialized resource of type Place which in term has a name from the `a`
subfield and a unique ID derived from the same subfield. Also each subfield `b`
leads to a newly materialized Agent resource. This time the unique ID is derived from
the value of the `b` itself (this is what target() means in that situation, because
it is under the influence of the foreach function).

References.

 * Linked Data URIs and Libraries: The Story So Far <http://www.dlib.org/dlib/may15/papadakis/05papadakis.html>

'''
# Full MARC field list: http://www.loc.gov/marc/bibliographic/ecbdlist.html

# These two lines are required at the top
#from bibframe import BL, BA, REL, MARC, RBMS, AV, POSTPROCESS_AS_INSTANCE
from bibframe import *
from bibframe.reader.util import *

# This line only needed if you are using advanced patterns e.g. with the replace_from function
import re

# from bibframe.reader.marcpatterns import *
# sorted([ (m, MATERIALIZE[m]) for m in MATERIALIZE if [ wf for wf in WORK_FIELDS if m[:2] == wf[:2]] ])

# '100': onwork.materialize('Agent', 'creator', unique=all_subfields, links={'a': 'label'}),

# Stuff such as Leader, 006, 007 & 008 are in marcextra.py

AUTHORITY_CODES = [
    (re.compile(r'\(DLC\)\s*(\S+)'), r'http://lccn.loc.gov/\1'),
    (re.compile(r'\(DLC\)sf\s*(\S+)'), r'http://lccn.loc.gov/sf\1'),
    (re.compile(r'\(DLC\)gm\s*(\S+)'), r'http://lccn.loc.gov/gm\1'),
    (re.compile(r'\(DLC\)n\s*(\S+)'), r'http://lccn.loc.gov/n\1'),
    (re.compile(r'\(DLC\)sh\s*(\S+)'), r'http://lccn.loc.gov/sh\1'),
    (re.compile(r'\(DLC\)sn\s*(\S+)'), r'http://lccn.loc.gov/sn\1'),
    (re.compile(r'\(OCoLC\)fst(\d+)'), r'http://id.worldcat.org/fast/\1'),
    (re.compile(r'\([O0]CoLC\)\s*oc?[nm]?(\d+)'), r'http://www.worldcat.org/oclc/\1'),
    (re.compile(r'\([O0]CoLC\)\s*(\d+)'), r'http://www.worldcat.org/oclc/\1'),
    (re.compile(r'\(viaf\)\s*(\S+)'), r'http://viaf.org/viaf/\1'),
    (re.compile(r'\(DNLM\)\s*(\S+)'), r'http://www.ncbi.nlm.nih.gov/nlmcatalog?term=\1'),
    (re.compile(r'\(DE\-101\)\s*(\S+)'), r'http://d-nb.info/\1'),
    (re.compile(r'\(DE\-588\)\s*(\S+)'), r'http://d-nb.info/gnd/\1'),
    (re.compile(r'\(LoC\)\s*(\S+)'), r'http://id.loc.gov/authorities/names/\1'),
    (re.compile(r'\(CaOONL\)\s*(\S+)'), r'http://www.collectionscanada.gc.ca/lac-bac/results/all?SearchInText_1=\1'),
]

BFLITE_TRANSFORMS = {
    '001': oninstance.link(rel=BL + 'controlCode'),

    #Explicitly ignore 002, just as an example. If we later on come up with a core rule for 002, just pick another key :)
    #To exercise, run:  marc2bf -v -o /dev/null test/resource/zweig-tiny.mrx
    '002': ignore(),

    # Link to the 010a value, naming the relationship 'lccn'
    '010$a': oninstance.link(rel=MARC + 'lccn'),
    '017$a': oninstance.link(rel=MARC + 'legalDeposit'),
    # ISBN is specially processed
    # '020$a': oninstance.link(rel='isbn'),
    '022$a': oninstance.link(rel=MARC + 'issn'),
    '024$a': oninstance.link(rel=MARC + 'otherControlNumber'),
    '024$a-#1': oninstance.link(rel=MARC + 'upc'),
    '025$a': oninstance.link(rel=MARC + 'lcOverseasAcq'),

    '028$a': oninstance.link(rel=MARC + 'publisherNumber'),
    '028$a-#0': oninstance.link(rel=MARC + 'issueNumber'),
    '028$a-#2': oninstance.link(rel=MARC + 'plateNumber'),
    '028$a-#4': oninstance.link(rel=MARC + 'videoRecordingNumber'),

    '034$a': oninstance.link(rel=MARC + 'cartographicMathematicalDataScaleStatement'),
    # Rebecca & Sally suggested this should effectively be a merge with 034a
    '034$b': oninstance.link(rel=MARC + 'cartographicMathematicalDataProjectionStatement'),
    '034$c': oninstance.link(rel=MARC + 'cartographicMathematicalDataCoordinateStatement'),
    '035$a': oninstance.link(rel=MARC + 'systemControlNumber'),
    '037$a': oninstance.link(rel=MARC + 'stockNumber'),

    '040$a': onwork.link(rel=MARC + 'catalogingSource'),

    '041$a': onwork.link(rel=BL + 'language'),
    '041$b': onwork.link(rel=BL + 'language'),
    '041$d': onwork.link(rel=BL + 'language'),
    '041$e': onwork.link(rel=BL + 'language'),
    '041$f': onwork.link(rel=BL + 'language'),
    '041$j': onwork.link(rel=BL + 'language'),
    '041$h': onwork.link(rel=BL + 'language'),

    '050$a': onwork.link(rel=MARC + 'lcCallNumber'),
    '050$b': onwork.link(rel=MARC + 'lcItemNumber'),
    '050$3': onwork.link(rel=BL + 'material'),
    '060$a': onwork.link(rel=MARC + 'nlmCallNumber'),
    '060$b': onwork.link(rel=MARC + 'nlmItemNumber'),
    '061$a': onwork.link(rel=MARC + 'nlmCopyStatement'),
    '070$a': onwork.link(rel=MARC + 'nalCallNumber'),
    '070$b': onwork.link(rel=MARC + 'nalItemNumber'),
    '071$a': onwork.link(rel=MARC + 'nalCopyStatement'),
    '082$a': onwork.link(rel=MARC + 'deweyNumber'),

    # Fields 100,110,111,etc. have a creator + role (if available) relationship to a new Agent object (only created as a new object if all subfields are unique)
    # generate hash values only from the properties specific to Agents

    '100': onwork.materialize(BL + 'Person',
                              values(
                                  BL + 'creator',
                                  relator_property(subfield('e'), prefix=REL),
                                  relator_property(subfield('4'), prefix=REL)
                              ),
                              unique=[
                                  (BL + 'name', subfield('a')),
                                  (MARC + 'numeration', subfield('b')),
                                  (MARC + 'titles', subfield('c')),
                                  (BL + 'date', subfield('d')),
                                  (MARC + 'nameAlternative', subfield('q')),
                              ],
                              # unique=values(subfield('a'),
                              # subfield('b'),
                              # subfield('c'),
                              # subfield('d'),
                              # subfield('g'),
                              # subfield('j'),
                              # subfield('q'),
                              # subfield('u')
                              # ),
                              links={
                                  BL + 'name': subfield('a'),
                                  MARC + 'numeration': subfield('b'),
                                  MARC + 'titles': subfield('c'),
                                  BL + 'date': subfield('d'),
                                  BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))),
                                  BL + 'nameAlternative': subfield('q')
                              }
    ),

    '110': onwork.materialize(BL + 'Organization',
                              values(
                                  BL + 'creator',
                                  relator_property(subfield('e'), prefix=REL),
                                  relator_property(subfield('4'), prefix=REL)
                              ),
                              unique=[
                                  (BL + 'name', subfield('a')),
                                  (MARC + 'subordinateUnit', subfield('b')),
                                  (BL + 'date', subfield('b')),
                              ],
                              # unique=values(subfield('a'),
                              # subfield('b'),
                              # subfield('c'),
                              # subfield('d'),
                              # subfield('g'),
                              # subfield('j'),
                              # subfield('u')),
                              links={
                                  BL + 'name': subfield('a'),
                                  MARC + 'subordinateUnit': subfield('b'),
                                  BL + 'date': subfield('d'),
                                  BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0')))
                              }
    ),

    '111': onwork.materialize(BL + 'Meeting',
                              values(
                                  BL + 'creator',
                                  relator_property(subfield('e'), prefix=REL),
                                  relator_property(subfield('4'), prefix=REL)
                              ),
                              unique=[
                                  (BL + 'name', subfield('a')),
                                  (BL + 'date', subfield('d')),
                                  (MARC + 'additionalName', subfield('q')),
                              ],
                              # unique=values(subfield('a'),
                              # subfield('b'),
                              # subfield('c'),
                              # subfield('d'),
                              # subfield('g'),
                              # subfield('j'),
                              # subfield('q'),
                              # subfield('u')),
                              links={
                                  BL + 'name': subfield('a'),
                                  BL + 'date': subfield('d'),
                                  BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))),
                                  MARC + 'additionalName': subfield('q')
                              }
    ),

    '130': onwork.materialize(BL + 'Collection',
                              values(
                                  BL + 'creator',
                                  relator_property(subfield('e'), prefix=REL),
                                  relator_property(subfield('4'), prefix=REL)
                              ),
                              unique=[
                                  (BL + 'title', subfield('a')),
                                  (MARC + 'legalDate', subfield('d')),
                                  (BL + 'medium', subfield('h')),
                                  (BL + 'language', subfield('l')),
                                  (AV + 'musicMedium', subfield('m')),
                                  (MARC + 'titleNumber', subfield('n')),
                                  (AV + 'arrangedMusic', subfield('o')),
                                  (MARC + 'titlePart', subfield('p')),
                                  (AV + 'musicKey', subfield('r')),
                                  (MARC + 'form', subfield('k')),
                                  (BL + 'date', subfield('f')),
                                  (MARC + 'version', subfield('s')),
                              ],
                              links={
                                  BL + 'title': subfield('a'),
                                  MARC + 'legalDate': subfield('d'),
                                  BL + 'medium': subfield('h'),
                                  BL + 'language': subfield('l'),
                                  AV + 'musicMedium': subfield('m'),
                                  MARC + 'titleNumber': subfield('n'),
                                  AV + 'arrangedMusic': subfield('o'),
                                  MARC + 'titlePart': subfield('p'),
                                  AV + 'musicKey': subfield('r'),
                                  MARC + 'form': subfield('k'),
                                  BL + 'date': subfield('f'),
                                  MARC + 'version': subfield('s')
                              }
    ),


    '210$a': oninstance.link(rel=MARC + 'abbreviatedTitle'),
    '222$a': oninstance.link(rel=MARC + 'keyTitle'),

    '240': onwork.materialize(BL + 'Collection',
                              BL + 'memberOf',
                              unique=[
                                  (BL + 'title', subfield('a')),
                                  (MARC + 'legalDate', subfield('d')),
                                  (BL + 'medium', subfield('h')),
                                  (BL + 'language', subfield('l')),
                                  (AV + 'musicMedium', subfield('m')),
                                  (MARC + 'titleNumber', subfield('n')),
                                  (AV + 'arrangedMusic', subfield('o')),
                                  (MARC + 'titlePart', subfield('p')),
                                  (AV + 'musicKey', subfield('r')),
                                  (MARC + 'form', subfield('k')),
                                  (BL + 'date', subfield('f')),
                                  (MARC + 'version', subfield('s')),
                              ],
                              # unique=values(subfield('a'),
                              # subfield('d'),
                              # subfield('h'),
                              # subfield('l'),
                              # subfield('m'),
                              # subfield('n'),
                              # subfield('o'),
                              # subfield('p'),
                              # subfield('r'),
                              # subfield('k'),
                              # subfield('f'),
                              # subfield('s')
                              # ),
                              links={
                                  BL + 'title': subfield('a'),
                                  MARC + 'legalDate': subfield('d'),
                                  BL + 'medium': subfield('h'),
                                  BL + 'language': subfield('l'),
                                  AV + 'musicMedium': subfield('m'),
                                  MARC + 'titleNumber': subfield('n'),
                                  AV + 'arrangedMusic': subfield('o'),
                                  MARC + 'titlePart': subfield('p'),
                                  AV + 'musicKey': subfield('r'),
                                  MARC + 'form': subfield('k'),
                                  BL + 'date': subfield('f'),
                                  MARC + 'version': subfield('s')
                              }
    ),

    '243': onwork.materialize(BL + 'Collection',
                              BL + 'memberOf',
                              unique=[
                                  (BL + 'title', subfield('a')),
                                  (MARC + 'legalDate', subfield('d')),
                                  (BL + 'medium', subfield('h')),
                                  (BL + 'language', subfield('l')),
                                  (AV + 'musicMedium', subfield('m')),
                                  (MARC + 'titleNumber', subfield('n')),
                                  (AV + 'arrangedMusic', subfield('o')),
                                  (MARC + 'titlePart', subfield('p')),
                                  (AV + 'musicKey', subfield('r')),
                                  (MARC + 'form', subfield('k')),
                                  (BL + 'date', subfield('f')),
                                  (MARC + 'version', subfield('s')),
                              ],
                              # unique=values(subfield('a'),
                              # subfield('d'),
                              # subfield('h'),
                              # subfield('l'),
                              # subfield('m'),
                              # subfield('n'),
                              # subfield('o'),
                              # subfield('p'),
                              # subfield('r'),
                              # subfield('k'),
                              # subfield('f'),
                              # subfield('s')
                              # ),
                              links={
                                  BL + 'title': subfield('a'),
                                  MARC + 'legalDate': subfield('d'),
                                  BL + 'medium': subfield('h'),
                                  BL + 'language': subfield('l'),
                                  AV + 'musicMedium': subfield('m'),
                                  MARC + 'titleNumber': subfield('n'),
                                  AV + 'arrangedMusic': subfield('o'),
                                  MARC + 'titlePart': subfield('p'),
                                  AV + 'musicKey': subfield('r'),
                                  MARC + 'form': subfield('k'),
                                  BL + 'date': subfield('f'),
                                  MARC + 'version': subfield('s')
                              }
    ),

    # Title(s) - replicate across both Work and Instance(s)

    '245$a': (onwork.link(rel=BL + 'title'), oninstance.link(rel=BL + 'title')),
    '245$b': (onwork.link(rel=MARC + 'titleRemainder'), oninstance.link(rel=MARC + 'titleRemainder')),
    '245$c': (onwork.link(rel=MARC + 'titleStatement'), oninstance.link(rel=MARC + 'titleStatement')),
    '245$n': (onwork.link(rel=MARC + 'titleNumber'), oninstance.link(rel=MARC + 'titleNumber')),
    '245$p': (onwork.link(rel=MARC + 'titlePart'), oninstance.link(rel=MARC + 'titlePart')),

    '245$f': onwork.link(rel=MARC + 'inclusiveDates'),
    '245$h': oninstance.link(rel=BL + 'medium'),
    '245$k': onwork.link(rel=MARC + 'formDesignation'),
    '246$a': onwork.link(rel=MARC + 'titleVariation'),
    '246$b': onwork.link(rel=MARC + 'titleVariationRemainder'),
    '246$f': onwork.link(rel=MARC + 'titleVariationDate'),
    '247$a': onwork.link(rel=MARC + 'formerTitle'),
    '250$a': oninstance.link(rel=MARC + 'edition'),
    '250$b': oninstance.link(rel=MARC + 'edition'),
    '254$a': oninstance.link(rel=MARC + 'musicalPresentation'),
    '255$a': oninstance.link(rel=MARC + 'cartographicMathematicalDataScaleStatement'),
    '255$b': oninstance.link(rel=MARC + 'cartographicMathematicalDataProjectionStatement'),
    '255$c': oninstance.link(rel=MARC + 'cartographicMathematicalDataCoordinateStatement'),
    '256$a': oninstance.link(rel=MARC + 'computerFilecharacteristics'),

    # Provider materialization

    '260': oninstance.materialize(BL + 'ProviderEvent',
                                  MARC + 'publication',
                                  unique=all_subfields,
                                  links={ifexists(subfield('a'), BL + 'providerPlace'):
                                             materialize(BL + 'Place',
                                                         unique=[
                                                             (BL + 'name', subfield('a'))
                                                         ],
                                                         # unique=subfield('a'),
                                                         links={
                                                             BL + 'name': subfield('a')
                                                         }
                                             ),
                                         ifexists(subfield('e'), BL + 'providerPlace'):
                                             materialize(BL + 'Place',
                                                         unique=[
                                                             (BL + 'name', subfield('e'))
                                                         ],
                                                         # unique=subfield('a'),
                                                         links={
                                                             BL + 'name': subfield('e')
                                                         }
                                             ),
                                         foreach(target=subfield('b')):
                                             materialize(BL + 'Agent',
                                                         values(
                                                             BL + 'providerAgent'
                                                         ),
                                                         unique=[
                                                             (BL + 'name', target())
                                                         ],
                                                         # unique=target(),
                                                         links={
                                                             BL + 'name': target()
                                                         }
                                             ),
                                         foreach(target=subfield('f')):
                                             materialize(BL + 'Agent',
                                                         values(
                                                             BL + 'providerAgent'
                                                         ),
                                                         unique=[
                                                             (BL + 'name', target())
                                                         ],
                                                         # unique=target(),
                                                         links={
                                                             BL + 'name': target()
                                                         }
                                             ),
                                         BL + 'providerDate': values(subfield('c'), subfield('d'))
                                  }
    ),

    '264-#4': oninstance.materialize(BL + 'CopyrightEvent',
                                     BL + 'copyright',
                                     unique=all_subfields,
                                     links={ifexists(subfield('a'), BL + 'copyrightPlace'):
                                                materialize(BL + 'Place',
                                                            unique=[(BL + 'name', subfield('a'))],
                                                            # unique=subfield('a'),
                                                            links={BL + 'name': subfield('a')}
                                                ),
                                            ifexists(subfield('b'), BL + 'copyrightAgent'):
                                                materialize(BL + 'Agent',
                                                            unique=[(BL + 'name', subfield('b'))],
                                                            # unique=subfield('b'),
                                                            links={BL + 'name': subfield('b')}
                                                ),
                                            BL + 'copyrightDate': subfield('c')}
    ),

    '264-#3': oninstance.materialize(BL + 'ProviderEvent',
                                     MARC + 'manufacture',
                                     unique=all_subfields,
                                     links={ifexists(subfield('a'), BL + 'providerPlace'):
                                                materialize(BL + 'Place',
                                                            unique=[
                                                                (BL + 'name', subfield('a'))
                                                            ],
                                                            # unique=subfield('a'),
                                                            links={
                                                                BL + 'name': subfield('a')
                                                            }
                                                ),
                                            ifexists(subfield('b'), BL + 'providerAgent'):
                                                materialize(BL + 'Agent',
                                                            unique=[
                                                                (BL + 'name', subfield('b'))
                                                            ],
                                                            # unique=subfield('b'),
                                                            links={
                                                                BL + 'name': subfield('b')
                                                            }
                                                ),
                                            BL + 'providerDate': subfield('c')}
    ),

    '264-#2': oninstance.materialize(BL + 'ProviderEvent',
                                     MARC + 'distribution',
                                     unique=all_subfields,
                                     links={ifexists(subfield('a'), BL + 'providerPlace'):
                                                materialize(BL + 'Place',
                                                            unique=[
                                                                (BL + 'name', subfield('a'))
                                                            ],
                                                            # unique=subfield('a'),
                                                            links={
                                                                BL + 'name': subfield('a')
                                                            }
                                                ),
                                            ifexists(subfield('b'), BL + 'providerAgent'):
                                                materialize(BL + 'Agent',
                                                            unique=[
                                                                (BL + 'name', subfield('b'))
                                                            ],
                                                            # unique=subfield('b'),
                                                            links={
                                                                BL + 'name': subfield('b')
                                                            }
                                                ),
                                            BL + 'providerDate': subfield('c')}
    ),

    '264-#1': oninstance.materialize(BL + 'ProviderEvent',
                                     MARC + 'publication',
                                     unique=all_subfields,
                                     links={ifexists(subfield('a'), BL + 'providerPlace'):
                                                materialize(BL + 'Place',
                                                            unique=[
                                                                (BL + 'name', subfield('a'))
                                                            ],
                                                            # unique=subfield('a'),
                                                            links={
                                                                BL + 'name': subfield('a')
                                                            }
                                                ),
                                            ifexists(subfield('b'), 'providerAgent'):
                                                materialize(BL + 'Agent',
                                                            unique=[
                                                                (BL + 'name', subfield('b'))
                                                            ],
                                                            # unique=subfield('b'),
                                                            links={
                                                                BL + 'name': subfield('b')
                                                            }
                                                ),
                                            BL + 'providerDate': subfield('c')}
    ),

    '264-#0': oninstance.materialize(BL + 'ProviderEvent',
                                     MARC + 'production',
                                     unique=all_subfields,
                                     links={ifexists(subfield('a'), BL + 'providerPlace'):
                                                materialize(BL + 'Place',
                                                            unique=[
                                                                (BL + 'name', subfield('a'))
                                                            ],
                                                            # unique=subfield('a'),
                                                            links={
                                                                BL + 'name': subfield('a')
                                                            }
                                                ),
                                            ifexists(subfield('b'), BL + 'providerAgent'):
                                                materialize(BL + 'Agent',
                                                            unique=[
                                                                (BL + 'name', subfield('b'))
                                                            ],
                                                            # unique=subfield('b'),
                                                            links={
                                                                BL + 'name': subfield('b')
                                                            }
                                                ),
                                            BL + 'providerDate': subfield('c')}
    ),

    # assume if indicators are blank its a publication

    '264-##': oninstance.materialize(BL + 'ProviderEvent',
                                     MARC + 'publication',
                                     unique=all_subfields,
                                     links={ifexists(subfield('a'), BL + 'providerPlace'):
                                                materialize(BL + 'Place',
                                                            unique=[
                                                                (BL + 'name', subfield('a'))
                                                            ],
                                                            # unique=subfield('a'),
                                                            links={
                                                                BL + 'name': subfield('a')
                                                            }
                                                ),
                                            ifexists(subfield('b'), 'providerAgent'):
                                                materialize(BL + 'Agent',
                                                            unique=[
                                                                (BL + 'name', subfield('b'))
                                                            ],
                                                            # unique=subfield('b'),
                                                            links={
                                                                BL + 'name': subfield('b')
                                                            }
                                                ),
                                            BL + 'providerDate': subfield('c')}
    ),

    '300$a': oninstance.link(rel=BL + 'extent'),
    '300$b': oninstance.link(rel=MARC + 'otherPhysicalDetails'),
    '300$c': oninstance.link(rel=BL + 'dimensions'),
    '300$e': oninstance.link(rel=MARC + 'accompanyingMaterial'),
    '300$f': oninstance.link(rel=MARC + 'typeOfunit'),
    '300$g': oninstance.link(rel=MARC + 'size'),
    '300$3': oninstance.link(rel=MARC + 'materials'),
    '310$a': oninstance.link(rel=MARC + 'publicationFrequency'),
    '310$b': oninstance.link(rel=MARC + 'publicationDateFrequency'),
    '336$a': oninstance.link(rel=MARC + 'contentCategory'),
    '336$b': oninstance.link(rel=MARC + 'contentTypeCode'),
    '336$2': oninstance.link(rel=MARC + 'contentTypeMARCsource'),
    '337$a': oninstance.link(rel=MARC + 'mediaCategory'),
    '337$b': oninstance.link(rel=MARC + 'mediaTypeCode'),
    '337$2': oninstance.link(rel=MARC + 'mediaMARCsource'),
    '338$a': oninstance.link(rel=MARC + 'carrierCategory'),
    '338$b': oninstance.link(rel=MARC + 'carrierCategoryCode'),
    '338$2': oninstance.link(rel=MARC + 'carrierMARCSource'),
    '340$a': oninstance.link(rel=MARC + 'physicalSubstance'),
    '340$b': oninstance.link(rel=MARC + 'dimensions'),
    '340$c': oninstance.link(rel=MARC + 'materialsApplied'),
    '340$d': oninstance.link(rel=MARC + 'recordingTechnique'),
    '340$e': oninstance.link(rel=MARC + 'physicalSupport'),
    '351$a': oninstance.link(rel=MARC + 'organizationMethod'),
    '351$b': oninstance.link(rel=MARC + 'arrangement'),
    '351$c': oninstance.link(rel=MARC + 'hierarchy'),
    '351$3': oninstance.link(rel=MARC + 'materialsSpec'),

    '362$a': oninstance.link(rel=MARC + 'publicationDesignation'),


    '382$a': onwork.link(rel=AV + 'performanceMedium'),
    '382$b': onwork.link(rel=AV + 'featuredMedium'),
    '382$p': onwork.link(rel=AV + 'alternativeMedium'),

    '382$s': onwork.link(rel=AV + 'numberOfPerformers'),
    '382$v': onwork.link(rel=AV + 'mediumNote'),

    '490$a': onwork.link(rel=MARC + 'seriesStatement'),
    '490$v': onwork.link(rel=MARC + 'seriesVolume'),

    '500$a': oninstance.link(rel=BL + 'note'),
    '501$a': oninstance.link(rel=BL + 'note'),
    '502$a': onwork.link(rel=MARC + 'dissertationNote'),
    '502$b': onwork.link(rel=MARC + 'degree'),
    '502$c': onwork.link(rel=MARC + 'grantingInstitution'),
    '502$d': onwork.link(rel=MARC + 'dissertationYear'),
    '502$g': onwork.link(rel=MARC + 'dissertationNote'),
    '502$o': onwork.link(rel=MARC + 'dissertationID'),
    '504$a': oninstance.link(rel=MARC + 'bibliographyNote'),

    # Formatted Contents Note
    '505$a': oninstance.link(rel=MARC + 'contentsNote'),
    '505$t': oninstance.link(rel=MARC + 'contentsNote'),
    '505$r': oninstance.link(rel=MARC + 'contentsNote'),
    '505$g': oninstance.link(rel=MARC + 'contentsNote'),

    # '505$a-0#': oninstance.link(rel=MARC+'contentsNote'),
    # '505$a-1#': oninstance.link(rel=MARC+'contentsNote'),  # incompleteContentsNote
    # '505$a-2#': oninstance.link(rel=MARC+'contentsNote'),  # partialContentsNote
    # '505$t-00': oninstance.link(rel=MARC+'contentsNote'),  # contentsTitle
    # '505$r-00': oninstance.link(rel=MARC+'contentsNote'),  # contentsStatementOfResponsibility
    # '505$g-00': oninstance.link(rel=MARC+'contentsNote'),  # contentsMisc

    '506$a': oninstance.link(rel=MARC + 'governingAccessNote'),
    '506$b': oninstance.link(rel=MARC + 'jurisdictionNote'),
    '506$c': oninstance.link(rel=MARC + 'physicalAccess'),
    '506$d': oninstance.link(rel=MARC + 'authorizedUsers'),
    '506$e': oninstance.link(rel=MARC + 'authorization'),
    '506$u': oninstance.link(rel=MARC + 'uriNote'),
    '507$a': oninstance.link(rel=MARC + 'representativeFractionOfScale'),
    '507$b': oninstance.link(rel=MARC + 'remainderOfScale'),
    '508$a': onwork.link(rel=MARC + 'creditsNote'),
    '510$a': onwork.link(rel=MARC + 'citationSource'),
    '510$b': onwork.link(rel=MARC + 'citationCoverage'),
    '510$c': onwork.link(rel=MARC + 'citationLocationWithinSource'),
    '510$u': onwork.link(rel=MARC + 'citationUri'),
    '511$a': onwork.link(rel=MARC + 'performerNote'),
    '513$a': onwork.link(rel=MARC + 'typeOfReport'),
    '513$b': onwork.link(rel=MARC + 'periodCovered'),
    '514$a': oninstance.link(rel=MARC + 'dataQuality'),
    '515$a': oninstance.link(rel=MARC + 'numberingPerculiarities'),
    '516$a': oninstance.link(rel=MARC + 'typeOfComputerFile'),
    '518$a': onwork.link(rel=MARC + 'dateTimePlace'),
    '518$d': onwork.link(rel=MARC + 'dateOfEvent'),
    '518$o': onwork.link(rel=MARC + 'otherEventInformation'),
    '518$p': onwork.link(rel=MARC + 'placeOfEvent'),
    '520$a': onwork.link(rel=MARC + 'summary'),
    '520$b': onwork.link(rel=MARC + 'summaryExpansion'),
    '520$c': onwork.link(rel=MARC + 'assigningSource'),
    '520$u': onwork.link(rel=MARC + 'summaryURI'),
    '521$a': onwork.link(rel=MARC + 'intendedAudience'),
    '521$b': onwork.link(rel=MARC + 'intendedAudienceSource'),
    '522$a': onwork.link(rel=MARC + 'geographicCoverage'),
    '526$a': onwork.link(rel=MARC + 'studyProgramName'),
    '526$b': onwork.link(rel=MARC + 'interestLevel'),
    '526$c': onwork.link(rel=MARC + 'readingLevel'),
    '530$a': onwork.link(rel=MARC + 'additionalPhysicalForm'),
    '533$a': oninstance.link(rel=MARC + 'reproductionNote'),
    '534$a': oninstance.link(rel=MARC + 'originalVersionNote'),
    '535$a': onwork.link(rel=MARC + 'locationOfOriginalsDuplicates'),
    '536$a': onwork.link(rel=MARC + 'fundingInformation'),
    '538$a': oninstance.link(rel=MARC + 'systemDetails'),
    '540$a': oninstance.link(rel=MARC + 'termsGoverningUse'),
    '541$a': oninstance.link(rel=MARC + 'immediateSourceOfAcquisition'),
    '542$a': onwork.link(rel=MARC + 'informationRelatingToCopyrightStatus'),
    '544$a': onwork.link(rel=MARC + 'locationOfOtherArchivalMaterial'),
    '545$a': onwork.link(rel=MARC + 'biographicalOrHistoricalData'),
    '546$a': onwork.link(rel=MARC + 'languageNote'),
    '547$a': onwork.link(rel=MARC + 'formerTitleComplexity'),
    '550$a': oninstance.link(rel=MARC + 'issuingBody'),
    '552$a': onwork.link(rel=MARC + 'entityAndAttributeInformation'),
    '555$a': oninstance.link(rel=MARC + 'cumulativeIndexFindingAids'),
    '556$a': onwork.link(rel=MARC + 'informationAboutDocumentation'),
    '561$a': oninstance.link(rel=MARC + 'ownership'),
    '580$a': onwork.link(rel=BL + 'note'),
    '583$a': onwork.link(rel=MARC + 'action'),
    '586$a': onwork.link(rel=MARC + 'awardsNote'),


    # subjects - the about-ness of a Work
    # subjects are modeled as topics with a focus specific to the MARC tag (person, place, organization, etc.
    # subjects of tags specific to agents with a $t designation are modeled with focuses to Works

    '600': ifexists(subfield('t'),
                    onwork.materialize(BL + 'Concept',
                                       values(
                                           BL + 'subject',
                                           relator_property(subfield('e'), prefix=REL),
                                       ),
                                       unique=[
                                           (BL + 'name', subfield('a')),
                                           (MARC + 'numeration', subfield('b')),
                                           (MARC + 'locationOfEvent', subfield('c')),
                                           (BL + 'date', subfield('d')),
                                           (BL + 'title', subfield('t')),
                                           (MARC + 'formSubdivision', subfield('v')),
                                           (MARC + 'generalSubdivision', subfield('x')),
                                           (MARC + 'chronologicalSubdivision', subfield('y')),
                                           (MARC + 'geographicSubdivision', subfield('z')),
                                       ],
                                       links={
                                           BL + 'name': subfield('a'),
                                           MARC + 'numeration': subfield('b'),
                                           MARC + 'locationOfEvent': subfield('c'),
                                           BL + 'date': subfield('d'),
                                           MARC + 'generalSubdivision': subfield('x'),
                                           MARC + 'chronologicalSubdivision': subfield('y'),
                                           MARC + 'formSubdivision': subfield('v'),
                                           MARC + 'geographicSubdivision': subfield('z'),
                                           BL + 'title': subfield('t'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))),
                                           ifexists(subfield('t'), BL + 'focus'):
                                               materialize(BL + 'Work',
                                                           unique=[
                                                               (BL + 'title', subfield('t')),
                                                               (MARC + 'titleNumber', subfield('n')),
                                                               (AV + 'arrangedMusic', subfield('o')),
                                                               (MARC + 'titlePart', subfield('p')),
                                                               (AV + 'musicKey', subfield('r')),
                                                               (MARC + 'form', subfield('k')),
                                                               (BL + 'date', subfield('f')),
                                                               (MARC + 'version', subfield('s')),
                                                           ],
                                                           links={
                                                               BL + 'title': subfield('t'),
                                                               MARC + 'titleNumber': subfield('n'),
                                                               AV + 'arrangedMusic': subfield('o'),
                                                               MARC + 'titlePart': subfield('p'),
                                                               AV + 'musicKey': subfield('r'),
                                                               MARC + 'form': subfield('k'),
                                                               BL + 'date': subfield('f'),
                                                               MARC + 'version': subfield('s'),
                                                               ifexists(subfield('a'), BL + 'creator'):
                                                                   materialize(BL + 'Person',
                                                                               unique=[
                                                                                   (BL + 'name', subfield('a')),
                                                                                   (MARC + 'numeration', subfield('b')),
                                                                                   (MARC + 'titles', subfield('c')),
                                                                                   (BL + 'date', subfield('d')),
                                                                                   (MARC + 'additionalName',
                                                                                    subfield('q')),
                                                                               ],
                                                                               links={
                                                                                   BL + 'name': subfield('a'),
                                                                                   MARC + 'numeration': subfield('b'),
                                                                                   MARC + 'titles': subfield('c'),
                                                                                   BL + 'date': subfield('d'),
                                                                                   MARC + 'additionalName': subfield(
                                                                                       'q')
                                                                               }
                                                                   )
                                                           }
                                               )
                                       }
                    ),
                    onwork.materialize(BL + 'Concept',
                                       values(
                                           BL + 'subject',
                                           relator_property(subfield('e'), prefix=REL),
                                       ),
                                       unique=[
                                           (BL + 'name', subfield('a')),
                                           (MARC + 'numeration', subfield('b')),
                                           (MARC + 'locationOfEvent', subfield('c')),
                                           (BL + 'date', subfield('d')),
                                           (BL + 'title', subfield('t')),
                                           (MARC + 'formSubdivision', subfield('v')),
                                           (MARC + 'generalSubdivision', subfield('x')),
                                           (MARC + 'chronologicalSubdivision', subfield('y')),
                                           (MARC + 'geographicSubdivision', subfield('z')),
                                       ],
                                       links={BL + 'name': subfield('a'),
                                              MARC + 'numeration': subfield('b'),
                                              MARC + 'locationOfEvent': subfield('c'),
                                              BL + 'date': subfield('d'),
                                              MARC + 'generalSubdivision': subfield('x'),
                                              MARC + 'chronologicalSubdivision': subfield('y'),
                                              MARC + 'formSubdivision': subfield('v'),
                                              MARC + 'geographicSubdivision': subfield('z'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))),
                                              ifexists(subfield('a'), BL + 'focus'):
                                                  materialize(BL + 'Person',  # same as 100
                                                              unique=[
                                                                  (BL + 'name', subfield('a')),
                                                                  (MARC + 'numeration', subfield('b')),
                                                                  (MARC + 'titles', subfield('c')),
                                                                  (BL + 'date', subfield('d')),
                                                                  (MARC + 'additionalName', subfield('q')),
                                                              ],
                                                              # unique=values(subfield('a'), subfield('b'), subfield('c'),
                                                              # subfield('d'), subfield('g'), subfield('j'),
                                                              # subfield('q'), subfield('u')
                                                              # ),
                                                              links={BL + 'name': subfield('a'),
                                                                     MARC + 'numeration': subfield('b'),
                                                                     MARC + 'titles': subfield('c'),
                                                                     BL + 'date': subfield('d'),
                                                                     MARC + 'additionalName': subfield('q')
                                                              }
                                                  )
                                       }
                    )
    ),

    '610': onwork.materialize(BL + 'Concept',
                              values(
                                  BL + 'subject',
                                  relator_property(subfield('e'), prefix=REL),
                              ),
                              unique=[
                                  (BL + 'name', subfield('a')),
                                  (MARC + 'subordinateUnit', subfield('b')),
                                  (MARC + 'locationOfEvent', subfield('c')),
                                  (BL + 'date', subfield('d')),
                                  (BL + 'title', subfield('t')),
                                  (MARC + 'formSubdivision', subfield('v')),
                                  (MARC + 'generalSubdivision', subfield('x')),
                                  (MARC + 'chronologicalSubdivision', subfield('y')),
                                  (MARC + 'geographicSubdivision', subfield('z')),
                              ],
                              # unique=values(subfield('a'), subfield('b'), subfield('c'),
                              # subfield('d'), subfield('f'), subfield('g'),
                              # subfield('h'), subfield('k'), subfield('l'),
                              # subfield('m'), subfield('n'), subfield('o'),
                              # subfield('p'), subfield('r'), subfield('s'),
                              # subfield('t'), subfield('u'), subfield('v'),
                              # subfield('x'), subfield('y'), subfield('z')),
                              links={BL + 'name': subfield('a'),
                                     MARC + 'subordinateUnit': subfield('b'),
                                     MARC + 'locationOfEvent': subfield('c'),
                                     BL + 'date': subfield('d'),
                                     MARC + 'generalSubdivision': subfield('x'),
                                     MARC + 'chronologicalSubdivision': subfield('y'),
                                     MARC + 'formSubdivision': subfield('v'),
                                     MARC + 'geographicSubdivision': subfield('z'),
                                     BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))),
                                     ifexists(subfield('a'), BL + 'focus'):
                                         materialize(BL + 'Organization',
                                                     unique=[
                                                         (BL + 'name', subfield('a')),
                                                         (MARC + 'subordinateUnit', subfield('b')),
                                                         (BL + 'date', subfield('d')),
                                                         (MARC + 'additionalName', subfield('q')),
                                                     ],
                                                     # unique=values(subfield('a'),  # same as 110
                                                     # subfield('b'),
                                                     # subfield('c'),
                                                     # subfield('d'),
                                                     # subfield('g'),
                                                     # subfield('j'),
                                                     # subfield('q'),
                                                     # subfield('u')),
                                                     links={BL + 'name': subfield('a'),
                                                            MARC + 'subordinateUnit': subfield('b'),
                                                            BL + 'date': subfield('d'),
                                                            MARC + 'additionalName': subfield('q')
                                                     }
                                         )
                              }
    ),

    '611': onwork.materialize(BL + 'Concept',
                              values(
                                  BL + 'subject',
                                  relator_property(subfield('e'), prefix=REL),
                              ),
                              unique=[
                                  (BL + 'name', subfield('a')),
                                  (MARC + 'numeration', subfield('b')),
                                  (MARC + 'locationOfEvent', subfield('c')),
                                  (BL + 'date', subfield('d')),
                                  (BL + 'title', subfield('t')),
                                  (MARC + 'formSubdivision', subfield('v')),
                                  (MARC + 'generalSubdivision', subfield('x')),
                                  (MARC + 'chronologicalSubdivision', subfield('y')),
                                  (MARC + 'geographicSubdivision', subfield('z')),
                              ],
                              # unique=values(subfield('a'), subfield('c'), subfield('d'),
                              # subfield('e'), subfield('f'), subfield('g'),
                              # subfield('h'), subfield('k'), subfield('l'),
                              # subfield('n'), subfield('p'), subfield('q'), subfield('s'),
                              # subfield('t'), subfield('u'), subfield('v'),
                              # subfield('x'), subfield('y'), subfield('z')),
                              links={BL + 'name': subfield('a'),
                                     MARC + 'locationOfEvent': subfield('c'),
                                     BL + 'date': subfield('d'),
                                     MARC + 'generalSubdivision': subfield('x'),
                                     MARC + 'chronologicalSubdivision': subfield('y'),
                                     MARC + 'formSubdivision': subfield('v'),
                                     MARC + 'geographicSubdivision': subfield('z'),
                                     BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))),
                                     ifexists(subfield('a'), BL + 'focus'):
                                         materialize(BL + 'Meeting',
                                                     unique=[
                                                         (BL + 'name', subfield('a')),
                                                         (BL + 'date', subfield('d')),
                                                         (MARC + 'additionalName', subfield('q')),
                                                     ],
                                                     # unique=values(subfield('a'),  # same as 111
                                                     # subfield('b'),
                                                     # subfield('c'),
                                                     # subfield('d'),
                                                     # subfield('g'),
                                                     # subfield('j'),
                                                     # subfield('q'),
                                                     # subfield('u')),
                                                     links={BL + 'name': subfield('a'),
                                                            BL + 'date': subfield('d'),
                                                            MARC + 'additionalName': subfield('q')
                                                     }
                                         )
                              }
    ),


    '630': onwork.materialize(BL + 'Concept',
                              values(
                                  BL + 'subject',
                                  relator_property(subfield('e'), prefix=REL),
                              ),
                              unique=[
                                  (BL + 'title', subfield('a')),
                                  (MARC + 'legalDate', subfield('d')),
                                  (BL + 'medium', subfield('h')),
                                  (BL + 'language', subfield('l')),
                                  (MARC + 'nameOfPart', subfield('p')),
                                  (MARC + 'formSubdivision', subfield('v')),
                                  (MARC + 'generalSubdivision', subfield('x')),
                                  (MARC + 'chronologicalSubdivision', subfield('y')),
                                  (MARC + 'geographicSubdivision', subfield('z')),
                              ],
                              links={BL + 'title': subfield('a'),
                                     MARC + 'legalDate': subfield('d'),
                                     BL + 'language': subfield('l'),
                                     BL + 'medium': subfield('h'),
                                     MARC + 'nameOfPart': subfield('p'),
                                     MARC + 'generalSubdivision': subfield('x'),
                                     MARC + 'chronologicalSubdivision': subfield('y'),
                                     MARC + 'formSubdivision': subfield('v'),
                                     MARC + 'geographicSubdivision': subfield('z'),
                                     BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))),
                                     ifexists(subfield('a'), BL + 'focus'):
                                         materialize(BL + 'Collection',
                                                     unique=[
                                                         (BL + 'title', subfield('a')),
                                                         (MARC + 'legalDate', subfield('d')),
                                                         (BL + 'medium', subfield('h')),
                                                         (BL + 'language', subfield('l')),
                                                         (AV + 'musicMedium', subfield('m')),
                                                         (MARC + 'titleNumber', subfield('n')),
                                                         (AV + 'arrangedMusic', subfield('o')),
                                                         (MARC + 'titlePart', subfield('p')),
                                                         (AV + 'musicKey', subfield('r')),
                                                         (MARC + 'form', subfield('k')),
                                                         (BL + 'date', subfield('f')),
                                                         (MARC + 'version', subfield('s')),
                                                     ],
                                                     links={
                                                         BL + 'title': subfield('a'),
                                                         MARC + 'legalDate': subfield('d'),
                                                         BL + 'date': subfield('f'),
                                                         BL + 'medium': subfield('h'),
                                                         MARC + 'form': subfield('k'),
                                                         BL + 'language': subfield('l'),
                                                         AV + 'musicMedium': subfield('m'),
                                                         MARC + 'titleNumber': subfield('n'),
                                                         AV + 'arrangedMusic': subfield('o'),
                                                         MARC + 'titlePart': subfield('p'),
                                                         AV + 'musicKey': subfield('r'),
                                                         MARC + 'version': subfield('s')
                                                     }
                                         )
                              }
    ),

    '650': onwork.materialize(BL + 'Concept',
                              values(
                                  BL + 'subject',
                                  relator_property(subfield('e'), prefix=REL),
                              ),
                              unique=[
                                  (BL + 'name', subfield('a')),
                                  (MARC + 'locationOfEvent', subfield('c')),
                                  (BL + 'date', subfield('d')),
                                  (MARC + 'formSubdivision', subfield('v')),
                                  (MARC + 'generalSubdivision', subfield('x')),
                                  (MARC + 'chronologicalSubdivision', subfield('y')),
                                  (MARC + 'geographicSubdivision', subfield('z')),
                              ],
                              links={
                                  BL + 'name': subfield('a'),
                                  MARC + 'locationOfEvent': subfield('c'),
                                  BL + 'date': subfield('d'),
                                  MARC + 'generalSubdivision': subfield('x'),
                                  MARC + 'chronologicalSubdivision': subfield('y'),
                                  MARC + 'formSubdivision': subfield('v'),
                                  MARC + 'geographicSubdivision': subfield('z'),
                                  BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))),
                                  ifexists(subfield('a'), BL + 'focus'):
                                      materialize(BL + 'Topic',
                                                  unique=[(BL + 'name', subfield('a'))],
                                                  # unique=values(subfield('a')),
                                                  links={
                                                      BL + 'name': subfield('a'),
                                                      MARC + 'additionalName': subfield('b'),
                                                      MARC + 'miscInfo': subfield('g')}
                                      )
                              }
    ),

    '651': onwork.materialize(BL + 'Concept',
                              values(
                                  BL + 'subject',
                                  relator_property(subfield('e'), prefix=REL),
                              ),
                              unique=[
                                  (BL + 'name', subfield('a')),
                                  (BL + 'date', subfield('d')),
                                  (MARC + 'formSubdivision', subfield('v')),
                                  (MARC + 'generalSubdivision', subfield('x')),
                                  (MARC + 'chronologicalSubdivision', subfield('y')),
                                  (MARC + 'geographicSubdivision', subfield('z')),
                              ],
                              links={
                                  BL + 'name': subfield('a'),
                                  BL + 'date': subfield('d'),
                                  MARC + 'generalSubdivision': subfield('x'),
                                  MARC + 'chronologicalSubdivision': subfield('y'),
                                  MARC + 'formSubdivision': subfield('v'),
                                  MARC + 'geographicSubdivision': subfield('z'),
                                  BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))),
                                  ifexists(subfield('a'), BL + 'focus'):
                                      materialize(BL + 'Place',
                                                  unique=[
                                                      (BL + 'name', subfield('a'))
                                                  ],
                                                  # unique=values(subfield('a')),
                                                  links={
                                                      BL + 'name': subfield('a'),
                                                      MARC + 'miscInfo': subfield('g')
                                                  }
                                      )
                              }
    ),

    '655': onwork.materialize(BL + 'Concept',
                              values(
                                  BL + 'subject',
                                  relator_property(subfield('e'), prefix=REL),
                              ),
                              unique=[
                                  (BL + 'name', subfield('a')),
                                  (BL + 'title', subfield('t')),
                                  (MARC + 'formSubdivision', subfield('v')),
                                  (MARC + 'generalSubdivision', subfield('x')),
                                  (MARC + 'chronologicalSubdivision', subfield('y')),
                                  (MARC + 'geographicSubdivision', subfield('z')),
                              ],
                              links={
                                  BL + 'name': subfield('a'),
                                  MARC + 'source': subfield('2'),
                                  MARC + 'generalSubdivision': subfield('x'),
                                  MARC + 'chronologicalSubdivision': subfield('y'),
                                  MARC + 'formSubdivision': subfield('v'),
                                  MARC + 'geographicSubdivision': subfield('z'),
                                  BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))),
                                  ifexists(subfield('a'), BL + 'focus'):
                                      materialize(BL + 'Form',
                                                  unique=[
                                                      (BL + 'name', subfield('a'))
                                                  ],
                                                  # unique=values(subfield('a')),
                                                  links={
                                                      BL + 'name': subfield('a'),
                                                      MARC + 'miscInfo': subfield('g')
                                                  }
                                      )
                              }
    ),

    # genres - the is-ness about a work

    # note: teasing 655 form / genre in two ways. one as a subject
    # with a value Concept that has a focus of Form, the other simply
    # as genre with a value of Form

    '600$v': onwork.materialize(BL + 'Form',
                                BL + 'genre',
                                unique=[
                                    (BL + 'name', subfield('v'))
                                ],
                                links={
                                    BL + 'name': subfield('v')
                                }
    ),

    '610$v': onwork.materialize(BL + 'Form',
                                BL + 'genre',
                                unique=[
                                    (BL + 'name', subfield('v'))
                                ],
                                links={
                                    BL + 'name': subfield('v')
                                }
    ),

    '611$v': onwork.materialize(BL + 'Form',
                                BL + 'genre',
                                unique=[
                                    (BL + 'name', subfield('v'))
                                ],
                                links={
                                    BL + 'name': subfield('v')
                                }
    ),

    '650$v': onwork.materialize(BL + 'Form',
                                BL + 'genre',
                                unique=[
                                    (BL + 'name', subfield('v'))
                                ],
                                links={
                                    BL + 'name': subfield('v')
                                }
    ),

    '651$v': onwork.materialize(BL + 'Form',
                                BL + 'genre',
                                unique=[
                                    (BL + 'name', subfield('v'))
                                ],
                                links={
                                    BL + 'name': subfield('v')
                                }
    ),

    '630$v': onwork.materialize(BL + 'Form',
                                BL + 'genre',
                                unique=[
                                    (BL + 'name', subfield('v'))
                                ],
                                links={
                                    BL + 'name': subfield('v')
                                }
    ),

    '655$a': onwork.materialize(BL + 'Form',
                                BL + 'genre',
                                unique=[
                                    (BL + 'name', subfield('a'))
                                ],
                                links={
                                    BL + 'name': subfield('a')
                                }
    ),

    # Fields 700,710,711,etc. have a contributor + role (if specified) relationship to a new Agent object (only created as a new object if all subfields are unique)
    # Generate hash values only from the properties specific to Agents
    # If there is a 700$t however this is an indication that there is a new Work. And yes, we're building a touring complete micro-language to address such patterns.

    '700': ifexists(subfield('t'),
                    onwork.materialize(BL + 'Work',
                                       values(
                                           BL + 'related',
                                           relator_property(subfield('i'), prefix=REL)
                                       ),
                                       unique=[
                                           (BL + 'title', subfield('t')),
                                           (BL + 'language', subfield('l')),
                                           (AV + 'musicMedium', subfield('m')),
                                           (MARC + 'titleNumber', subfield('n')),
                                           (AV + 'arrangedMusic', subfield('o')),
                                           (MARC + 'titlePart', subfield('p')),
                                           (AV + 'musicKey', subfield('r')),
                                           (MARC + 'form', subfield('k')),
                                           (BL + 'date', subfield('f')),
                                           (MARC + 'version', subfield('s')),
                                       ],
                                       # unique=values(subfield('t'), subfield('l'), subfield('m'), subfield('n'),
                                       # subfield('o'), subfield('p'), subfield('r'), subfield('k'),
                                       # subfield('f'), subfield('s')
                                       # ),
                                       links={
                                           BL + 'title': subfield('t'),
                                           BL + 'language': subfield('l'),
                                           AV + 'musicMedium': subfield('m'),
                                           MARC + 'titleNumber': subfield('n'),
                                           AV + 'arrangedMusic': subfield('o'),
                                           MARC + 'titlePart': subfield('p'),
                                           AV + 'musicKey': subfield('r'),
                                           MARC + 'form': subfield('k'),
                                           BL + 'date': subfield('f'),
                                           MARC + 'version': subfield('s'),
                                           ifexists(subfield('a'), BL + 'creator'):
                                               materialize(BL + 'Person',
                                                           unique=[
                                                               (BL + 'name', subfield('a')),
                                                               (BL + 'date', subfield('d'))
                                                           ],
                                                           # unique=values(subfield('a'),
                                                           # subfield('d')
                                                           # ),
                                                           links={
                                                               BL + 'name': subfield('a'),
                                                               BL + 'date': subfield('d')
                                                           }
                                               )
                                       }
                    ),
                    onwork.materialize(BL + 'Person',
                                       values(
                                           BL + 'contributor',
                                           relator_property(subfield('e'), prefix=REL),
                                           relator_property(subfield('4'), prefix=REL)
                                       ),
                                       unique=[
                                           (BL + 'name', subfield('a')),
                                           (MARC + 'numeration', subfield('b')),
                                           (MARC + 'titles', subfield('c')),
                                           (BL + 'date', subfield('d')),
                                           (MARC + 'nameAlternative', subfield('q')),
                                       ],
                                       # unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'),
                                       # subfield('g'), subfield('j'), subfield('q'), subfield('u')),
                                       links={
                                           BL + 'name': subfield('a'),
                                           MARC + 'numeration': subfield('b'),
                                           MARC + 'titles': subfield('c'),
                                           BL + 'date': subfield('d'),
                                           BL + 'nameAlternative': subfield('q'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0'))
                                           )
                                       }
                    )
    ),

    '710': ifexists(subfield('t'),
                    onwork.materialize(BL + 'Work',
                                       values(
                                           BL + 'related',
                                           relator_property(subfield('i'), prefix=REL)
                                       ),
                                       unique=[
                                           (BL + 'title', subfield('t')),
                                           (BL + 'language', subfield('l'))
                                       ],
                                       links={BL + 'language': subfield('l'),
                                              ifexists(subfield('a'), BL + 'creator'):
                                                  materialize(BL + 'Organization',
                                                              unique=[
                                                                  (BL + 'name', subfield('a'))
                                                              ],
                                                              # unique=values(subfield('a')),more RE
                                                              links={
                                                                  BL + 'name': subfield('a'),
                                                                  BL + 'date': subfield('d')
                                                              }
                                                  ),
                                              BL + 'title': subfield('t'),
                                              BL + 'language': subfield('l')
                                       }
                    ),
                    onwork.materialize(BL + 'Organization',
                                       values(
                                           BL + 'contributor',
                                           relator_property(subfield('e'), prefix=REL),
                                           relator_property(subfield('4'), prefix=REL)
                                       ),
                                       unique=[
                                           (BL + 'name', subfield('a')),
                                           (MARC + 'subordinateUnit', subfield('b')),
                                           (BL + 'date', subfield('d'))
                                       ],
                                       # unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('g'),
                                       # subfield('j'), subfield('q'), subfield('u')),
                                       links={
                                           BL + 'name': subfield('a'),
                                           MARC + 'subordinateUnit': subfield('b'),
                                           BL + 'date': subfield('d'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0')))
                                       }
                    )
    ),

    '711': ifexists(subfield('t'),
                    onwork.materialize(BL + 'Work',
                                       values(
                                           BL + 'related',
                                           relator_property(subfield('i'), prefix=REL)
                                       ),
                                       unique=[
                                           (BL + 'language', subfield('l')),
                                           (BL + 'title', subfield('t')),
                                       ],
                                       # unique=values(subfield('t'),
                                       # subfield('l')),
                                       links={
                                           BL + 'language': subfield('l'),
                                           BL + 'title': subfield('t'),
                                           ifexists(subfield('a'), BL + 'creator'):
                                               materialize(BL + 'Meeting',
                                                           unique=[
                                                               (BL + 'name', subfield('a'))
                                                           ],
                                                           # unique=values(subfield('a')),
                                                           links={
                                                               BL + 'name': subfield('a'),
                                                               BL + 'date': subfield('d')
                                                           }
                                               )
                                       }
                    ),
                    onwork.materialize(BL + 'Meeting',
                                       values(
                                           BL + 'contributor',
                                           relator_property(subfield('e'), prefix=REL),
                                           relator_property(subfield('4'), prefix=REL)
                                       ),
                                       unique=[
                                           (BL + 'name', subfield('a')),
                                           (BL + 'date', subfield('d')),
                                           (MARC + 'nameAlternative', subfield('q')),
                                       ],
                                       # unique=values(subfield('a'), subfield('c'), subfield('d'), subfield('e'),
                                       # subfield('q'), subfield('u')
                                       # ),
                                       links={
                                           BL + 'name': subfield('a'),
                                           BL + 'date': subfield('d'),
                                           BL + 'nameAlternative': subfield('q'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('0')))
                                       }
                    ),
    ),

    '720-1#': onwork.materialize(BL + 'Person',
                                 values(
                                     BL + 'contributor',
                                     relator_property(subfield('e'), prefix=REL),
                                     relator_property(subfield('4'), prefix=REL)
                                 ),
                                 unique=[
                                     (BL + 'name', subfield('a'))
                                 ],
                                 # unique=values(subfield('a')),
                                 links={
                                     BL + 'name': subfield('a')
                                 }
    ),

    '720-##': onwork.materialize(BL + 'Agent',
                                 values(
                                     BL + 'contributor',
                                     relator_property(subfield('e'), prefix=REL),
                                     relator_property(subfield('4'), prefix=REL)
                                 ),
                                 unique=[
                                     (BL + 'name', subfield('a'))
                                 ],
                                 # unique=values(subfield('a')),
                                 links={
                                     BL + 'name': subfield('a')
                                 }
    ),

    '730': onwork.materialize(BL + 'Collection',
                              BL + 'related',
                              unique=all_subfields,
                              links={
                                  BL + 'title': ifexists(subfield('a'), subfield('a'), alt=subfield('t')),
                                  BL + 'language': subfield('l'),
                                  BL + 'date': subfield('f'),
                                  BL + 'medium': subfield('h'),
                                  MARC + 'titlePart': subfield('p'),
                                  MARC + 'titleNumber': subfield('n'),
                                  MARC + 'version': subfield('s'),
                                  AV + 'musicKey': subfield('r'),
                                  AV + 'arrangedStatementForMusic': subfield('o'),
                                  AV + 'musicMedium': subfield('m')
                              }

    ),

    '740': onwork.materialize(BL + 'Work',
                              BL + 'related',
                              unique=[
                                  (BL + 'title', subfield('a')),
                                  (BL + 'medium', subfield('h')),
                                  (MARC + 'titleNumber', subfield('n')),
                                  (MARC + 'titlePart', subfield('p')),
                              ],
                              # unique=values(subfield('a'), subfield('h'),
                              # subfield('n'), subfield('p')),
                              links={
                                  BL + 'title': subfield('a'),
                                  MARC + 'medium': subfield('h'),
                                  MARC + 'titleNumber': subfield('n'),
                                  MARC + 'titlePart': subfield('p')
                              }
    ),

    # Linking Entries

    # SubSeries

    '760': onwork.materialize(MARC + 'Series',
                              REL + 'isSubSeriesOf',
                              unique=all_subfields,
                              links={
                                  BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                  MARC + 'issn': subfield('x'),
                                  BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                  MARC + 'edition': subfield('b'),
                                  BL + 'note': subfield('n'),
                                  MARC + 'isbn': subfield('z')
                              }
    ),

    '762': onwork.materialize(MARC + 'Series',
                              values(REL + 'hasSubSeries'),
                              unique=all_subfields,
                              links={
                                  BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                  MARC + 'issn': subfield('x'),
                                  BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                  MARC + 'edition': subfield('b'),
                                  BL + 'note': subfield('n'),
                                  MARC + 'isbn': subfield('z')
                              }
    ),

    # Translation(s)

    '765': ifexists(subfield('s'),
                    onwork.materialize(BL + 'Collection',
                                       values(REL + 'isTranslationOf'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': subfield('s'),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    ),
                    onwork.materialize(BL + 'Work',
                                       values(REL + 'isTranslationOf'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    )
    ),

    '767': ifexists(subfield('s'),
                    onwork.materialize(BL + 'Collection',
                                       values(REL + 'hasTranslation'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': subfield('s'),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    ),
                    onwork.materialize(BL + 'Work',
                                       values(REL + 'hasTranslation'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    )
    ),

    # Supplemental

    '770': ifexists(subfield('s'),
                    onwork.materialize(BL + 'Collection',
                                       values(REL + 'isSupplementOf'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': subfield('s'),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    ),
                    onwork.materialize(BL + 'Work',
                                       values(REL + 'isSupplementOf'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    )
    ),

    '772': ifexists(subfield('s'),
                    onwork.materialize(BL + 'Collection',
                                       values(REL + 'hasSupplement'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': subfield('s'),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    ),
                    onwork.materialize(BL + 'Work',
                                       values(REL + 'hasSupplement'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    )
    ),

    # Is Part Of (vertical relationship)

    '773': ifexists(subfield('s'),
                    onwork.materialize(BL + 'Collection',
                                       values(REL + 'isPartOf'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': subfield('s'),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    ),
                    onwork.materialize(BL + 'Work',
                                       values(REL + 'isPartOf'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    )
    ),

    '774': ifexists(subfield('s'),
                    onwork.materialize(BL + 'Collection',
                                       values(REL + 'isPartOf'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': subfield('s'),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    ),
                    onwork.materialize(BL + 'Work',
                                       values(REL + 'isPartOf'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    )
    ),

    # Other editions

    '775': ifexists(subfield('s'),
                    onwork.materialize(BL + 'Collection',
                                       values(REL + 'hasEdition'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': subfield('s'),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    ),
                    onwork.materialize(BL + 'Work',
                                       values(REL + 'hasEdition'),
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    )
    ),

    # Alternative Format (Instance) - define instance to instance relationship and instantiates

    '776': ifexists(subfield('s'),
                    oninstance.materialize(BL + 'Collection',
                                           values(REL + 'hasOtherPhysicalFormat'),
                                           unique=all_subfields,
                                           links={
                                               BL + 'title': subfield('s'),
                                               ifexists(subfield('a'), BL + 'creator'):
                                                   materialize(BL + 'Agent',
                                                               unique=[
                                                                   (BL + 'name', subfield('a'))
                                                               ],
                                                               links={
                                                                   BL + 'name': subfield('a')
                                                               }
                                                   ),
                                               BL + 'authorityLink': url(
                                                   replace_from(AUTHORITY_CODES, subfield('w'))),
                                               MARC + 'edition': subfield('b'),
                                               BL + 'note': values(subfield('n'), subfield('c'), subfield('i')),
                                               MARC + 'issn': subfield('x'),
                                               MARC + 'isbn': normalize_isbn(subfield('z'))}
                    ),
                    oninstance.materialize(BL + 'Instance',
                                           values(REL + 'hasOtherPhysicalFormat'),
                                           unique=all_subfields,
                                           links={
                                               BL + 'title': subfield('t'),
                                               ifexists(subfield('a'), BL + 'creator'):
                                                   materialize(BL + 'Agent',
                                                               unique=[
                                                                   (BL + 'name', subfield('a'))
                                                               ],
                                                               links={
                                                                   BL + 'name': subfield('a')
                                                               }
                                                   ),
                                               BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                               MARC + 'edition': subfield('b'),
                                               BL + 'note': values(subfield('n'), subfield('c'), subfield('i')),
                                               MARC + 'issn': subfield('x'),
                                               MARC + 'isbn': normalize_isbn(subfield('z')),
                                               BL + 'instantiates': anchor(BL+'Work')},
                                           postprocess=POSTPROCESS_AS_INSTANCE
                    )
    ),

    # Issued With (instance)

    '777': ifexists(subfield('s'),
                    oninstance.materialize(BL + 'Collection',
                                           values(REL + 'issuedWith'),
                                           unique=all_subfields,
                                           links={
                                               BL + 'title': subfield('s'),
                                               MARC + 'issn': subfield('x'),
                                               BL + 'authorityLink': url(
                                                   replace_from(AUTHORITY_CODES, subfield('w'))),
                                               MARC + 'edition': subfield('b'),
                                               BL + 'note': subfield('n'),
                                               MARC + 'isbn': subfield('z')}
                    ),
                    oninstance.materialize(BL + 'Instance',
                                           values(REL + 'issuedWith'),
                                           unique=all_subfields,
                                           links={
                                               BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                               MARC + 'issn': subfield('x'),
                                               BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                               MARC + 'edition': subfield('b'),
                                               BL + 'note': subfield('n'),
                                               MARC + 'isbn': subfield('z')}
                    )
    ),

    # Preceding Entry

    '780-?0': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          values(REL + 'continues'),
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          values(REL + 'continues'),
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '780-?1': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'continuesInPart',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'continuesInPart',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '780-?2': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'supersedes',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'supersedes',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '780-?3': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'supersedesInPart',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'supersedesInPart',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '780-?4': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'unionOf',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'unionOf',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '780-?5': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'absorbed',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'absorbed',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '780-?6': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'absorbedInPart',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'absorbedInPart',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '780-?7': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'separatedFrom',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'separatedFrom',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'edition': subfield('b'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    # Succeeding Entry

    '785-?0': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'continuedBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'continuedBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '785-?1': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'continuedInPartBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'continuedInPartBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '785-?2': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'supersededBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'supersededBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '785-?3': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'supersededInPartBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'supersededInPartBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '785-?4': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'absorbedBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'absorbedBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '785-?5': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'absorbedInPartBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'edition': subfield('b'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'absorbedInPartBy',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '785-?6': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'splitInto',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'splitInto',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '785-?7': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'mergedWith',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'mergedWith',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    '785-?8': ifexists(subfield('s'),
                       onwork.materialize(BL + 'Collection',
                                          REL + 'changedBackTo',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': subfield('s'),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(
                                                  replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       ),
                       onwork.materialize(BL + 'Work',
                                          REL + 'changedBackTo',
                                          unique=all_subfields,
                                          links={
                                              BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                              MARC + 'issn': subfield('x'),
                                              BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                              MARC + 'edition': subfield('b'),
                                              BL + 'note': subfield('n'),
                                              MARC + 'isbn': subfield('z')}
                       )
    ),

    # Other related works / collections

    '787': ifexists(subfield('s'),
                    onwork.materialize(BL + 'Collection',
                                       BL + 'related',
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': subfield('s'),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    ),
                    onwork.materialize(BL + 'Work',
                                       BL + 'related',
                                       unique=all_subfields,
                                       links={
                                           BL + 'title': ifexists(subfield('t'), subfield('t'), alt=subfield('a')),
                                           MARC + 'issn': subfield('x'),
                                           BL + 'authorityLink': url(replace_from(AUTHORITY_CODES, subfield('w'))),
                                           MARC + 'edition': subfield('b'),
                                           BL + 'note': subfield('n'),
                                           MARC + 'isbn': subfield('z')}
                    )
    ),

    # Series

    '830': onwork.materialize(MARC + 'Series',
                              BL + 'memberOf',
                              unique=[
                                  (BL + 'name', subfield('a'))
                              ],
                              # unique=values(subfield('a')),
                              links={
                                  BL + 'title': subfield('a'),
                                  MARC + 'titleRemainder': subfield('k'),
                                  MARC + 'volume': subfield('v'),
                                  MARC + 'titleNumber': subfield('n'),
                                  MARC + 'titlePart': subfield('p'),
                              }
    ),

    '856$u': oninstance.link(rel=BL + 'link', res=True),

}

BFLITE_TRANSFORMS_ID = 'http://bibfra.me/tool/pybibframe/transforms#bflite'
register_transforms(BFLITE_TRANSFORMS_ID, BFLITE_TRANSFORMS)

MARC_TRANSFORMS = {  # #HeldItem is a refinement of Annotation
    # '852': oninstance.materialize(BL+'Annotation',
    # BA+'institution',
    # unique=all_subfields,
    # links={BA+'holderType': BA+'Library', BA+'location': subfield('a'), BA+'subLocation': subfield('b'), BA+'callNumber': subfield('h'), BA+'code': subfield('n'), BL+'link': subfield('u'), BA+'streetAddress': subfield('e')}),
}

MARC_TRANSFORMS_ID = 'http://bibfra.me/tool/pybibframe/transforms#marc'
register_transforms(MARC_TRANSFORMS_ID, MARC_TRANSFORMS)

# XXX This might instead be a job for collections.ChainMap
TRANSFORMS = {}
TRANSFORMS.update(BFLITE_TRANSFORMS)
TRANSFORMS.update(MARC_TRANSFORMS)
