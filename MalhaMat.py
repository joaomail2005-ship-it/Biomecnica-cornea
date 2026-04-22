# -*- coding: utf-8 -*-
# Condicoes.py

# -*- coding: mbcs -*-
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

import numpy as np

import math as math

#CRIANDO MALHA E MATERIAIS
def criar_malha(devFact,minSizeFact,elementSize):
    mdb.models['Model-1'].parts['Part-1'].setMeshControls(algorithm=MEDIAL_AXIS, 
        regions=mdb.models['Model-1'].parts['Part-1'].cells[:]
        , technique=SWEEP)
    
    mdb.models['Model-1'].parts['Part-1'].seedPart(deviationFactor=devFact, 
        minSizeFactor=minSizeFact, size=elementSize)
    mdb.models['Model-1'].parts['Part-1'].generateMesh()

def criar_materiais_linElastico(Esaudavel, Rsaudavel, Efraco, Rfraco):

    part = mdb.models['Model-1'].parts['Part-1']

    # Material saudável 
    mdb.models['Model-1'].Material(name='Speavk')
    mdb.models['Model-1'].materials['Speavk'].Elastic(table=((Esaudavel, Rsaudavel), ))
    mdb.models['Model-1'].HomogeneousSolidSection(material='Speavk', name='Section-1', thickness=None)
    part.Set(cells=part.cells[:], name='Set-3')
    part.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
        region=part.sets['Set-3'], sectionName='Section-1', thicknessAssignment=FROM_SECTION)

    # Material enfraquecido 
    mdb.models['Model-1'].Material(name='Enfraquecido')
    mdb.models['Model-1'].materials['Enfraquecido'].Elastic(table=((Efraco, Rfraco), ))
    mdb.models['Model-1'].HomogeneousSolidSection(material='Enfraquecido', name='Section-2', thickness=None)
    part.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
        region=part.sets['Fraqueza'], sectionName='Section-2', thicknessAssignment=FROM_SECTION)
