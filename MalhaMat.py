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
def criar_malha(modelo,model_part,devFact,minSizeFact,elementSize):
    model_part.setMeshControls(algorithm=MEDIAL_AXIS, 
        regions=model_part.cells[:]
        , technique=SWEEP)
    
    model_part.seedPart(deviationFactor=devFact, 
        minSizeFactor=minSizeFact, size=elementSize)
    model_part.generateMesh()

def criar_materiais_linElastico(modelo,model_part,Esaudavel, Rsaudavel, Efraco, Rfraco):

    part = model_part

    # Material saudável 
    modelo.Material(name='Speavk')
    modelo.materials['Speavk'].Elastic(table=((Esaudavel, Rsaudavel), ))
    modelo.HomogeneousSolidSection(material='Speavk', name='Section-1', thickness=None)
    part.Set(cells=part.cells[:], name='Set-3')
    part.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
        region=part.sets['Set-3'], sectionName='Section-1', thicknessAssignment=FROM_SECTION)

    # Material enfraquecido 
    modelo.Material(name='Enfraquecido')
    modelo.materials['Enfraquecido'].Elastic(table=((Efraco, Rfraco), ))
    modelo.HomogeneousSolidSection(material='Enfraquecido', name='Section-2', thickness=None)
    part.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
        region=part.sets['Fraqueza'], sectionName='Section-2', thicknessAssignment=FROM_SECTION)
