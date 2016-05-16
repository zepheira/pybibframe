# -*- coding: utf-8 -*-
'''
'''
# These two lines are required at the top
from bibframe import BL, BA, REL, MARC, RBMS, AV
from bibframe.reader.util import *
from . import VTYPE_REL

LL = 'http://library.link/vocab/'

WORK_HASH_TRANSFORMS = {
    # Key creator info
    '100$a': onwork.link(rel=LL + 'creatorName'),
    '100$d': onwork.link(rel=LL + 'creatorDate'),

    '110$a': onwork.link(rel=BL + 'organizationName'),
    '110$d': onwork.link(rel=BL + 'organizationDate'),

    '111$a': onwork.link(rel=BL + 'meetingName'),
    '111$d': onwork.link(rel=BL + 'meetingDate'),

    '130$a': onwork.link(rel=BL + 'collectionName'),

    # key uniform title info
    '240a': oninstance.link(rel=LL + 'collectionTitle'),
    # '240f': oninstance.link(rel=LL + 'collectionDate'),
    # '240n': oninstance.link(rel=LL + 'collectionPartCount'),
    # '240o': oninstance.link(rel=LL + 'collectionMusicArrangement'),
    # '240p': oninstance.link(rel=LL + 'collectionPartName'),
    # '240l': oninstance.link(rel=LL + 'collectionLanguage'),

    # Title info
    '245$a': onwork.link(rel=BL + 'title'),
    '245$b': onwork.link(rel=MARC + 'titleRemainder'),
    '245$c': onwork.link(rel=MARC + 'titleStatement'),
    '245$n': onwork.link(rel=MARC + 'titleNumber'),
    '245$p': onwork.link(rel=MARC + 'titlePart'),
    '245$f': onwork.link(rel=MARC + 'inclusiveDates'),
    '245$k': onwork.link(rel=MARC + 'formDesignation'),

    # Title variation info
    '246$a': onwork.link(rel=MARC + 'titleVariation'),
    '246$b': onwork.link(rel=MARC + 'titleVariationRemainder'),
    '246$f': onwork.link(rel=MARC + 'titleVariationDate'),

    # # Key edition info
    # '250$a': onwork.link(rel=MARC + 'edition'),
    # '250$b': onwork.link(rel=MARC + 'edition'),

    # Key subject info
    '600$a': onwork.link(rel=LL + 'subjectName'),
    '610$a': onwork.link(rel=LL + 'subjectName'),
    '611$a': onwork.link(rel=LL + 'subjectName'),
    '650$a': onwork.link(rel=LL + 'subjectName'),
    '651$a': onwork.link(rel=LL + 'subjectName'),

    # Key contributor info
    '700$a': onwork.link(rel=LL + 'relatedWorkOrContributorName'),
    '700$d': onwork.link(rel=LL + 'relatedWorkOrContributorDate'),

    '710$a': onwork.link(rel=LL + 'relatedWorkOrContributorName'),
    '710$d': onwork.link(rel=LL + 'relatedWorkOrContributorDate'),

    '711$a': onwork.link(rel=LL + 'relatedWorkOrContributorName'),
    '711$d': onwork.link(rel=LL + 'relatedWorkOrContributorDate'),

    '730$a': onwork.link(rel=BL + 'collectionName'),
}


WORK_HASH_TRANSFORMS_ID = 'http://bibfra.me/tool/pybibframe/transforms#workhash'

register_transforms(WORK_HASH_TRANSFORMS_ID, WORK_HASH_TRANSFORMS)


# special thanks to UCD, NLM, GW
WORK_HASH_INPUT = [
    # Stuff derived from leader, 006 & 008
    VTYPE_REL,
    LL + 'date',
    LL + 'language',
    # MARC + 'literaryForm',
    # MARC + 'illustrations',
    # MARC + 'index',
    # MARC + 'natureOfContents',
    # MARC + 'formOfItem',
    # MARC + 'governmentPublication',
    # MARC + 'biographical',
    # MARC + 'formOfComposition',
    # MARC + 'formatOfMusic',
    # MARC + 'musicParts',
    # MARC + 'targetAudience',
    # MARC + 'accompanyingMatter',
    # MARC + 'literaryTextForSoundRecordings',
    # MARC + 'transpositionAndArrangement',
    # MARC + 'relief',
    # MARC + 'projection',
    # MARC + 'characteristic',
    # MARC + 'specialFormatCharacteristics',
    # MARC + 'runtime',
    # MARC + 'technique',
    # MARC + 'frequency',
    # MARC + 'regularity',
    # MARC + 'formOfOriginalItem',
    # MARC + 'natureOfEntireWork',
    # MARC + 'natureOfContents',
    # MARC + 'originalAlphabetOrScriptOfTitle',
    # MARC + 'entryConvention',
    # MARC + 'specificMaterialDesignation',
    # MARC + 'color',
    # MARC + 'physicalMedium',
    # MARC + 'typeOfReproduction',
    # MARC + 'productionReproductionDetails',
    # MARC + 'positiveNegativeAspect',
    # MARC + 'sound',
    # MARC + 'dimensions',
    # MARC + 'imageBitDepth',
    # MARC + 'fileFormat',
    # MARC + 'qualityAssuranceTargets',
    # MARC + 'antecedentSource',
    # MARC + 'levelOfCompression',
    # MARC + 'reformattingQuality',
    # MARC + 'typeOfReproduction',
    # MARC + 'classOfBrailleWriting',
    # MARC + 'levelOfContraction',
    # MARC + 'brailleMusicFormat',
    # MARC + 'specialPhysicalCharacteristics',
    # MARC + 'baseOfEmulsion',
    # MARC + 'soundOnMediumOrSeparate',
    # MARC + 'mediumForSound',
    # MARC + 'secondarySupportMaterial',
    # MARC + 'positiveNegativeAspect',
    # MARC + 'reductionRatioRange',
    # MARC + 'reductionRatio',
    # MARC + 'emulsionOnFilm',
    # MARC + 'generation',
    # MARC + 'baseOfFilm',
    # MARC + 'motionPicturePresentationFormat',
    # MARC + 'configurationOfPlaybackChannels',
    # MARC + 'productionElements',
    # MARC + 'refinedCategoriesOfColor',
    # MARC + 'kindOfColorStockOrPrint',
    # MARC + 'deteriorationStage',
    # MARC + 'completeness',
    # MARC + 'filmInspectionDate',
    # MARC + 'altitudeOfSensor',
    # MARC + 'cloudCover',
    # MARC + 'platformConstructionType',
    # MARC + 'platformUseCategory',
    # MARC + 'sensorType',
    # MARC + 'dataType',
    # MARC + 'speed',
    # MARC + 'configurationOfPlaybackChannels',
    # MARC + 'grooveWidthPitch',
    # MARC + 'tapeWidth',
    # MARC + 'tapeConfiguration',
    # MARC + 'kindOfDiscCylinderOrTape',
    # MARC + 'kindOfMaterial',
    # MARC + 'kindOfCutting',
    # MARC + 'specialPlaybackCharacteristics',
    # MARC + 'captureAndStorageTechnique',
    # MARC + 'videorecordingFormat',

    LL + 'collectionTitle',
    LL + 'collectionName',

    BL + 'title',
    MARC + 'titleRemainder',
    MARC + 'titleStatement',
    MARC + 'titleNumber',
    MARC + 'titlePart',
    MARC + 'inclusiveDates',
    MARC + 'formDesignation',

    MARC + 'titleVariation',
    MARC + 'titleVariationRemainder',
    MARC + 'titleVariationDate',

    # MARC + 'edition',

    LL + 'creatorName',
    LL + 'creatorDate',

    BL + 'organizationName',
    BL + 'organizationDate',

    BL + 'meetingName',
    BL + 'meetingNate',

    LL + 'subjectName',

    LL + 'relatedWorkOrContributorName',
    LL + 'relatedWorkOrContributorDate',
]
