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
                BL+'ProviderEvent', RDA+'publication',
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
from bibframe import BL, BA, REL, RDA, RBMS, AV
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
    '010$a': oninstance.rename(rel=RDA+'lccn'),
    '017$a': oninstance.rename(rel=RDA+'legalDeposit'),
    #ISBN is specially processed
    #'020$a': oninstance.rename(rel='isbn'),
    '022$a': oninstance.rename(rel=RDA+'issn'),
    '024$a': oninstance.rename(rel=RDA+'otherControlNumber'),
    '024$a-#1': oninstance.rename(rel=RDA+'upc'),
    '025$a': oninstance.rename(rel=RDA+'lcOverseasAcq'),

    '028$a': oninstance.rename(rel=RDA+'publisherNumber'),
    '028$a-#0': oninstance.rename(rel=RDA+'issueNumber'),
    '028$a-#2': oninstance.rename(rel=RDA+'plateNumber'),
    '028$a-#4': oninstance.rename(rel=RDA+'videoRecordingNumber'),    

    '034$a': oninstance.rename(rel=RDA+'cartographicMathematicalDataScaleStatement'),  #Rebecca & Sally suggested this should effectively be a merge with 034a
    '034$b': oninstance.rename(rel=RDA+'cartographicMathematicalDataProjectionStatement'),
    '034$c': oninstance.rename(rel=RDA+'cartographicMathematicalDataCoordinateStatement'),
    '035$a': oninstance.rename(rel=RDA+'systemControlNumber'),
    '037$a': oninstance.rename(rel=RDA+'stockNumber'),

    '040$a': onwork.rename(rel=RDA+'catalogingSource'),
    '041$a': onwork.rename(rel=BL+'language'),
    '050$a': onwork.rename(rel=RDA+'lcCallNumber'),
    '050$b': onwork.rename(rel=RDA+'lcItemNumber'),
    '050$3': onwork.rename(rel=BL+'material'),
    '060$a': onwork.rename(rel=RDA+'nlmCallNumber'),
    '060$b': onwork.rename(rel=RDA+'nlmItemNumber'),
    '061$a': onwork.rename(rel=RDA+'nlmCopyStatement'),
    '070$a': onwork.rename(rel=RDA+'nalCallNumber'),
    '070$b': onwork.rename(rel=RDA+'nalItemNumber'),
    '071$a': onwork.rename(rel=RDA+'nalCopyStatement'),
    '082$a': onwork.rename(rel=RDA+'deweyNumber'),

    # Fields 100,110,111,etc. have a creator + role (if available) relationship to a new Agent object (only created as a new object if all subfields are unique)
    # generate hash values only from the properties specific to Agents 

    '100': onwork.materialize(BL+'Person', 
                              values(BL+'creator', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')),
                              links={BL+'name': subfield('a'), RDA+'numeration': subfield('b'), RDA+'titles': subfield('c'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0')), RDA+'additionalName': subfield('q')}),

    '110': onwork.materialize(BL+'Organization', 
                              values(BL+'creator', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')),
                              links={BL+'name': subfield('a'), RDA+'subordinateUnit': subfield('b'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0')), RDA+'additionalName': subfield('q')}),

    '111': onwork.materialize(BL+'Meeting', 
                              values(BL+'creator', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')),
                              links={BL+'name': subfield('a'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0')), RDA+'additionalName': subfield('q')}),

    '210$a': oninstance.rename(rel=RDA+'abbreviatedTitle'),
    '222$a': oninstance.rename(rel=RDA+'keyTitle'),

    '240': onwork.materialize(BL+'Collection', 
                              BL+'memberOf', 
                              unique=values(subfield('a'), subfield('d'), subfield('h'), subfield('l'), subfield('m'), subfield('n'), subfield('o'), subfield('p'), subfield('r'), subfield('k'), subfield('f'), subfield('s')),
                              links={BL+'title': subfield('a'), RDA+'legalDate': subfield('d'), BL+'medium': subfield('h'), BL+'language': subfield('l'), AV+'musicMedium': subfield('m'), RDA+'titleNumber': subfield('n'), AV+'arrangedMusic': subfield('o'), RDA+'titlePart': subfield('p'), AV+'musicKey': subfield('r'), RDA+'form': subfield('k'), BL+'date': subfield('f'), RDA+'version': subfield('s')}),
    
    '243': onwork.materialize(BL+'Collection', 
                              BL+'memberOf', 
                              unique=values(subfield('a'), subfield('d'), subfield('h'), subfield('l'), subfield('m'), subfield('n'), subfield('o'), subfield('p'), subfield('r'), subfield('k'), subfield('f'), subfield('s')),
                              links={BL+'title': subfield('a'), RDA+'legalDate': subfield('d'), BL+'medium': subfield('h'), BL+'language': subfield('l'), AV+'musicMedium': subfield('m'), RDA+'titleNumber': subfield('n'), AV+'arrangedMusic': subfield('o'), RDA+'titlePart': subfield('p'), AV+'musicKey': subfield('r'), RDA+'form': subfield('k'), BL+'date': subfield('f'), RDA+'version': subfield('s')}),

    # Title(s) - replicate across both Work and Instance(s) 

    '245$a': (onwork.rename(rel=BL+'title'), oninstance.rename(rel=BL+'title')),
    '245$b': (onwork.rename(rel=RDA+'titleRemainder'), oninstance.rename(rel=RDA+'titleRemainder')),
    '245$c': (onwork.rename(rel=RDA+'titleStatement'), oninstance.rename(rel=RDA+'titleStatement')),
    '245$n': (onwork.rename(rel=RDA+'titleNumber'), oninstance.rename(rel=RDA+'titleNumber')),
    '245$p': (onwork.rename(rel=RDA+'titlePart'), oninstance.rename(rel=RDA+'titlePart')),

    '245$f': onwork.rename(rel=RDA+'inclusiveDates'),
    '245$h': onwork.rename(rel=BL+'medium'),
    '245$k': onwork.rename(rel=RDA+'formDesignation'),
    '246$a': onwork.rename(rel=RDA+'titleVariation'),
    '246$b': onwork.rename(rel=RDA+'titleVariationRemainder'),
    '246$f': onwork.rename(rel=RDA+'titleVariationDate'),
    '247$a': onwork.rename(rel=RDA+'formerTitle'),
    '250$a': oninstance.rename(rel=RDA+'edition'),
    '250$b': oninstance.rename(rel=RDA+'edition'),
    '254$a': oninstance.rename(rel=RDA+'musicalPresentation'),
    '255$a': oninstance.rename(rel=RDA+'cartographicMathematicalDataScaleStatement'),
    '255$b': oninstance.rename(rel=RDA+'cartographicMathematicalDataProjectionStatement'),
    '255$c': oninstance.rename(rel=RDA+'cartographicMathematicalDataCoordinateStatement'),
    '256$a': oninstance.rename(rel=RDA+'computerFilecharacteristics'),

    # Provider materialization 

    #'260': oninstance.materialize('ProviderEvent', 
    #                              'publication', 
    #                              unique=all_subfields, 
    #                              links={ifexists(subfield('a'), 'providerPlace'): materialize('Place', unique=subfield('a'), links={'name': subfield('a')}), 
    #                                             ifexists(subfield('b'), 'providerAgent'): materialize('Agent', unique=target(), links={'name': subfield('b')}), 
    #                                             'providerDate': subfield('c')}),
    
    '260': oninstance.materialize(BL+'ProviderEvent', 
                                  RDA+'publication', 
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
                                  RDA+'publication', 
                                  unique=all_subfields, 
                                  links={ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), 
                                                                                                  links={BL+'name': subfield('a')}), 
                                         ifexists(subfield('b'), BL+'providerAgent'): materialize(BL+'Agent', unique=subfield('b'), 
                                                                                                  links={BL+'name': subfield('b')}), BL+'providerDate': subfield('c')}
                                  ),

    #Ind1 is blank ('#') ind2 is 3

    '264$c-#4': oninstance.rename(rel=RDA+'copyrightDate'),

    '264-#3': oninstance.materialize(BL+'ProviderEvent', 
                                     RDA+'manufacture', 
                                     unique=all_subfields, 
                                     links={ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), 
                                                                                                     links={BL+'name': subfield('a')}), 
                                                    ifexists(subfield('b'), BL+'providerAgent'): materialize(BL+'Agent', unique=subfield('b'), 
                                                                                                             links={BL+'name': subfield('b')}), BL+'providerDate': subfield('c')}
                                     ),

    '264-#2': oninstance.materialize(BL+'ProviderEvent', 
                                     RDA+'distribution', 
                                     unique=all_subfields, 
                                     links={ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), 
                                                                                                     links={BL+'name': subfield('a')}), 
                                                    ifexists(subfield('b'), BL+'providerAgent'): materialize(BL+'Agent', unique=subfield('b'), 
                                                                                                             links={BL+'name': subfield('b')}), BL+'providerDate': subfield('c')}
                                     ),

    '264-#1': oninstance.materialize(BL+'ProviderEvent', 
                                     RDA+'publication', 
                                     unique=all_subfields, 
                                     links={ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), 
                                                                                                     links={BL+'name': subfield('a')}), 
                                                    ifexists(subfield('b'), 'providerAgent'): materialize(BL+'Agent', unique=subfield('b'), 
                                                                                                          links={BL+'name': subfield('b')}), BL+'providerDate': subfield('c')}
                                     ),

    '264-#0': oninstance.materialize(BL+'ProviderEvent', 
                                     RDA+'production', 
                                     unique=all_subfields, 
                                     links={ifexists(subfield('a'), BL+'providerPlace'): materialize(BL+'Place', unique=subfield('a'), 
                                                                                                     links={BL+'name': subfield('a')}), 
                                                    ifexists(subfield('b'), BL+'providerAgent'): materialize(BL+'Agent', unique=subfield('b'), 
                                                                                                             links={BL+'name': subfield('b')}), BL+'providerDate': subfield('c')}),

    '300$a': oninstance.rename(rel=BL+'extent'),
    '300$b': oninstance.rename(rel=RDA+'otherPhysicalDetails'),
    '300$c': oninstance.rename(rel=BL+'dimensions'),
    '300$e': oninstance.rename(rel=RDA+'accompanyingMaterial'),
    '300$f': oninstance.rename(rel=RDA+'typeOfunit'),
    '300$g': oninstance.rename(rel=RDA+'size'),
    '300$3': oninstance.rename(rel=RDA+'materials'),
    '310$a': oninstance.rename(rel=RDA+'publicationFrequency'),
    '310$b': oninstance.rename(rel=RDA+'publicationDateFrequency'),
    '336$a': oninstance.rename(rel=RDA+'contentCategory'),
    '336$b': oninstance.rename(rel=RDA+'contentTypeCode'),
    '336$2': oninstance.rename(rel=RDA+'contentTypeRDAsource'),
    '337$a': oninstance.rename(rel=RDA+'mediaCategory'),
    '337$b': oninstance.rename(rel=RDA+'mediaTypeCode'),
    '337$2': oninstance.rename(rel=RDA+'medaiRDAsource'),
    '338$a': oninstance.rename(rel=RDA+'carrierCategory'),
    '338$b': oninstance.rename(rel=RDA+'carrierCategoryCode'),
    '338$2': oninstance.rename(rel=RDA+'carrierRDASource'),
    '340$a': oninstance.rename(rel=RDA+'physicalSubstance'),
    '340$b': oninstance.rename(rel=RDA+'dimensions'),
    '340$c': oninstance.rename(rel=RDA+'materialsApplied'),
    '340$d': oninstance.rename(rel=RDA+'recordingTechnique'),
    '340$e': oninstance.rename(rel=RDA+'physicalSupport'),
    '351$a': oninstance.rename(rel=RDA+'organizationMethod'),
    '351$b': oninstance.rename(rel=RDA+'arrangement'),
    '351$c': oninstance.rename(rel=RDA+'hierarchy'),
    '351$3': oninstance.rename(rel=RDA+'materialsSpec'),

    '362$a': oninstance.rename(rel=RDA+'publicationDesignation'),



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

    '490$a': onwork.rename(rel=RDA+'seriesStatement'),
    '490$v': onwork.rename(rel=RDA+'seriesVolume'),

    '500$a': onwork.rename(rel=BL+'note'),
    '501$a': onwork.rename(rel=RDA+'note'),
    '502$a': onwork.rename(rel=RDA+'dissertationNote'),
    '502$b': onwork.rename(rel=RDA+'degree'),
    '502$c': onwork.rename(rel=RDA+'grantingInstitution'),
    '502$d': onwork.rename(rel=RDA+'dissertationYear'),
    '502$g': onwork.rename(rel=RDA+'dissertationNote'),
    '502$o': onwork.rename(rel=RDA+'dissertationID'),
    '504$a': onwork.rename(rel=RDA+'bibliographyNote'),

    '505$a': oninstance.rename(rel=RDA+'contentsNote'),

    '506$a': oninstance.rename(rel=RDA+'governingAccessNote'),
    '506$b': oninstance.rename(rel=RDA+'jurisdictionNote'),
    '506$c': oninstance.rename(rel=RDA+'physicalAccess'),
    '506$d': oninstance.rename(rel=RDA+'authorizedUsers'),
    '506$e': oninstance.rename(rel=RDA+'authorization'),
    '506$u': oninstance.rename(rel=RDA+'uriNote'),
    '507$a': oninstance.rename(rel=RDA+'representativeFractionOfScale'),
    '507$b': oninstance.rename(rel=RDA+'remainderOfScale'),
    '508$a': oninstance.rename(rel=RDA+'creditsNote'),
    '510$a': onwork.rename(rel=RDA+'citationSource'),
    '510$b': onwork.rename(rel=RDA+'citationCoverage'),
    '510$c': onwork.rename(rel=RDA+'citationLocationWithinSource'),
    '510$u': onwork.rename(rel=RDA+'citationUri'),
    '511$a': onwork.rename(rel=RDA+'performerNote'),
    '513$a': onwork.rename(rel=RDA+'typeOfReport'),
    '513$b': onwork.rename(rel=RDA+'periodCoveredn'),
    '514$a': onwork.rename(rel=RDA+'dataQuality'),
    '515$a': oninstance.rename(rel='RDA+numberingPerculiarities'),
    '516$a': oninstance.rename(rel=RDA+'typeOfComputerFile'),
    '518$a': onwork.rename(rel=RDA+'dateTimePlace'),
    '518$d': onwork.rename(rel=RDA+'dateOfEvent'),
    '518$o': onwork.rename(rel=RDA+'otherEventInformation'),
    '518$p': onwork.rename(rel=RDA+'placeOfEvent'),
    '520$a': onwork.rename(rel=RDA+'summary'),
    '520$b': onwork.rename(rel=RDA+'summaryExpansion'),
    '520$c': onwork.rename(rel=RDA+'assigningSource'),
    '520$u': onwork.rename(rel=RDA+'summaryURI'),
    '521$a': onwork.rename(rel=RDA+'intendedAudience'),
    '521$b': onwork.rename(rel=RDA+'intendedAudienceSource'),
    '522$a': onwork.rename(rel=RDA+'geograhpicCoverage'),
    '525$a': oninstance.rename(rel=RDA+'supplement'),
    '526$a': onwork.rename(rel=RDA+'studyProgramName'),
    '526$b': onwork.rename(rel=RDA+'interestLevel'),
    '526$c': onwork.rename(rel=RDA+'readingLevel'),
    '530$a': oninstance.rename(rel=RDA+'additionalPhysicalForm'),
    '533$a': onwork.rename(rel=RDA+'reproductionNote'),
    '534$a': onwork.rename(rel=RDA+'originalVersionNote'),
    '535$a': onwork.rename(rel=RDA+'locationOfOriginalsDuplicates'),
    '536$a': onwork.rename(rel=RDA+'fundingInformation'),
    '538$a': oninstance.rename(rel=RDA+'systemDetails'),
    '540$a': onwork.rename(rel=RDA+'termsGoverningUse'),
    '541$a': onwork.rename(rel=RDA+'immediateSourceOfAcquisition'),
    '542$a': onwork.rename(rel=RDA+'informationRelatingToCopyrightStatus'),
    '544$a': onwork.rename(rel=RDA+'locationOfOtherArchivalMaterial'),
    '545$a': onwork.rename(rel=RDA+'biographicalOrHistoricalData'),
    '546$a': onwork.rename(rel=RDA+'languageNote'),
    '547$a': onwork.rename(rel=RDA+'formerTitleComplexity'),
    '550$a': onwork.rename(rel=RDA+'issuingBody'),
    '552$a': onwork.rename(rel=RDA+'entityAndAttributeInformation'),
    '555$a': onwork.rename(rel=RDA+'cumulativeIndexFindingAids'),
    '556$a': onwork.rename(rel=RDA+'informationAboutDocumentation'),
    '561$a': oninstance.rename(rel=RDA+'ownership'),
    '580$a': onwork.rename(rel=BL+'note'),
    '583$a': onwork.rename(rel=RDA+'action'),
    '586$a': onwork.rename(rel=RDA+'AwardsNote'),


    # subjects
    # generate hash values only from all properties specific to Subjects
        
    '600': onwork.materialize(BL+'Person', 
                              BL+'subject', 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('f'), subfield('g'), subfield('h'), subfield('j'), subfield('k'), subfield('l'), subfield('m'), subfield('n'), subfield('o'), subfield('p'), subfield('q'), subfield('r'), subfield('s'), subfield('t'), subfield('u'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), RDA+'numeration': subfield('b'), RDA+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),

    '610': onwork.materialize(BL+'Organization', 
                              BL+'subject', 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('f'), subfield('g'), subfield('h'), subfield('k'), subfield('l'), subfield('m'), subfield('n'), subfield('o'), subfield('p'), subfield('r'), subfield('s'), subfield('t'), subfield('u'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), RDA+'subordinateUnit': subfield('b'), RDA+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),

    '611': onwork.materialize(BL+'Meeting', 
                              BL+'subject', 
                              unique=values(subfield('a'), subfield('c'), subfield('d'), subfield('e'), subfield('f'), subfield('g'), subfield('h'), subfield('k'), subfield('l'), subfield('n'), subfield('p'), subfield('q'), subfield('s'), subfield('t'), subfield('u'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), RDA+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),

    '630': onwork.materialize(BL+'Collection', 
                              BL+'subject', 
                              unique=all_subfields,
                              links={BL+'title': subfield('a'), BL+'language': subfield('l'), BL+'medium': subfield('h'), RDA+'nameOfPart': subfield('p'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z')}),

    '650': onwork.materialize(BL+'Topic', 
                              BL+'subject', 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), RDA+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),

    '651': onwork.materialize(BL+'Place', 
                              BL+'subject', 
                              unique=values(subfield('a'), subfield('g'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), BL+'date': subfield('d'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),
    
    '655': onwork.materialize(BL+'Genre', 
                              BL+'genre', 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('v'), subfield('x'), subfield('y'), subfield('z')),
                              links={BL+'name': subfield('a'), RDA+'source': subfield('2'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))}),

    # Fields 700,710,711,etc. have a contributor + role (if specified) relationship to a new Agent object (only created as a new object if all subfields are unique)
    # Generate hash values only from the properties specific to Agents 
    # If there is a 700$t however this is an indication that there is a new Work. And yes, we're building a touring complete micro-language to address such patterns.

    '700': ifexists(subfield('t'),
                    onwork.materialize(BL+'Work', 
                                       values(REL+'hasPart', relator_property(subfield('i'), prefix=REL)),
                                       unique=values(subfield('t'), subfield('l'), subfield('m'), subfield('n'), subfield('o'), subfield('p'), subfield('r'), subfield('k'), subfield('f'), subfield('s')),
                                       links={BL+'title': subfield('t'), BL+'language': subfield('l'), AV+'musicMedium': subfield('m'), RDA+'titleNumber': subfield('n'), AV+'arrangedMusic': subfield('o'), RDA+'titlePart': subfield('p'), AV+'musicKey': subfield('r'), RDA+'form': subfield('k'), BL+'date': subfield('f'), RDA+'version': subfield('s'),
                                              ifexists(subfield('a'), BL+'creator'): materialize(BL+'Person', 
                                                                                                 unique=values(subfield('a')),
                                                                                                 links={BL+'name': subfield('a'), BL+'date': subfield('d')})
                                              }
                                       ),                   
                    onwork.materialize(BL+'Person', 
                                       values(BL+'contributor', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                                       unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')),
                                       links={BL+'name': subfield('a'), RDA+'numeration': subfield('b'), RDA+'titles': subfield('c'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))})
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
                                       links={BL+'name': subfield('a'), RDA+'subordinateUnit': subfield('b'), BL+'date': subfield('d'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('0'))})
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

    '720': onwork.materialize(BL+'Agent',
                              values(BL+'contributor', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)),
                              unique=values(subfield('a')),
                              links={BL+'name': subfield('a')}),

    '730': onwork.materialize(BL+'Collection', 
                              BL+'related', 
                              unique=all_subfields,
                              links={BL+'title': subfield('a'), BL+'language': subfield('l'), BL+'medium': subfield('h'), RDA+'titlePart': subfield('p'), RDA+'titleNumber': subfield('n'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z')}),

    '740': onwork.materialize(BL+'Work', 
                              BL+'related', 
                              unique=values(subfield('a'), subfield('h'), subfield('n'), subfield('p')),
                              links={BL+'title': subfield('a'), RDA+'medium': subfield('h'), RDA+'titleNumber': subfield('n'), RDA+'titlePart': subfield('p')}),

    # Translation(s)
    
    '765':  onwork.materialize(BL+'Work', 
                               REL+'isTranslationOf', 
                               unique=all_subfields, 
                               links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '767':  onwork.materialize(BL+'Work', 
                               REL+'hasTranslation', 
                               unique=all_subfields, 
                               links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    # Preceding Entry

    '780-?0': onwork.materialize(BL+'Work', 
                                 REL+'continues', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '780-?1': onwork.materialize(BL+'Work', 
                                 REL+'continuesInPart', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '780-?2': onwork.materialize(BL+'Work', 
                                 REL+'supersedes', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '780-?3': onwork.materialize(BL+'Work', 
                                 REL+'supersedesInPart', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '780-?4': onwork.materialize(BL+'Work', 
                                 REL+'unionOf', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '780-?5': onwork.materialize(BL+'Work', 
                                 REL+'absorbed', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '780-?6': onwork.materialize(BL+'Work', 
                                 REL+'absorbedInPart', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '780-?7': onwork.materialize(BL+'Work', 
                                 REL+'separatedFrom', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    # Succeeding Entry

    '785-?0': onwork.materialize(BL+'Work', 
                                 REL+'continuedBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '785-?1': onwork.materialize(BL+'Work', 
                                 REL+'continuedInPartBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '785-?2': onwork.materialize(BL+'Work', 
                                 REL+'supersededBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '785-?3': onwork.materialize(BL+'Work', 
                                 REL+'supersededInPartBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '785-?4': onwork.materialize(BL+'Work', 
                                 REL+'absorbedBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '785-?5': onwork.materialize(BL+'Work', 
                                 REL+'absorbedInPartBy', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '785-?6': onwork.materialize(BL+'Work', 
                                 REL+'splitInto', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '785-?7': onwork.materialize(BL+'Work', 
                                 REL+'mergedWith', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    '785-?8': onwork.materialize(BL+'Work', 
                                 REL+'changedBackTo', 
                                 unique=all_subfields, 
                                 links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    # Other related works

    '787': onwork.materialize(BL+'Work', 
                              REL+'related', 
                              unique=all_subfields, 
                              links={BL+'title': subfield('t'), RDA+'issn': subfield('x'), BL+'authorityLink': replace_from(AUTHORITY_CODES, subfield('w')), RDA+'edition': subfield('b'), BL+'note': subfield('n'), RDA+'edition': subfield('b'), RDA+'isbn': subfield('z')}),

    # Series

    '830': onwork.materialize(RDA+'Series', 
                              BL+'memberOf', 
                              unique=values(subfield('a')),
                              links={BL+'title': subfield('a'), RDA+'titleRemainder': subfield('k'), RDA+'volume': subfield('v'), RDA+'titleNumber': subfield('n'), RDA+'titlePart': subfield('p'), }),

    '856$u': oninstance.rename(rel=BL+'link', res=True),

    }

register_transforms("http://bibfra.me/tool/pybibframe/transforms#bflite", BFLITE_TRANSFORMS)

MARC_TRANSFORMS = {
    #HeldItem is a refinement of Annotation
    '852': oninstance.materialize(BL+'Annotation', BA+'institution', unique=all_subfields, links={BA+'holderType': BA+'Library', BA+'location': subfield('a'), BA+'subLocation': subfield('b'), BA+'callNumber': subfield('h'), BA+'code': subfield('n'), BL+'link': subfield('u'), BA+'streetAddress': subfield('e')}),
}

register_transforms("http://bibfra.me/tool/pybibframe/transforms#marc", MARC_TRANSFORMS)

#XXX This might instead be a job for collections.ChainMap
TRANSFORMS = {}
TRANSFORMS.update(BFLITE_TRANSFORMS)
TRANSFORMS.update(MARC_TRANSFORMS)

