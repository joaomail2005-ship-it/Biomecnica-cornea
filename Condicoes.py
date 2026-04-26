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

def encontraPmidCirc(p1,p2,c):
  x = (p1[0]+p2[0])/2
  
  r = pow(p1[0]-c[0],2) + pow(p1[1]-c[1],2)

  y = c[1] + pow(r - pow(x - c[0],2),0.5)

  pmid = (x,y)

  return pmid

def indices_para_mask(indices):
            """Converte lista de índices de edge no formato de máscara do Abaqus."""
            if not indices:
                return ('[#0 ]',)
            n_words = (max(indices) // 32) + 1
            words = [0] * n_words
            for i in indices:
                words[i // 32] |= (1 << (i % 32))
            mask_str = '[' + ' '.join('#%x' % w for w in words) + ' ]'
            return (mask_str,)

def encontra_faces(inst,p1,p2):
    faces_inf = []
    for i in [0, 1]:
        for p in [p1,p2]:
            x  = p[0] * (-1)**i
            y  = p[1]
            z  = p[2] * (-1)**i
            face = inst.faces.getClosest(coordinates=((x, y, z),))[0][0]
            faces_inf.append(face)

            x2 = p[0] * (-1)**(i+1)
            z2 = p[2] * (-1)**i
            face2 = inst.faces.getClosest(coordinates=((x2, y, z2),))[0][0]
            faces_inf.append(face2)
            
    id_faces = list(set(e.index for e in faces_inf))
    mask = indices_para_mask(id_faces)
    faces_seq = inst.faces.getSequenceFromMask(mask=mask)
    
    return faces_seq
#CRIANDO CONDIÇÕES DE CONTORNO E APLICANDO PRESSÃO
def aplicar_condicoes(modelo,model_part,press,S,L, rfraq, pfraq, cord_iniciais,pontos_fraq):

    p1 = cord_iniciais[0]
    p2 = cord_iniciais[1]
    p4 = cord_iniciais[4]

    # Assembly
    modelo.rootAssembly.DatumCsysByDefault(CARTESIAN)
    modelo.rootAssembly.Instance(
        dependent=ON, name='Part-1-1',
        part=model_part
    )

    inst = modelo.rootAssembly.instances['Part-1-1']

    print("Pontos contorno: ")
    pmid1 = encontraPmidCirc((p2[0], 0), (0, p2[0]), (0, 0))
    pmid1 = (pmid1[0], p2[1], pmid1[1])
    print(pmid1)

    pmid2 = encontraPmidCirc((p4[0], 0), (0, p4[0]), (0, 0))
    pmid2 = (pmid2[0], p4[1], pmid2[1])
    print(pmid2)

    pmid3 = (
        (pmid1[0] + pmid2[0]) / 2,
        (pmid1[1] + pmid2[1]) / 2,
        (pmid1[2] + pmid2[2]) / 2
    )
    print(pmid3)
    
    faces_seq = encontra_faces(inst,(pmid3[0],pmid3[1]-0.2,pmid3[2]),
                  (pmid3[0],pmid3[1]+0.2,pmid3[2]))
    
    modelo.EncastreBC(
        createStepName='Initial',
        localCsys=None,
        name='BC-1',
        region=Region(faces = faces_seq)
    )

    modelo.StaticStep(name='Step-1', previous='Initial')
    
    faces_seq = encontra_faces(inst,(pontos_fraq[1][0]-0.2,pontos_fraq[1][1]-S,pontos_fraq[1][2]-0.2),
                  (pontos_fraq[1][0]+0.2,pontos_fraq[1][1]-S,pontos_fraq[1][2]+0.2))
    
    modelo.Pressure(
        amplitude=UNSET, createStepName='Step-1',
        distributionType=UNIFORM, field='',
        magnitude=press, name='Load-1',
        region=Region(side1Faces=faces_seq)
        )
    