# -*- coding: utf-8 -*-
'''
Declarations defining patterns to be asserted upon MARC files to generate linked data
in the form of a Versa output model

BFLITE_TRANSFORMS is an example of a speification designed to be understood
by moderately tech-savvy librarians, and even overridden to specialize the
MARC -> BIBFRAME conversion by the more adventurous.

A few examples of entries to help communicate the nature and power of the pattern
specification language

    '001': oninstance.rename(rel=BL+'controlCode'),

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

    '010$a': onwork.rename(rel=MARC+'lccn'),

what's matched is any MARC 010 tag field which has an `a` subfield.
The generated link originates with the materialized work resource rather than
than the instance. The link relationship IRI is `http://bibfra.me/vocab/marc/lccn`.
The link target value comes form the value of the `a` subfield.

    '100': onwork.materialize(
                BL+'Person', BL+'creator',
                unique=values(subfield('a'), subfield('b'), subfield('c')),
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
                unique=values(subfield('a'), subfield('b'), subfield('c')),
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
                unique=all_subfields, 
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

'''
#all_subfields - All the MARC subfields are used together to determine the uniqueness

#Full MARC field list: http://www.loc.gov/marc/bibliographic/ecbdlist.html

#These two lines are required at the top
from bibframe import BL, BA, REL, MARC, RBMS, AV
from bibframe.reader.util import *

#This line only needed if you are using advanced patterns e.g. with the replace_from function
import re

#from bibframe.reader.marcpatterns import *
#sorted([ (m, MATERIALIZE[m]) for m in MATERIALIZE if [ wf for wf in WORK_FIELDS if m[:2] == wf[:2]] ])

#    '100': onwork.materialize('Agent', 'creator', unique=all_subfields, links={'a': 'label'}),

# where do we put LDR info, e.g. LDR 07 / 19 positions = mode of issuance

AUTHORITY_CODES = [
    (re.compile(r'\(DLC\)\s*(\S+)'), r'http://lccn.loc.gov/\1'),
    (re.compile(r'\(OCoLC\)fst(\d+)'), r'http://id.worldcat.org/fast/\1'),
    (re.compile(r'\(OCoLC\)\s*(\d+)'), r'http://www.worldcat.org/oclc/\1'),
    (re.compile(r'\(0CoLC\)\s*(\d+)'), r'http://www.worldcat.org/oclc/\1'),   # yes, thats 0CoLC not OCoLC
    (re.compile(r'\(viaf\)\s*(\S+)'), r'http://viaf.org/viaf/\1'),
    (re.compile(r'\(DNLM\)\s*(\S+)'), r'http://www.ncbi.nlm.nih.gov/nlmcatalog?term=\1'),
    (re.compile(r'\(DE\-101\)\s*(\S+)'), r'http://d-nb.info/\1'),
    (re.compile(r'\(LoC\)\s*(\S+)'), r'http://id.loc.gov/authorities/names/\1')
]


BFLITE_TRANSFORMS = {
    '001': oninstance.rename(rel=BL+'controlCode'),

    #Link to the 010a value, naming the relationship 'lccn'
    '010$a': oninstance.rename(rel=MARC+'lccn'),
    '017$a': oninstance.rename(rel=MARC+'legalDeposit'),
    #ISBN is specially processed
    #'020$a': oninstance.rename(rel='isbn'),
    '022$a': oninstance.rename(rel=MARC+'issn'),
    '024$a': oninstance.rename(rel=MARC+'otherControlNumber'),
    '024$a-#1': oninstance.rename(rel=MARC+'upc'),
    '025$a': oninstance.rename(rel=MARC+'lcOverseasAcq'),

    '028$a': oninstance.rename(rel=MARC+'publisherNumber'),
    '028$a-#0': oninstance.rename(rel=MARC+'issueNumber'),
    '028$a-#2': oninstance.rename(rel=MARC+'plateNumber'),
    '028$a-#4': oninstance.rename(rel=MARC+'videoRecordingNumber'),    

    '034$a': oninstance.rename(rel=MARC+'cartographicMathematicalDataScaleStatement'),  #Rebecca & Sally suggested this should effectively be a merge with 034a
    '034$b': oninstance.rename(rel=MARC+'cartographicMathematicalDataProjectionStatement'),
    '034$c': oninstance.rename(rel=MARC+'cartographicMathematicalDataCoordinateStatement'),
    '035$a': oninstance.rename(rel=MARC+'systemControlNumber'),
    '037$a': oninstance.rename(rel=MARC+'stockNumber'),

    '040$a': onwork.rename(rel=MARC+'catalogingSource'),
    '041$a': onwork.rename(rel=BL+'language'),
    '050$a': onwork.rename(rel=MARC+'lcCallNumber'),
    '050$b': onwork.rename(rel=MARC+'lcItemNumber'),
    '050$3': onwork.rename(rel=BL+'material'),
    '060$a': onwork.rename(rel=MARC+'nlmCallNumber'),
    '060$b': onwork.rename(rel=MARC+'nlmItemNumber'),
    '061$a': onwork.rename(rel=MARC+'nlmCopyStatement'),
    '070$a': onwork.rename(rel=MARC+'nalCallNumber'),
    '070$b': onwork.rename(rel=MARC+'nalItemNumber'),
    '071$a': onwork.rename(rel=MARC+'nalCopyStatement'),
    '082$a': onwork.rename(rel=MARC+'deweyNumber'),

    # Fields 100,110,111,etc. have a creator + role (if available) relationship to a new Agent object (only created as a new object if all subfields are unique)
    # generate hash values only from the properties specific to Agents 

    '100': onwork.materialize(BL+'Person', 
                              values(BL+'creator', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')),
                              links={BL+'name': subfield('a'), MARC+'numeration': subfield('b'), MARC+'titles': subfield('c'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0')), MARC+'additionalName': subfield('q')}),

    '110': onwork.materialize(BL+'Organization', 
                              values(BL+'creator', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')),
                              links={BL+'name': subfield('a'), MARC+'subordinateUnit': subfield('b'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0')), MARC+'additionalName': subfield('q')}),

    '111': onwork.materialize(BL+'Meeting', 
                              values(BL+'creator', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')),
                              links={BL+'name': subfield('a'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0')), MARC+'additionalName': subfield('q')}),

    '210$a': oninstance.rename(rel=MARC+'abbreviatedTitle'),
    '222$a': oninstance.rename(rel=MARC+'keyTitle'),

    '240': onwork.materialize(BL+'Collection', 
                              BL+'memberOf', 
                              unique=values(subfield('a'), subfield('d'), subfield('h'), subfield('l'), subfield('m'), subfield('n'), subfield('o'), subfield('p'), subfield('r'), subfield('k'), subfield('f'), subfield('s')),
                              links={BL+'title': subfield('a'), MARC+'legalDate': subfield('d'), BL+'medium': subfield('h'), BL+'language': subfield('l'), AV+'musicMedium': subfield('m'), MARC+'titleNumber': subfield('n'), AV+'arrangedMusic': subfield('o'), MARC+'titlePart': subfield('p'), AV+'musicKey': subfield('r'), MARC+'form': subfield('k'), BL+'date': subfield('f'), MARC+'version': subfield('s')}),
    
    '243': onwork.materialize(BL+'Collection', 
                              BL+'memberOf', 
                              unique=values(subfield('a'), subfield('d'), subfield('h'), subfield('l'), subfield('m'), subfield('n'), subfield('o'), subfield('p'), subfield('r'), subfield('k'), subfield('f'), subfield('s')),
                              links={BL+'title': subfield('a'), MARC+'legalDate': subfield('d'), BL+'medium': subfield('h'), BL+'language': subfield('l'), AV+'musicMedium': subfield('m'), MARC+'titleNumber': subfield('n'), AV+'arrangedMusic': subfield('o'), MARC+'titlePart': subfield('p'), AV+'musicKey': subfield('r'), MARC+'form': subfield('k'), BL+'date': subfield('f'), MARC+'version': subfield('s')}),

    # Title(s) - replicate across both Work and Instance(s) 

    '245$a': (onwork.rename(rel=BL+'title'), oninstance.rename(rel=BL+'title')),
    '245$b': (onwork.rename(rel=MARC+'titleRemainder'), oninstance.rename(rel=MARC+'titleRemainder')),
    '245$c': (onwork.rename(rel=MARC+'titleStatement'), oninstance.rename(rel=MARC+'titleStatement')),
    '245$n': (onwork.rename(rel=MARC+'titleNumber'), oninstance.rename(rel=MARC+'titleNumber')),
    '245$p': (onwork.rename(rel=MARC+'titlePart'), oninstance.rename(rel=MARC+'titlePart')),

    '245$f': onwork.rename(rel=MARC+'inclusiveDates'),
    '245$h': oninstance.rename(rel=BL+'medium'),
    '245$k': onwork.rename(rel=MARC+'formDesignation'),
    '246$a': onwork.rename(rel=MARC+'titleVariation'),
    '246$b': onwork.rename(rel=MARC+'titleVariationRemainder'),
    '246$f': onwork.rename(rel=MARC+'titleVariationDate'),
    '247$a': onwork.rename(rel=MARC+'formerTitle'),
    '250$a': oninstance.rename(rel=MARC+'edition'),
    '250$b': oninstance.rename(rel=MARC+'edition'),
    '254$a': oninstance.rename(rel=MARC+'musicalPresentation'),
    '255$a': oninstance.rename(rel=MARC+'cartographicMathematicalDataScaleStatement'),
    '255$b': oninstance.rename(rel=MARC+'cartographicMathematicalDataProjectionStatement'),
    '255$c': oninstance.rename(rel=MARC+'cartographicMathematicalDataCoordinateStatement'),
    '256$a': oninstance.rename(rel=MARC+'computerFilecharacteristics'),

    # Provider materialization 

    #'260': oninstance.materialize('ProviderEvent', 
    #                              'publication', 
    #                              unique=all_subfields, 
    #                              links={ifexists(subfield('a'), 'providerPlace'): materialize('Place', unique=subfield('a'), links={'name': subfield('a')}), 
    #                                             ifexists(subfield('b'), 'providerAgent'): materialize('Agent', unique=target(), links={'name': subfield('b')}), 
    #                                             'providerDate': subfield('c')}),
    
    '260': oninstance.materialize(BL+'ProviderEvent', 
                                  MARC+'publication', 
                                  unique=all_subfields, 
                                  links={
                                      ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), links={BL+'name': subfield('a')}),
                                      foreach(target=subfield('b')): materialize(BL+'Agent', BL+'providerAgent', unique=target(), links={BL+'name': target()}),
                                      BL+'providerDate': subfield('c')
                                  },
#foreach(create_link(target=materialize('Agent', unique=target(), links={'name': subfield('b')})), rel='providerAgent', target=subfield('b'))
                                      #foreach(rel='providerAgent', target=subfield('b'))
                                  ),

    '264': oninstance.materialize(BL+'ProviderEvent', 
                                  MARC+'publication', 
                                  unique=all_subfields, 
                                  links={ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), 
                                                                                                  links={BL+'name': subfield('a')}), 
                                         ifexists(subfield('b'), BL+'providerAgent'): materialize(BL+'Agent', unique=subfield('b'), 
                                                                                                  links={BL+'name': subfield('b')}), BL+'providerDate': subfield('c')}
                                  ),

    #Ind1 is blank ('#') ind2 is 3

    '264$c-#4': oninstance.rename(rel=MARC+'copyrightDate'),

    '264-#3': oninstance.materialize(BL+'ProviderEvent', 
                                     MARC+'manufacture', 
                                     unique=all_subfields, 
                                     links={ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), 
                                                                                                     links={BL+'name': subfield('a')}), 
                                                    ifexists(subfield('b'), BL+'providerAgent'): materialize(BL+'Agent', unique=subfield('b'), 
                                                                                                             links={BL+'name': subfield('b')}), BL+'providerDate': subfield('c')}
                                     ),

    '264-#2': oninstance.materialize(BL+'ProviderEvent', 
                                     MARC+'distribution', 
                                     unique=all_subfields, 
                                     links={ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), 
                                                                                                     links={BL+'name': subfield('a')}), 
                                                    ifexists(subfield('b'), BL+'providerAgent'): materialize(BL+'Agent', unique=subfield('b'), 
                                                                                                             links={BL+'name': subfield('b')}), BL+'providerDate': subfield('c')}
                                     ),

    '264-#1': oninstance.materialize(BL+'ProviderEvent', 
                                     MARC+'publication', 
                                     unique=all_subfields, 
                                     links={ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), 
                                                                                                     links={BL+'name': subfield('a')}), 
                                                    ifexists(subfield('b'), 'providerAgent'): materialize(BL+'Agent', unique=subfield('b'), 
                                                                                                          links={BL+'name': subfield('b')}), BL+'providerDate': subfield('c')}
                                     ),

    '264-#0': oninstance.materialize(BL+'ProviderEvent', 
                                     MARC+'production', 
                                     unique=all_subfields, 
                                     links={ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), 
                                                                                                     links={BL+'name': subfield('a')}), 
                                                    ifexists(subfield('b'), BL+'providerAgent'): materialize(BL+'Agent', unique=subfield('b'), 
                                                                                                             links={BL+'name': subfield('b')}), BL+'providerDate': subfield('c')}),

    '300$a': oninstance.rename(rel=BL+'extent'),
    '300$b': oninstance.rename(rel=MARC+'otherPhysicalDetails'),
    '300$c': oninstance.rename(rel=BL+'dimensions'),
    '300$e': oninstance.rename(rel=MARC+'accompanyingMaterial'),
    '300$f': oninstance.rename(rel=MARC+'typeOfunit'),
    '300$g': oninstance.rename(rel=MARC+'size'),
    '300$3': oninstance.rename(rel=MARC+'materials'),
    '310$a': oninstance.rename(rel=MARC+'publicationFrequency'),
    '310$b': oninstance.rename(rel=MARC+'publicationDateFrequency'),
    '336$a': oninstance.rename(rel=MARC+'contentCategory'),
    '336$b': oninstance.rename(rel=MARC+'contentTypeCode'),
    '336$2': oninstance.rename(rel=MARC+'contentTypeMARCsource'),
    '337$a': oninstance.rename(rel=MARC+'mediaCategory'),
    '337$b': oninstance.rename(rel=MARC+'mediaTypeCode'),
    '337$2': oninstance.rename(rel=MARC+'medaiMARCsource'),
    '338$a': oninstance.rename(rel=MARC+'carrierCategory'),
    '338$b': oninstance.rename(rel=MARC+'carrierCategoryCode'),
    '338$2': oninstance.rename(rel=MARC+'carrierMARCSource'),
    '340$a': oninstance.rename(rel=MARC+'physicalSubstance'),
    '340$b': oninstance.rename(rel=MARC+'dimensions'),
    '340$c': oninstance.rename(rel=MARC+'materialsApplied'),
    '340$d': oninstance.rename(rel=MARC+'recordingTechnique'),
    '340$e': oninstance.rename(rel=MARC+'physicalSupport'),
    '351$a': oninstance.rename(rel=MARC+'organizationMethod'),
    '351$b': oninstance.rename(rel=MARC+'arrangement'),
    '351$c': oninstance.rename(rel=MARC+'hierarchy'),
    '351$3': oninstance.rename(rel=MARC+'materialsSpec'),

    '362$a': oninstance.rename(rel=MARC+'publicationDesignation'),



# let's make some music! 
#
#    '382$a': onwork.materialize('Medium', 
#                                'performanceMedium', 
#                                unique=values(subfield('a')),
#                                links={'name': subfield('a')}),
#
#    '382$b': onwork.materialize('Medium', 
#                                'featuredMedium', 
#                                unique=values(subfield('b')),
#                                links={'name': subfield('b')}),
#
#    '382$p': onwork.materialize('Medium', 
#                                'alternativeMedium', 
#                                unique=values(subfield('f')),
#                                links={'name': subfield('f')}),
#

    '382$a': onwork.rename(rel=AV+'performanceMedium'),
    '382$b': onwork.rename(rel=AV+'featuredMedium'),
    '382$p': onwork.rename(rel=AV+'alternativeMedium'),

    '382$s': onwork.rename(rel=AV+'numberOfPerformers'),
    '382$v': onwork.rename(rel=AV+'mediumNote'),

    '490$a': onwork.rename(rel=MARC+'seriesStatement'),
    '490$v': onwork.rename(rel=MARC+'seriesVolume'),

    '500$a': onwork.rename(rel=BL+'note'),
    '501$a': onwork.rename(rel=MARC+'note'),
    '502$a': onwork.rename(rel=MARC+'dissertationNote'),
    '502$b': onwork.rename(rel=MARC+'degree'),
    '502$c': onwork.rename(rel=MARC+'grantingInstitution'),
    '502$d': onwork.rename(rel=MARC+'dissertationYear'),
    '502$g': onwork.rename(rel=MARC+'dissertationNote'),
    '502$o': onwork.rename(rel=MARC+'dissertationID'),
    '504$a': onwork.rename(rel=MARC+'bibliographyNote'),

    '505$a': oninstance.rename(rel=MARC+'contentsNote'),

    '506$a': oninstance.rename(rel=MARC+'governingAccessNote'),
    '506$b': oninstance.rename(rel=MARC+'jurisdictionNote'),
    '506$c': oninstance.rename(rel=MARC+'physicalAccess'),
    '506$d': oninstance.rename(rel=MARC+'authorizedUsers'),
    '506$e': oninstance.rename(rel=MARC+'authorization'),
    '506$u': oninstance.rename(rel=MARC+'uriNote'),
    '507$a': oninstance.rename(rel=MARC+'representativeFractionOfScale'),
    '507$b': oninstance.rename(rel=MARC+'remainderOfScale'),
    '508$a': oninstance.rename(rel=MARC+'creditsNote'),
    '510$a': onwork.rename(rel=MARC+'citationSource'),
    '510$b': onwork.rename(rel=MARC+'citationCoverage'),
    '510$c': onwork.rename(rel=MARC+'citationLocationWithinSource'),
    '510$u': onwork.rename(rel=MARC+'citationUri'),
    '511$a': onwork.rename(rel=MARC+'performerNote'),
    '513$a': onwork.rename(rel=MARC+'typeOfReport'),
    '513$b': onwork.rename(rel=MARC+'periodCoveredn'),
    '514$a': onwork.rename(rel=MARC+'dataQuality'),
    '515$a': oninstance.rename(rel='MARC+numberingPerculiarities'),
    '516$a': oninstance.rename(rel=MARC+'typeOfComputerFile'),
    '518$a': onwork.rename(rel=MARC+'dateTimePlace'),
    '518$d': onwork.rename(rel=MARC+'dateOfEvent'),
    '518$o': onwork.rename(rel=MARC+'otherEventInformation'),
    '518$p': onwork.rename(rel=MARC+'placeOfEvent'),
    '520$a': onwork.rename(rel=MARC+'summary'),
    '520$b': onwork.rename(rel=MARC+'summaryExpansion'),
    '520$c': onwork.rename(rel=MARC+'assigningSource'),
    '520$u': onwork.rename(rel=MARC+'summaryURI'),
    '521$a': onwork.rename(rel=MARC+'intendedAudience'),
    '521$b': onwork.rename(rel=MARC+'intendedAudienceSource'),
    '522$a': onwork.rename(rel=MARC+'geograhpicCoverage'),
    '525$a': oninstance.rename(rel=MARC+'supplement'),
    '526$a': onwork.rename(rel=MARC+'studyProgramName'),
    '526$b': onwork.rename(rel=MARC+'interestLevel'),
    '526$c': onwork.rename(rel=MARC+'readingLevel'),
    '530$a': oninstance.rename(rel=MARC+'additionalPhysicalForm'),
    '533$a': onwork.rename(rel=MARC+'reproductionNote'),
    '534$a': onwork.rename(rel=MARC+'originalVersionNote'),
    '535$a': onwork.rename(rel=MARC+'locationOfOriginalsDuplicates'),
    '536$a': onwork.rename(rel=MARC+'fundingInformation'),
    '538$a': oninstance.rename(rel=MARC+'systemDetails'),
    '540$a': onwork.rename(rel=MARC+'termsGoverningUse'),
    '541$a': onwork.rename(rel=MARC+'immediateSourceOfAcquisition'),
    '542$a': onwork.rename(rel=MARC+'informationRelatingToCopyrightStatus'),
    '544$a': onwork.rename(rel=MARC+'locationOfOtherArchivalMaterial'),
    '545$a': onwork.rename(rel=MARC+'biographicalOrHistoricalData'),
    '546$a': onwork.rename(rel=MARC+'languageNote'),
    '547$a': onwork.rename(rel=MARC+'formerTitleComplexity'),
    '550$a': onwork.rename(rel=MARC+'issuingBody'),
    '552$a': onwork.rename(rel=MARC+'entityAndAttributeInformation'),
    '555$a': onwork.rename(rel=MARC+'cumulativeIndexFindingAids'),
    '556$a': onwork.rename(rel=MARC+'informationAboutDocumentation'),
    '561$a': oninstance.rename(rel=MARC+'ownership'),
    '580$a': onwork.rename(rel=BL+'note'),
    '583$a': onwork.rename(rel=MARC+'action'),
    '586$a': onwork.rename(rel=MARC+'AwardsNote'),


    # subjects
    # generate hash values only from all properties specific to Subjects
        
    '600': onwork.materialize(BL+'Person', 
                              BL+'subject', 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('f'), subfield('g'), subfield('h'), subfield('j'), subfield('k'), subfield('l'), subfield('m'), subfield('n'), subfield('o'), subfield('p'), subfield('q'), subfield('r'), subfield('s'), subfield('t'), subfield('u'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), MARC+'numeration': subfield('b'), MARC+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), MARC+'formSubdivision': subfield('v'), MARC+'generalSubdivision': subfield('x'), MARC+'chronologicalSubdivision': subfield('y'), MARC+'geographicSubdivision': subfield('z'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),

    '610': onwork.materialize(BL+'Organization', 
                              BL+'subject', 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('f'), subfield('g'), subfield('h'), subfield('k'), subfield('l'), subfield('m'), subfield('n'), subfield('o'), subfield('p'), subfield('r'), subfield('s'), subfield('t'), subfield('u'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), MARC+'subordinateUnit': subfield('b'), MARC+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), MARC+'formSubdivision': subfield('v'), MARC+'generalSubdivision': subfield('x'), MARC+'chronologicalSubdivision': subfield('y'), MARC+'geographicSubdivision': subfield('z'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),

    '611': onwork.materialize(BL+'Meeting', 
                              BL+'subject', 
                              unique=values(subfield('a'), subfield('c'), subfield('d'), subfield('e'), subfield('f'), subfield('g'), subfield('h'), subfield('k'), subfield('l'), subfield('n'), subfield('p'), subfield('q'), subfield('s'), subfield('t'), subfield('u'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), MARC+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), MARC+'formSubdivision': subfield('v'), MARC+'generalSubdivision': subfield('x'), MARC+'chronologicalSubdivision': subfield('y'), MARC+'geographicSubdivision': subfield('z'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),

    '630': onwork.materialize(BL+'Collection', 
                              BL+'subject', 
                              unique=all_subfields,
                              links={BL+'title': subfield('a'), BL+'language': subfield('l'), BL+'medium': subfield('h'), MARC+'nameOfPart': subfield('p'), MARC+'formSubdivision': subfield('v'), MARC+'generalSubdivision': subfield('x'), MARC+'chronologicalSubdivision': subfield('y'), MARC+'geographicSubdivision': subfield('z')}),

    '650': onwork.materialize(BL+'Topic', 
                              BL+'subject', 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), MARC+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), MARC+'formSubdivision': subfield('v'), MARC+'generalSubdivision': subfield('x'), MARC+'chronologicalSubdivision': subfield('y'), MARC+'geographicSubdivision': subfield('z'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),

    '651': onwork.materialize(BL+'Place', 
                              BL+'subject', 
                              unique=values(subfield('a'), subfield('g'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), BL+'date': subfield('d'), MARC+'formSubdivision': subfield('v'), MARC+'generalSubdivision': subfield('x'), MARC+'chronologicalSubdivision': subfield('y'), MARC+'geographicSubdivision': subfield('z'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),
    
    '655': onwork.materialize(BL+'Genre', 
                              BL+'genre', 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), MARC+'source': subfield('2'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),

    # Fields 700,710,711,etc. have a contributor + role (if specified) relationship to a new Agent object (only created as a new object if all subfields are unique)
    # Generate hash values only from the properties specific to Agents 
    # If there is a 700$t however this is an indication that there is a new Work. And yes, we're building a touring complete micro-language to address such patterns.

    '700': ifexists(subfield('t'),
                    onwork.materialize(BL+'Work', 
                                       values(REL+'hasPart', relator_property(subfield('i'), prefix=REL)),
                                       unique=values(subfield('t'), subfield('l'), subfield('m'), subfield('n'), subfield('o'), subfield('p'), subfield('r'), subfield('k'), subfield('f'), subfield('s')),
                                       links={BL+'title': subfield('t'), BL+'language': subfield('l'), AV+'musicMedium': subfield('m'), MARC+'titleNumber': subfield('n'), AV+'arrangedMusic': subfield('o'), MARC+'titlePart': subfield('p'), AV+'musicKey': subfield('r'), MARC+'form': subfield('k'), BL+'date': subfield('f'), MARC+'version': subfield('s'),
                                              ifexists(subfield('a'), BL+'creator'): materialize(BL+'Person', 
                                                                                                 unique=values(subfield('a')),
                                                                                                 links={BL+'name': subfield('a'), BL+'date': subfield('d')})
                                              }
                                       ),                   
                    onwork.materialize(BL+'Person', 
                                       values(BL+'contributor', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                                       unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')),
                                       links={BL+'name': subfield('a'), MARC+'numeration': subfield('b'), MARC+'titles': subfield('c'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))})
                    ),


    '710': ifexists(subfield('t'),
                    onwork.materialize(BL+'Work', 
                                       values(REL+'hasPart', relator_property(subfield('i'), prefix=REL)),
                                       unique=values(subfield('t'), subfield('l')),
                                       links={BL+'language': subfield('l'),
                                              ifexists(subfield('a'), BL+'creator'): materialize(BL+'Organization', 
                                                                                                 unique=values(subfield('a')),
                                                                                                 links={BL+'name': subfield('a'), BL+'date': subfield('d')}), 
                                              BL+'title': subfield('t'), BL+'language': subfield('l')}
                                       ),                   
                    onwork.materialize(BL+'Organization', 
                                       values(BL+'contributor', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                                       unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('g'), subfield('j'), subfield('q'), subfield('u')),
                                       links={BL+'name': subfield('a'), MARC+'subordinateUnit': subfield('b'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))})
                    ),

    
    '711': ifexists(subfield('t'),
                    onwork.materialize(BL+'Work', 
                                       values(REL+'hasPart', relator_property(subfield('i'), prefix=REL)),
                                       unique=values(subfield('t'), subfield('l')),
                                       links={BL+'language': subfield('l'),
                                              ifexists(subfield('a'), BL+'creator'): materialize(BL+'Meeting', 
                                                                                                 unique=values(subfield('a')),
                                                                                                 links={BL+'name': subfield('a'), BL+'date': subfield('d')}), 
                                              BL+'title': subfield('t'), BL+'language': subfield('l')}
                                       ),                   
                    onwork.materialize(BL+'Meeting', 
                                       values(BL+'contributor', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                                       unique=values(subfield('a'), subfield('c'), subfield('d'), subfield('e'), subfield('q'), subfield('u')),
                                       links={BL+'name': subfield('a'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))})
                    ),

    '720-1#': onwork.materialize(BL+'Person',
                                 values(BL+'contributor', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)),
                                 unique=values(subfield('a')),
                                 links={BL+'name': subfield('a')}),

    '720-##': onwork.materialize(BL+'Agent',
                                 values(BL+'contributor', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)),
                                 unique=values(subfield('a')),
                                 links={BL+'name': subfield('a')}),

    '730': onwork.materialize(BL+'Collection', 
                              BL+'related', 
                              unique=all_subfields,
                              links={BL+'title': subfield('a'), BL+'language': subfield('l'), BL+'medium': subfield('h'), MARC+'titlePart': subfield('p'), MARC+'titleNumber': subfield('n'), MARC+'formSubdivision': subfield('v'), MARC+'generalSubdivision': subfield('x'), MARC+'chronologicalSubdivision': subfield('y'), MARC+'geographicSubdivision': subfield('z')}),

    '740': onwork.materialize(BL+'Work', 
                              BL+'related', 
                              unique=values(subfield('a'), subfield('h'), subfield('n'), subfield('p')),
                              links={BL+'title': subfield('a'), MARC+'medium': subfield('h'), MARC+'titleNumber': subfield('n'), MARC+'titlePart': subfield('p')}),

    # Translation(s)
    
    '765':  onwork.materialize(BL+'Work', 
                               REL+'isTranslationOf', 
                               unique=all_subfields, 
                               links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '767':  onwork.materialize(BL+'Work', 
                               REL+'hasTranslation', 
                               unique=all_subfields, 
                               links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    # Preceding Entry

    '780-?0': onwork.materialize(BL+'Work', 
                                 REL+'continues', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '780-?1': onwork.materialize(BL+'Work', 
                                 REL+'continuesInPart', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '780-?2': onwork.materialize(BL+'Work', 
                                 REL+'supersedes', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '780-?3': onwork.materialize(BL+'Work', 
                                 REL+'supersedesInPart', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '780-?4': onwork.materialize(BL+'Work', 
                                 REL+'unionOf', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '780-?5': onwork.materialize(BL+'Work', 
                                 REL+'absorbed', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '780-?6': onwork.materialize(BL+'Work', 
                                 REL+'absorbedInPart', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '780-?7': onwork.materialize(BL+'Work', 
                                 REL+'separatedFrom', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    # Succeeding Entry

    '785-?0': onwork.materialize(BL+'Work', 
                                 REL+'continuedBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '785-?1': onwork.materialize(BL+'Work', 
                                 REL+'continuedInPartBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '785-?2': onwork.materialize(BL+'Work', 
                                 REL+'supersededBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '785-?3': onwork.materialize(BL+'Work', 
                                 REL+'supersededInPartBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '785-?4': onwork.materialize(BL+'Work', 
                                 REL+'absorbedBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '785-?5': onwork.materialize(BL+'Work', 
                                 REL+'absorbedInPartBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '785-?6': onwork.materialize(BL+'Work', 
                                 REL+'splitInto', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '785-?7': onwork.materialize(BL+'Work', 
                                 REL+'mergedWith', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    '785-?8': onwork.materialize(BL+'Work', 
                                 REL+'changedBackTo', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    # Other related works

    '787': onwork.materialize(BL+'Work', 
                              REL+'related', 
                              unique=all_subfields, 
                              links={BL+'title': subfield('t'), MARC+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), MARC+'edition': subfield('b'), BL+'note': subfield('n'), MARC+'edition': subfield('b'), MARC+'isbn': subfield('z')}),

    # Series

    '830': onwork.materialize(MARC+'Series', 
                              BL+'memberOf', 
                              unique=values(subfield('a')),
                              links={BL+'title': subfield('a'), MARC+'titleRemainder': subfield('k'), MARC+'volume': subfield('v'), MARC+'titleNumber': subfield('n'), MARC+'titlePart': subfield('p'), }),

    '856$u': oninstance.rename(rel=BL+'link', res=True),

    }

register_transforms("http://bibfra.me/tool/pybibframe/transforms#bflite", BFLITE_TRANSFORMS)

MARC_TRANSFORMS = {
    #HeldItem is a refinement of Annotation
    '852': oninstance.materialize(BL+'Annotation', 
                                  BA+'institution', 
                                  unique=all_subfields, 
                                  links={BA+'holderType': BA+'Library', BA+'location': subfield('a'), BA+'subLocation': subfield('b'), BA+'callNumber': subfield('h'), BA+'code': subfield('n'), BL+'link': subfield('u'), BA+'streetAddress': subfield('e')}),
}

register_transforms("http://bibfra.me/tool/pybibframe/transforms#marc", MARC_TRANSFORMS)

#XXX This might instead be a job for collections.ChainMap
TRANSFORMS = {}
TRANSFORMS.update(BFLITE_TRANSFORMS)
TRANSFORMS.update(MARC_TRANSFORMS)

