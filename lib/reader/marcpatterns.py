'''
Declarations used to elucidate MARC model
'''
#Just set up some flags
#BOUND_TO_WORK = object()
#BOUND_TO_INSTANCE = object()

#Full MARC field list: http://www.loc.gov/marc/bibliographic/ecbdlist.html

#This line must be included
from bibframe.reader.util import *

#from bibframe.reader.marcpatterns import *
#sorted([ (m, MATERIALIZE[m]) for m in MATERIALIZE if [ wf for wf in WORK_FIELDS if m[:2] == wf[:2]] ])

#    '100': onwork.materialize('Agent', 'creator', unique=all_subfields, links={'a': 'label'}),

# where do we put LDR info, e.g. LDR 07 / 19 positions = mode of issuance
#Don't do a simple field renaming of ISBN because

# Partitioning namespaces

BL = 'http://bibfra.me/vocab/lite/'
BA = 'http://bibfra.me/vocab/annotation/'
REL = 'http://bibfra.me/vocab/relation/'
RDA = 'http://bibfra.me/vocab/rda/'
RBMS = 'http://bibfra.me/vocab/rbms/'
AV = 'http://bibfra.me/vocab/audiovisual/'

BFLITE_TRANSFORMS = {
    #Link to the 010a value, naming the relationship 'lccn'
    '010$a': onwork.rename(rel=RDA+'lccn'),
    '017$a': onwork.rename(rel=RDA+'legalDeposit'),
    #ISBN is specially processed
    #'020$a': oninstance.rename(rel='isbn'),
    '022$a': oninstance.rename(rel=RDA+'issn'),
    '024$a': onwork.rename(rel=RDA+'otherControlNumber'),
    '025$a': onwork.rename(rel=RDA+'lcOverseasAcq'),

    '034$a': onwork.rename(rel=RDA+'cartographicMathematicalDataScaleStatement'),  #Rebecca & Sally suggested this should effectively be a merge with 034a
    '034$b': onwork.rename(rel=RDA+'cartographicMathematicalDataProjectionStatement'),
    '034$c': onwork.rename(rel=RDA+'cartographicMathematicalDataCoordinateStatement'),
    '035$a': onwork.rename(rel=RDA+'systemControlNumber'),
    '037$a': onwork.rename(rel=RDA+'stockNumber'),

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
                              links={BL+'name': subfield('a'), RDA+'numeration': subfield('b'), RDA+'titles': subfield('c'), BL+'date': subfield('d'), BL+'authorityLink': subfield('0')}),

    '110': onwork.materialize(BL+'Organization', 
                              values(BL+'creator', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')), 
                              links={BL+'name': subfield('a'), RDA+'subordinateUnit': subfield('b'), BL+'date': subfield('d'), BL+'authorityLink': subfield('0')}),

    '111': onwork.materialize(BL+'Meeting', 
                              values(BL+'creator', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')), 
                              links={BL+'name': subfield('a'), BL+'date': subfield('d'), BL+'authorityLink': subfield('0')}),

    '210$a': oninstance.rename(rel=RDA+'abbreviatedTitle'),
    '222$a': oninstance.rename(rel=RDA+'keyTitle'),

    '240': onwork.materialize(BL+'Collection', 
                              BL+'memberOf', 
                              unique=values(subfield('a'), subfield('h'), subfield('k'), subfield('l'), subfield('m'), subfield('s')), 
                              links={BL+'title': subfield('a'), RDA+'legalDate': subfield('d'), BL+'medium': subfield('h'), AV+'musicMedium': subfield('m'), AV+'musicKey': subfield('r')}),
    
    '243': onwork.materialize(BL+'Collection', 
                              BL+'memberOf', 
                              unique=values(subfield('a'), subfield('h'), subfield('k'), subfield('l'), subfield('m'), subfield('s')), 
                              links={BL+'title': subfield('a'), RDA+'legalDate': subfield('d'), BL+'medium': subfield('h'), AV+'musicMedium': subfield('m'), AV+'musicKey': subfield('r')}),

    # Title(s) - replicate across both Work and Instance(s) 

    '245$a': (onwork.rename(rel=BL+'title'), oninstance.rename(rel=BL+'title')),
    '245$b': (onwork.rename(rel=RDA+'titleRemainder'), oninstance.rename(rel=RDA+'titleRemainder')),
    '245$c': (onwork.rename(rel=RDA+'titleStatement'), oninstance.rename(rel=RDA+'titleStatement')),
    '245$n': (onwork.rename(rel=RDA+'titleNumber'), oninstance.rename(rel=RDA+'titleNumber')),
    '245$p': (onwork.rename(rel=RDA+'titleName'), oninstance.rename(rel=RDA+'titleName')),

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
                                  BL+'publication', 
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

    '300$a': oninstance.rename(rel=RDA+'extent'),
    '300$b': oninstance.rename(rel=RDA+'otherPhysicalDetails'),
    '300$c': oninstance.rename(rel=RDA+'dimensions'),
    '300$e': oninstance.rename(rel=RDA+'accompanyingMaterial'),
    '300$f': oninstance.rename(rel=RDA+'typeOfunit'),
    '300$g': oninstance.rename(rel=RDA+'size'),
    '300$3': oninstance.rename(rel=RDA+'materials'),
    '310$a': oninstance.rename(rel=RDA+'publicationFrequency'),
    '310$b': oninstance.rename(rel=RDA+'publicationDateFrequency'),
    '336$a': onwork.rename(rel=RDA+'contentCategory'),
    '336$b': onwork.rename(rel=RDA+'contentTypeCode'),
    '336$2': onwork.rename(rel=RDA+'contentTypeRDAsource'),
    '337$a': onwork.rename(rel=RDA+'mediaCategory'),
    '337$b': onwork.rename(rel=RDA+'mediaTypeCode'),
    '337$2': onwork.rename(rel=RDA+'medaiRDAsource'),
    '338$a': onwork.rename(rel=RDA+'carrierCategory'),
    '338$b': onwork.rename(rel=RDA+'carrierCategoryCode'),
    '338$2': onwork.rename(rel=RDA+'carrierRDASource'),
    '340$a': oninstance.rename(rel=RDA+'physicalSubstance'),
    '340$b': oninstance.rename(rel=RDA+'dimensions'),
    '340$c': oninstance.rename(rel=RDA+'materialsApplied'),
    '340$d': oninstance.rename(rel=RDA+'recordingTechnique'),
    '340$e': oninstance.rename(rel=RDA+'physicalSupport'),
    '351$a': oninstance.rename(rel=RDA+'organizationMethod'),
    '351$b': oninstance.rename(rel=RDA+'arrangement'),
    '351$c': oninstance.rename(rel=RDA+'hierarchy'),
    '351$3': oninstance.rename(rel=RDA+'materialsSpec'),

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

    '382$a': onwork.rename(rel=RDA+'performanceMedium'),
    '382$b': onwork.rename(rel=RDA+'featuredMedium'),
    '382$p': onwork.rename(rel=RDA+'alternativeMedium'),

    '382$s': onwork.rename(rel=RDA+'numberOfPerformers'),
    '382$v': onwork.rename(rel=RDA+'mediumNote'),

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
    '530$a': oninstance.rename(rel='additionalPhysicalForm'),
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
    '583$a': onwork.rename(rel=RDA+'action'),

    # subjects
    # generate hash values only from all properties specific to Subjects
        
    '600': onwork.materialize(BL+'Person', 
                              BL+'subject', 
                              unique=all_subfields,
                              links={BL+'name': subfield('a'), RDA+'numeration': subfield('b'), RDA+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z'), BL+'authorityLink': subfield('0')}),

    '610': onwork.materialize(BL+'Organization', 
                              BL+'subject', 
                              unique=all_subfields, 
                              links={BL+'name': subfield('a'), RDA+'subordinateUnit': subfield('b'), RDA+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z'), BL+'authorityLink': subfield('0')}),

    '611': onwork.materialize(BL+'Meeting', 
                              BL+'subject', 
                              unique=all_subfields, 
                              links={BL+'name': subfield('a'), RDA+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z'), BL+'authorityLink': subfield('0')}),
\
    '630': onwork.materialize(RDA+'Title', 
                              BL+'subject', 
                              unique=all_subfields,
                              links={BL+'name': subfield('a'), BL+'language': subfield('l'), BL+'medium': subfield('h'), RDA+'nameOfPart': subfield('p'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z')}),

    '650': onwork.materialize(BL+'Topic', 
                              BL+'subject', 
                              unique=all_subfields, 
                              links={BL+'name': subfield('a'), RDA+'locationOfEvent': subfield('c'), BL+'date': subfield('d'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z'), BL+'authorityLink': subfield('0')}),

    '651': onwork.materialize(BL+'Place', 
                              BL+'subject', 
                              unique=all_subfields, 
                              links={BL+'name': subfield('a'), BL+'date': subfield('d'), RDA+'formSubdivision': subfield('v'), RDA+'generalSubdivision': subfield('x'), RDA+'chronologicalSubdivision': subfield('y'), RDA+'geographicSubdivision': subfield('z'), BL+'authorityLink': subfield('0')}),

    '655': onwork.materialize(BL+'Genre', 
                              BL+'genre', 
                              unique=all_subfields, 
                              links={BL+'name': subfield('a'), RDA+'source': subfield('2'), BL+'authorityLink': subfield('0')}),

    # Fields 700,710,711,etc. have a contributor + role (if specified) relationship to a new Agent object (only created as a new object if all subfields are unique)
    # Generate hash values only from the properties specific to Agents 
    # If there is a 700$t however this is an indication that there is a new Work. And yes, we're building a touring complete micro-language to address such patterns.

    '700': ifexists(subfield('t'),
                    onwork.materialize(BL+'Work', 
                                       values(BL+'related', relator_property(subfield('i'), prefix=REL)),
                                       unique=values(subfield('t'), subfield('l')), 
                                       links={BL+'language': subfield('l'),
                                              ifexists(subfield('a'), BL+'creator'): materialize(BL+'Person', 
                                                                                                 unique=values(subfield('a')), 
                                                                                                 links={BL+'name': subfield('a'), BL+'date': subfield('d')}), 
                                              BL+'title': subfield('t'), BL+'language': subfield('l')}
                                   ),                   
                    onwork.materialize(BL+'Person', 
                                       values(BL+'contributor', relator_property(subfield('e'), prefix=REL), relator_property(subfield('4'), prefix=REL)), 
                                       unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('g'), subfield('j'), subfield('q'), subfield('u')), 
                                       links={BL+'name': subfield('a'), RDA+'numeration': subfield('b'), RDA+'titles': subfield('c'), BL+'date': subfield('d'), BL+'authorityLink': subfield('0')})
                    ),


    '710': ifexists(subfield('t'),
                    onwork.materialize(BL+'Work', 
                                       values(BL+ 'related', relator_property(subfield('i'), prefix=REL)),
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
                                       links={BL+'name': subfield('a'), RDA+'subordinateUnit': subfield('b'), BL+'date': subfield('d'), BL+'authorityLink': subfield('0')})
                    ),

    
    '711': ifexists(subfield('t'),
                    onwork.materialize(BL+'Work', 
                                       values(BL+'related', relator_property(subfield('i'), prefix=REL)),
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
                                       links={BL+'name': subfield('a'), BL+'date': subfield('d'), BL+'authorityLink': subfield('0')})
                    ),
    
    # Series

    '830': onwork.materialize(RDA+'Series', 
                              BL+'memberOf', 
                              unique=values(subfield('a')), 
                              links={BL+'title': subfield('a'), RDA+'subtitle': subfield('k'), RDA+'volume': subfield('v'), RDA+'number': subfield('n'), RDA+'part': subfield('p'), }),

    # '880$a' insert logic here

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

