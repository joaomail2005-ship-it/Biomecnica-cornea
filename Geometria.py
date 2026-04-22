# -*- coding: utf-8 -*-
# Geometria.py

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

def calculo_cordenadas(S,H,L):
    
    p1 = (0.0,H)
    p3 = (0.0,H - S)
    p4 = (L/2,0.0)
    
    Cy = (p4[0]**2 - p3[0]**2 + p4[1]**2 - p3[1]**2) / (2*(p4[1] - p3[1]))
    c2 = (0.0, Cy)
    
    a = 0
    b = Cy
        
    c1 = (a,b)
    
    R = ((p1[0]-a)**2 + (p1[1]-b)**2)**0.5
    
    m = (p4[1] - b) / (p4[0] - a)
    
    dx = R / (1 + m**2)**0.5
    
    x1 = a + dx
    x2 = a - dx
    
    y1 = m*(x1 - a) + b
    y2 = m*(x2 - a) + b
    
    if x1 > 0:
        p2 = (x1, y1)
    else:
        p2 = (x2, y2)
    return [p1, p2, c1, p3, p4, c2]

#CRIANDO GEOMETRIA INICIAL
def cria_geometria(model,cord_iniciais,L):
    
    p1 = cord_iniciais[0]
    p2 = cord_iniciais[1]
    c1 = cord_iniciais[2]
    p3 = cord_iniciais[3]
    p4 = cord_iniciais[4]
    c2 = cord_iniciais[5]
    
    #Cria sketch
    model.ConstrainedSketch(name='__profile__', sheetSize=200.0)

    #Linha de construção
    model.sketches['__profile__'].ConstructionLine(point1=(0.0, 
        -100.0), point2=(0.0, 100.0))
    model.sketches['__profile__'].FixedConstraint(entity=
        model.sketches['__profile__'].geometry[2])

    sketch = mdb.models['Model-1'].sketches['__profile__']
    
    sketch.ArcByCenterEnds(center=c1, point1=p1, point2=p2, direction=CLOCKWISE)
    sketch.ArcByCenterEnds(center=c2, point1=p3, point2=p4, direction=CLOCKWISE)

    sketch.Line(point1=p1, point2=p3)
    sketch.Line(point1=p4, point2=p2)
    
    #Finaliza sketch
    mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Part-1', type=
        DEFORMABLE_BODY)

    #Faz o revolution criando a geometria 3D
    mdb.models['Model-1'].parts['Part-1'].BaseSolidRevolve(angle=360.0, 
        flipRevolveDirection=OFF, sketch=
        mdb.models['Model-1'].sketches['__profile__'])
    del mdb.models['Model-1'].sketches['__profile__']

    #Cria partição cortando ao meio
    mdb.models['Model-1'].parts['Part-1'].PartitionCellByPlaneThreePoints(cells=
        mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(('[#1 ]', 
        ), ), point1=mdb.models['Model-1'].parts['Part-1'].InterestingPoint(
        mdb.models['Model-1'].parts['Part-1'].edges[2], MIDDLE), point2=
        mdb.models['Model-1'].parts['Part-1'].vertices[3], point3=
        mdb.models['Model-1'].parts['Part-1'].vertices[0])

    # Sketch partition face na face que corta a peça ao meio
    mdb.models['Model-1'].ConstrainedSketch(
        gridSpacing=0.59, 
        name='__profile__',      
        sheetSize=23.73, 
        transform=
            mdb.models['Model-1'].parts['Part-1'].MakeSketchTransform(
                sketchPlane=mdb.models['Model-1'].parts['Part-1'].faces[0],  
                sketchPlaneSide=SIDE1,
                sketchUpEdge=mdb.models['Model-1'].parts['Part-1'].edges[4],  
                sketchOrientation=RIGHT,
                origin=(0.0, 0.0, 0.0)  
            )
    )

    print("linha 79 ok")
    
    # Projeta as arestas coplanares da peça no sketch
    mdb.models['Model-1'].parts['Part-1'].projectReferencesOntoSketch(
        filter=COPLANAR_EDGES, 
        sketch=mdb.models['Model-1'].sketches['__profile__']
    )

    # Cria um arco definido por 3 pontos (em metade da peça)
    p5 =( -((p3[1]+p1[1])/2) ,
        ((p3[0]+p1[0])/2)
        )
    p6 = (
          -(p2[1] + p4[1])/2 , 
          ((p2[0] + p4[0])/2)
          )
    
    pmid = encontraPmidCirc((-p5[1],-p5[0]),(-p6[1],-p6[0]),c2)
    #print(p5,p6,c2,pmid)
    mdb.models['Model-1'].sketches['__profile__'].ArcByCenterEnds(center=(-c2[1],c2[0]), point1=p5, point2=p6, direction=CLOCKWISE)

    # Particiona uma face da peça usando o sketch criado
    mdb.models['Model-1'].parts['Part-1'].PartitionFaceBySketch(
        faces=mdb.models['Model-1'].parts['Part-1'].faces[0],
        sketch=mdb.models['Model-1'].sketches['__profile__'],
        sketchUpEdge=mdb.models['Model-1'].parts['Part-1'].edges[4]
    )
        
    print("linha 114 ok")
    # Deleta o sketch após uso
    del mdb.models['Model-1'].sketches['__profile__']
    
    # Particiona células varrendo uma aresta tendo como caminho as bordas da geometira (separando a espessura em duas camadas)
    edge = mdb.models['Model-1'].parts['Part-1'].edges.findAt((pmid[0], pmid[1], 0.0))

    mdb.models['Model-1'].parts['Part-1'].PartitionCellBySweepEdge(
        cells=mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(('[#3 ]',)),
        edges=(edge,), 
        sweepPath=mdb.models['Model-1'].parts['Part-1'].edges.findAt((0, p4[1], p4[0]))
    )
    

    # Outra partição por varredura (repete o processo acima para a outra metade da peça)
    edge = mdb.models['Model-1'].parts['Part-1'].edges.findAt((pmid[0], pmid[1], 0.0))

    mdb.models['Model-1'].parts['Part-1'].PartitionCellBySweepEdge(
        cells=mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(('[#3 ]',)),
        edges=(edge,), 
        sweepPath=mdb.models['Model-1'].parts['Part-1'].edges.findAt((0, p4[1], -p4[0]))
    )

    #Cria partição que corta a geometria em outra metade, deixando com 4 partes quando vista de cima ou de baixo
    mdb.models['Model-1'].parts['Part-1'].PartitionCellByPlaneThreePoints(cells=
        mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(('[#f ]', 
        ), ), point1=mdb.models['Model-1'].parts['Part-1'].InterestingPoint(
        mdb.models['Model-1'].parts['Part-1'].edges[14], MIDDLE), point2=
        mdb.models['Model-1'].parts['Part-1'].vertices[7], point3=
        mdb.models['Model-1'].parts['Part-1'].InterestingPoint(
        mdb.models['Model-1'].parts['Part-1'].edges[4], MIDDLE))