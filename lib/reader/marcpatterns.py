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

#    '100': onwork.materialize('Agent', 'creator', unique=all_subfields, mr_properties={'a': 'label'}),

# where do we put LDR info, e.g. LDR 07 / 19 positions = mode of issuance
#Don't do a simple field renaming of ISBN because

TRANSFORMS = {
    #Link to the 010a value, naming the relationship 'lccn'
    '010$a': onwork.rename(rel='lccn'),
    '017$a': onwork.rename(rel='legalDeposit'),
    #ISBN is specially processed
    #'020$a': oninstance.rename(rel='isbn'),
    '022$a': oninstance.rename(rel='issn'),
    '024$a': onwork.rename(rel='otherControlNumber'),
    '025$a': onwork.rename(rel='lcOverseasAcq'),

    '034$a': onwork.rename(rel='cartographicMathematicalDataScaleStatement'),  #Rebecca & Sally suggested this should effectively be a merge with 034a
    '034$b': onwork.rename(rel='cartographicMathematicalDataProjectionStatement'),
    '034$c': onwork.rename(rel='cartographicMathematicalDataCoordinateStatement'),
    '035$a': onwork.rename(rel='systemControlNumber'),
    '037$a': onwork.rename(rel='stockNumber'),

    '040$a': onwork.rename(rel='catalogingSource'),
    '041$a': onwork.rename(rel='language'),
    '050$a': onwork.rename(rel='lcCallNumber'),
    '050$b': onwork.rename(rel='lcItemNumber'),
    '050$3': onwork.rename(rel='material'),
    '060$a': onwork.rename(rel='nlmCallNumber'),
    '060$b': onwork.rename(rel='nlmItemNumber'),
    '061$a': onwork.rename(rel='nlmCopyStatement'),
    '070$a': onwork.rename(rel='nalCallNumber'),
    '070$b': onwork.rename(rel='nalItemNumber'),
    '071$a': onwork.rename(rel='nalCopyStatement'),
    '082$a': onwork.rename(rel='deweyNumber'),

    # Fields 100,110,111,etc. have a creator + role (if available) relationship to a new Agent object (only created as a new object if all subfields are unique)
    # generate hash values only from the properties specific to Agents 

    '100': onwork.materialize('Person', 
                              values('creator', normalizeparse(subfield('e')), normalizeparse(subfield('4'))), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')), 
                              mr_properties={'name': subfield('a'), 'numeration': subfield('b'), 'titles': subfield('c'), 'date': subfield('d'), 'hasAuthorityLink': subfield('0')}),

    '110': onwork.materialize('Organization', 
                              values('creator', normalizeparse(subfield('e')), normalizeparse(subfield('4'))), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')), 
                              mr_properties={'name': subfield('a'), 'subordinateUnit': subfield('b'), 'date': subfield('d'), 'hasAuthorityLink': subfield('0')}),

    '111': onwork.materialize('Meeting', 
                              values('creator', normalizeparse(subfield('e')), normalizeparse(subfield('4'))), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('d'), subfield('g'), subfield('j'), subfield('q'), subfield('u')), 
                              mr_properties={'name': subfield('a'), 'date': subfield('d'), 'hasAuthorityLink': subfield('0')}),

    '210$a': oninstance.rename(rel='abbreviatedTitle'),
    '222$a': oninstance.rename(rel='keyTitle'),

    '240': onwork.materialize('Collection', 
                              'memberOf', 
                              unique=values(subfield('a'), subfield('h'), subfield('k'), subfield('l'), subfield('m'), subfield('s')), 
                              mr_properties={'title': subfield('a'), 'legalDate': subfield('d'), 'medium': subfield('h'), 'musicMedium': subfield('m'), 'musicKey': subfield('r')}),
    
    '243': onwork.materialize('Collection', 
                              'memberOf', 
                              unique=values(subfield('a'), subfield('h'), subfield('k'), subfield('l'), subfield('m'), subfield('s')), 
                              mr_properties={'title': subfield('a'), 'legalDate': subfield('d'), 'medium': subfield('h'), 'musicMedium': subfield('m'), 'musicKey': subfield('r')}),

    '245$a': (onwork.rename(rel='title'), oninstance.rename(rel='title')),
    '245$b': onwork.rename(rel='subtitle'),
    '245$c': onwork.rename(rel='titleStatement'),
    '245$f': onwork.rename(rel='inclusiveDates'),
    '245$h': onwork.rename(rel='medium'),
    '245$k': onwork.rename(rel='formDesignation'),
    '246$a': onwork.rename(rel='titleVariation'),
    '246$f': onwork.rename(rel='titleVariationDate'),
    '247$a': onwork.rename(rel='formerTitle'),
    '250$a': oninstance.rename(rel='edition'),
    '250$b': oninstance.rename(rel='edition'),
    '254$a': oninstance.rename(rel='musicalPresentation'),
    '255$a': oninstance.rename(rel='cartographicMathematicalDataScaleStatement'),
    '255$b': oninstance.rename(rel='cartographicMathematicalDataProjectionStatement'),
    '255$c': oninstance.rename(rel='cartographicMathematicalDataCoordinateStatement'),
    '256$a': oninstance.rename(rel='computerFilecharacteristics'),

    # Provider materialization 

    '260': oninstance.materialize('ProviderEvent', 
                                  'publication', 
                                  unique=all_subfields, 
                                  mr_properties={ifexists(subfield('a'), 'providerPlace'): materialize('Place', unique=subfield('a'), mr_properties={'name': subfield('a')}), 
                                                 ifexists(subfield('b'), 'providerAgent'): materialize('Agent', unique=subfield('b'), mr_properties={'name': subfield('b')}), 
                                                 'providerDate': subfield('c')}),

    '264': oninstance.materialize('ProviderEvent', 
                                  'publication', 
                                  unique=all_subfields, 
                                  mr_properties={ifexists(subfield('a'), 'providerPlace'): materialize('Place', unique=subfield('a'), mr_properties={'name': subfield('a')}), 
                                                 ifexists(subfield('b'), 'providerAgent'): materialize('Agent', unique=subfield('b'), mr_properties={'name': subfield('b')}), 
                                                 'providerDate': subfield('c')}),

    #Ind1 is blank ('#') ind2 is 3

    '264$c-#4': oninstance.rename(rel='copyrightDate'),

    '264-#3': oninstance.materialize('ProviderEvent', 
                                     'manufacture', 
                                     unique=all_subfields, 
                                     mr_properties={ifexists(subfield('a'), 'providerPlace'): materialize('Place', unique=subfield('a'), mr_properties={'name': subfield('a')}), 
                                                    ifexists(subfield('b'), 'providerAgent'): materialize('Agent', unique=subfield('b'), mr_properties={'name': subfield('b')}), 
                                                    'providerDate': subfield('c')}),

    '264-#2': oninstance.materialize('ProviderEvent', 
                                     'distribution', 
                                     unique=all_subfields, 
                                     mr_properties={ifexists(subfield('a'), 'providerPlace'): materialize('Place', unique=subfield('a'), mr_properties={'name': subfield('a')}), 
                                                    ifexists(subfield('b'), 'providerAgent'): materialize('Agent', unique=subfield('b'), mr_properties={'name': subfield('b')}), 
                                                    'providerDate': subfield('c')}),

    '264-#1': oninstance.materialize('ProviderEvent', 
                                     'publication', 
                                     unique=all_subfields, 
                                     mr_properties={ifexists(subfield('a'), 'providerPlace'): materialize('Place', unique=subfield('a'), mr_properties={'name': subfield('a')}), 
                                                    ifexists(subfield('b'), 'providerAgent'): materialize('Agent', unique=subfield('b'), mr_properties={'name': subfield('b')}), 
                                                    'providerDate': subfield('c')}),

    '264-#0': oninstance.materialize('ProviderEvent', 
                                     'production', 
                                     unique=all_subfields, 
                                     mr_properties={ifexists(subfield('a'), 'providerPlace'): materialize('Place', unique=subfield('a'), mr_properties={'name': subfield('a')}), 
                                                    ifexists(subfield('b'), 'providerAgent'): materialize('Agent', unique=subfield('b'), mr_properties={'name': subfield('b')}), 
                                                    'providerDate': subfield('c')}),

    '300$a': oninstance.rename(rel='extent'),
    '300$b': oninstance.rename(rel='otherPhysicalDetails'),
    '300$c': oninstance.rename(rel='dimensions'),
    '300$e': oninstance.rename(rel='accompanyingMaterial'),
    '300$f': oninstance.rename(rel='typeOfunit'),
    '300$g': oninstance.rename(rel='size'),
    '300$3': oninstance.rename(rel='materials'),
    '310$a': oninstance.rename(rel='publicationFrequency'),
    '310$b': oninstance.rename(rel='publicationDateFrequency'),
    '336$a': onwork.rename(rel='contentCategory'),
    '336$b': onwork.rename(rel='contentTypeCode'),
    '336$2': onwork.rename(rel='contentTypeRDAsource'),
    '337$a': onwork.rename(rel='mediaCategory'),
    '337$b': onwork.rename(rel='mediaTypeCode'),
    '337$2': onwork.rename(rel='medaiRDAsource'),
    '338$a': onwork.rename(rel='carrierCategory'),
    '338$b': onwork.rename(rel='carrierCategoryCode'),
    '338$2': onwork.rename(rel='carrierRDASource'),
    '340$a': oninstance.rename(rel='physicalSubstance'),
    '340$b': oninstance.rename(rel='dimensions'),
    '340$c': oninstance.rename(rel='materialsApplied'),
    '340$d': oninstance.rename(rel='recordingTechnique'),
    '340$e': oninstance.rename(rel='physicalSupport'),
    '351$a': oninstance.rename(rel='organizationMethod'),
    '351$b': oninstance.rename(rel='arrangement'),
    '351$c': oninstance.rename(rel='hierarchy'),
    '351$3': oninstance.rename(rel='materialsSpec'),

# let's make some music! 
#
#    '382$a': onwork.materialize('Medium', 
#                                'performanceMedium', 
#                                unique=values(subfield('a')), 
#                                mr_properties={'name': subfield('a')}),
#
#    '382$b': onwork.materialize('Medium', 
#                                'featuredMedium', 
#                                unique=values(subfield('b')), 
#                                mr_properties={'name': subfield('b')}),
#
#    '382$p': onwork.materialize('Medium', 
#                                'alternativeMedium', 
#                                unique=values(subfield('f')), 
#                                mr_properties={'name': subfield('f')}),
#

    '382$a': onwork.rename(rel='performanceMedium'),
    '382$b': onwork.rename(rel='featuredMedium'),
    '382$p': onwork.rename(rel='alternativeMedium'),

    '382$s': onwork.rename(rel='numberOfPerformers'),
    '382$v': onwork.rename(rel='mediumNote'),

    '490$a': onwork.rename(rel='seriesStatement'),
    '490$v': onwork.rename(rel='seriesVolume'),

    '500$a': onwork.rename(rel='note'),
    '501$a': onwork.rename(rel='note'),
    '502$a': onwork.rename(rel='dissertationNote'),
    '502$b': onwork.rename(rel='degree'),
    '502$c': onwork.rename(rel='grantingInstitution'),
    '502$d': onwork.rename(rel='dissertationYear'),
    '502$g': onwork.rename(rel='dissertationNote'),
    '502$o': onwork.rename(rel='dissertationID'),
    '504$a': onwork.rename(rel='bibliographyNote'),
    '505$a': oninstance.rename(rel='contentsNote'),
    '506$a': oninstance.rename(rel='governingAccessNote'),
    '506$b': oninstance.rename(rel='jurisdictionNote'),
    '506$c': oninstance.rename(rel='physicalAccess'),
    '506$d': oninstance.rename(rel='authorizedUsers'),
    '506$e': oninstance.rename(rel='authorization'),
    '506$u': oninstance.rename(rel='uriNote'),
    '507$a': oninstance.rename(rel='representativeFractionOfScale'),
    '507$b': oninstance.rename(rel='remainderOfScale'),
    '508$a': oninstance.rename(rel='creditsNote'),
    '510$a': onwork.rename(rel='citationSource'),
    '510$b': onwork.rename(rel='citationCoverage'),
    '510$c': onwork.rename(rel='citationLocationWithinSource'),
    '510$u': onwork.rename(rel='citationUri'),
    '511$a': onwork.rename(rel='performerNote'),
    '513$a': onwork.rename(rel='typeOfReport'),
    '513$b': onwork.rename(rel='periodCoveredn'),
    '514$a': onwork.rename(rel='dataQuality'),
    '515$a': oninstance.rename(rel='numberingPerculiarities'),
    '516$a': oninstance.rename(rel='typeOfComputerFile'),
    '518$a': onwork.rename(rel='dateTimePlace'),
    '518$d': onwork.rename(rel='dateOfEvent'),
    '518$o': onwork.rename(rel='otherEventInformation'),
    '518$p': onwork.rename(rel='placeOfEvent'),
    '520$a': onwork.rename(rel='summary'),
    '520$b': onwork.rename(rel='summaryExpansion'),
    '520$c': onwork.rename(rel='assigningSource'),
    '520$u': onwork.rename(rel='summaryURI'),
    '521$a': onwork.rename(rel='intendedAudience'),
    '521$b': onwork.rename(rel='intendedAudienceSource'),
    '522$a': onwork.rename(rel='geograhpicCoverage'),
    '525$a': oninstance.rename(rel='supplement'),
    '526$a': onwork.rename(rel='studyProgramName'),
    '526$b': onwork.rename(rel='interestLevel'),
    '526$c': onwork.rename(rel='readingLevel'),
    '530$a': oninstance.rename(rel='additionalPhysicalForm'),
    '533$a': onwork.rename(rel='reproductionNote'),
    '534$a': onwork.rename(rel='originalVersionNote'),
    '535$a': onwork.rename(rel='locationOfOriginalsDuplicates'),
    '536$a': onwork.rename(rel='fundingInformation'),
    '538$a': oninstance.rename(rel='systemDetails'),
    '540$a': onwork.rename(rel='termsGoverningUse'),
    '541$a': onwork.rename(rel='immediateSourceOfAcquisition'),
    '542$a': onwork.rename(rel='informationRelatingToCopyrightStatus'),
    '544$a': onwork.rename(rel='locationOfOtherArchivalMaterial'),
    '545$a': onwork.rename(rel='biographicalOrHistoricalData'),
    '546$a': onwork.rename(rel='languageNote'),
    '547$a': onwork.rename(rel='formerTitleComplexity'),
    '550$a': onwork.rename(rel='issuingBody'),
    '552$a': onwork.rename(rel='entityAndAttributeInformation'),
    '555$a': onwork.rename(rel='cumulativeIndexFindingAids'),
    '556$a': onwork.rename(rel='informationAboutDocumentation'),
    '561$a': oninstance.rename(rel='ownership'),
    '583$a': onwork.rename(rel='action'),

    # subjects
    # generate hash values only from all properties specific to Subjects
    
    
    '600': onwork.materialize('Person', 
                              'subject', 
                              unique=all_subfields,
                              mr_properties={'name': subfield('a'), 'numeration': subfield('b'), 'locationOfEvent': subfield('c'), 'date': subfield('d'), 'formSubdivision': subfield('v'), 'generalSubdivision': subfield('x'), 'chronologicalSubdivision': subfield('y'), 'geographicSubdivision': subfield('z'), 'hasAuthorityLink': subfield('0')}),

    '610': onwork.materialize('Organization', 
                              'subject', 
                              unique=all_subfields, 
                              mr_properties={'name': subfield('a'), 'subordinateUnit': subfield('b'), 'locationOfEvent': subfield('c'), 'date': subfield('d'), 'formSubdivision': subfield('v'), 'generalSubdivision': subfield('x'), 'chronologicalSubdivision': subfield('y'), 'geographicSubdivision': subfield('z'), 'hasAuthorityLink': subfield('0')}),

    '611': onwork.materialize('Meeting', 
                              'subject', 
                              unique=all_subfields, 
                              mr_properties={'name': subfield('a'), 'locationOfEvent': subfield('c'), 'date': subfield('d'), 'formSubdivision': subfield('v'), 'generalSubdivision': subfield('x'), 'chronologicalSubdivision': subfield('y'), 'geographicSubdivision': subfield('z'), 'hasAuthorityLink': subfield('0')}),

    #'610$d': onwork.rename(rel='date'),  #Note: there has been discussion about removing this, but we are not sure we get reliable ID.LOC lookups without it.  If it is removed, update augment.py

    '630': onwork.materialize('Title', 
                              'uniformTitle', 
                              unique=all_subfields,
                              mr_properties={'uniformTitle': subfield('a'), 'language': subfield('l'), 'medium': subfield('h'), 'formSubdivision': subfield('v'), 'generalSubdivision': subfield('x'), 'chronologicalSubdivision': subfield('y'), 'geographicSubdivision': subfield('z')}),

    '650': onwork.materialize('Topic', 
                              'subject', 
                              unique=all_subfields, 
                              mr_properties={'name': subfield('a'), 'locationOfEvent': subfield('c'), 'date': subfield('d'), 'formSubdivision': subfield('v'), 'generalSubdivision': subfield('x'), 'chronologicalSubdivision': subfield('y'), 'geographicSubdivision': subfield('z'), 'hasAuthorityLink': subfield('0')}),

    '651': onwork.materialize('Place', 
                              'subject', 
                              unique=all_subfields, 
                              mr_properties={'name': subfield('a'), 'date': subfield('d'), 'formSubdivision': subfield('v'), 'generalSubdivision': subfield('x'), 'chronologicalSubdivision': subfield('y'), 'geographicSubdivision': subfield('z'), 'hasAuthorityLink': subfield('0')}),

    '655': onwork.materialize('Genre', 
                              'genre', 
                              unique=all_subfields, 
                              mr_properties={'name': subfield('a'), 'source': subfield('2'), 'hasAuthorityLink': subfield('0')}),

    # Fields 700,710,711,etc. have a contributor + role (if specified) relationship to a new Agent object (only created as a new object if all subfields are unique)
    # generate hash values only from the properties specific to Agents 

    '700': onwork.materialize('Person', 
                              values('contributor', normalizeparse(subfield('e')), normalizeparse(subfield('4'))), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('g'), subfield('j'), subfield('q'), subfield('u')), 
                              mr_properties={'name': subfield('a'), 'numeration': subfield('b'), 'titles': subfield('c'), 'date': subfield('d'), 'hasAuthorityLink': subfield('0')}),

    '710': onwork.materialize('Organization', 
                              values('contributor', normalizeparse(subfield('e')), normalizeparse(subfield('4'))), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('g'), subfield('j'), subfield('q'), subfield('u')), 
                              mr_properties={'name': subfield('a'), 'subordinateUnit': subfield('b'), 'date': subfield('d'), 'hasAuthorityLink': subfield('0')}),

    '711': onwork.materialize('Meeting', 
                              values('contributor', normalizeparse(subfield('e')), normalizeparse(subfield('4'))), 
                              unique=values(subfield('a'), subfield('c'), subfield('d'), subfield('e'), subfield('q'), subfield('u')), 
                              mr_properties={'name': subfield('a'), 'date': subfield('d'), 'hasAuthorityLink': subfield('0')}),

    '830': onwork.materialize('Series', 
                              'memberOf', 
                              unique=values(subfield('a')), 
                              mr_properties={'title': subfield('a'), 'subtitle': subfield('k'), 'volume': subfield('v'), 'number': subfield('n'), 'part': subfield('p'), }),

    #HeldItem is a refinement of Annotation
    '852': oninstance.materialize('HeldItem', 'institution', unique=all_subfields, mr_properties={'holderType': 'Library', 'location': subfield('a'), 'subLocation': subfield('b'), 'callNumber': subfield('h'), 'code': subfield('n'), 'link': subfield('u'), 'streetAddress': subfield('e')}),

    '880$a': onwork.rename(rel='title'),
    '856$u': oninstance.rename(rel='link', res=True),


    # RBMS partial profile (flesh this out and separate into a specialized marcpatterns.py file)

    '790': oninstance.materialize('Person', 
                              values('contributor', normalizeparse(subfield('e')), normalizeparse(subfield('4'))), 
                              unique=values(subfield('a'), subfield('b'), subfield('c'), subfield('g'), subfield('j'), subfield('q'), subfield('u')), 
                              mr_properties={'name': subfield('a'), 'numeration': subfield('b'), 'titles': subfield('c'), 'date': subfield('d'), 'hasAuthorityLink': subfield('0')}),
    
    '793': onwork.materialize('Collection', 
                              'memberOf', 
                              unique=values(subfield('a'), subfield('h'), subfield('k'), subfield('l'), subfield('m'), subfield('s')), 
                              mr_properties={'title': subfield('a'), 'legalDate': subfield('d'), 'medium': subfield('h'), 'musicMedium': subfield('m'), 'musicKey': subfield('r')}),

    '590$a': oninstance.rename(rel='note'),

}

