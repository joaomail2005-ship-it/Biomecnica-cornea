# -*- coding: utf-8 -*-
# Fraqueza.py

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


def criar_fraqueza(cord_iniciais, pfraq, rfraq, S, L):

    p1 = cord_iniciais[0]
    p2 = cord_iniciais[1]
    c1 = cord_iniciais[2]
    p3 = cord_iniciais[3]
    p4 = cord_iniciais[4]
    c2 = cord_iniciais[5]

    part = mdb.models['Model-1'].parts['Part-1']

    # Raio externo e interno
    R_outer = ((p1[0]-c1[0])**2 + (p1[1]-c1[1])**2) ** 0.5
    c1_3d   = (c1[0], c1[1], 0.0)

    #Datum axis
    datum_axis = part.DatumAxisByTwoPoint(
        point1=(c1[0], c1[1], 0.0),
        point2=(pfraq[0], pfraq[1], pfraq[2])
    )
    datum_axis_id = datum_axis.id

    # Datum plane em pfraq
    datum_plane = part.DatumPlaneByPointNormal(
        normal=part.datums[datum_axis_id],
        point=(pfraq[0], pfraq[1], pfraq[2])
    )
    datum_plane_id = datum_plane.id

    # Aresta de referência para orientar o sketch 
    aresta_ref = part.edges.getClosest(
        coordinates=((pfraq[0] - 0.1, pfraq[1], pfraq[2]),)
    )[0][0]

    # Sketch com círculo centrado na origem do plano
    mdb.models['Model-1'].ConstrainedSketch(
        gridSpacing=0.91, name='__profile__', sheetSize=36.59,
        transform=part.MakeSketchTransform(
            sketchPlane=part.datums[datum_plane_id],
            sketchPlaneSide=SIDE1,
            sketchUpEdge=aresta_ref,
            sketchOrientation=RIGHT,
            origin=(pfraq[0], pfraq[1], pfraq[2])
        )
    )
    mdb.models['Model-1'].sketches['__profile__'].CircleByCenterPerimeter(
        center=(0.0, 0.0), point1=(0.0, rfraq)
    )

    # Particiona todas as faces com o cilindro 
    part.PartitionFaceBySketchThruAll(
        faces=part.faces.getByBoundingBox(
            xMin=-100, yMin=-100, zMin=-100,
            xMax= 100, yMax= 100, zMax= 100
        ),
        sketch=mdb.models['Model-1'].sketches['__profile__'],
        sketchPlane=part.datums[datum_plane_id],
        sketchPlaneSide=SIDE1,
        sketchUpEdge=aresta_ref
    )
    del mdb.models['Model-1'].sketches['__profile__']

    # Direção do eixo normalizada
    dx = pfraq[0] - c1[0]
    dy = pfraq[1] - c1[1]
    dz = pfraq[2] - 0.0
    norm_len = (dx**2 + dy**2 + dz**2) ** 0.5
    nx, ny, nz = dx/norm_len, dy/norm_len, dz/norm_len

    tol_raio = rfraq * 0.05   
    tol_R    = R_outer * 0.005 

    # Filtra arestas
    linhas_fraq    = []
    pontos_retorno = []

    for edge in part.edges:
        pt = edge.pointOn[0]

        # distância perpendicular ao eixo do cilindro
        vx = pt[0] - pfraq[0]
        vy = pt[1] - pfraq[1]
        vz = pt[2] - pfraq[2]
        v_par     = vx*nx + vy*ny + vz*nz
        dist_perp = ((vx - v_par*nx)**2 +
                     (vy - v_par*ny)**2 +
                     (vz - v_par*nz)**2) ** 0.5

        if abs(dist_perp - rfraq) > tol_raio:
            continue

        # ponto sobre a superfície esférica externa
        dist_c1 = ((pt[0]-c1_3d[0])**2 +
                   (pt[1]-c1_3d[1])**2 +
                   (pt[2]-c1_3d[2])**2) ** 0.5

        if abs(dist_c1 - R_outer) > tol_R:
            continue

        linhas_fraq.append(edge)
        pontos_retorno.append(pt)
        part.DatumPointByCoordinate(coords=pt)

    print("Arestas do loop externo encontradas: %d" % len(linhas_fraq))

    #Extrude para criar a célula fraca 
    part.PartitionCellByExtrudeEdge(
        cells=part.cells[:],
        edges=linhas_fraq,
        line=part.datums[datum_axis_id],
        sense=REVERSE
    )

    # Set da região fraca
    tol = 0.1
    celulas_candidatas = part.cells.getByBoundingBox(
        xMin=pfraq[0] - rfraq - tol, xMax=pfraq[0] + rfraq + tol,
        yMin=pfraq[1] - rfraq - tol, yMax=pfraq[1] + rfraq + tol,
        zMin=pfraq[2] - rfraq - tol, zMax=pfraq[2] + rfraq + tol
    )

    celulas_fraq = []
    for cell in celulas_candidatas:
        pt = cell.pointOn[0]

        # Distância perpendicular ao eixo do cilindro
        vx = pt[0] - pfraq[0]
        vy = pt[1] - pfraq[1]
        vz = pt[2] - pfraq[2]
        v_par     = vx*nx + vy*ny + vz*nz
        dist_perp = ((vx - v_par*nx)**2 +
                     (vy - v_par*ny)**2 +
                     (vz - v_par*nz)**2) ** 0.5

        if dist_perp < rfraq:
            celulas_fraq.append(cell)

    indices = [cell.index for cell in celulas_fraq]

    # Converte índices para máscara Abaqus
    n_words = (max(indices) // 32) + 1
    words = [0] * n_words
    for i in indices:
        words[i // 32] |= (1 << (i % 32))
    mask = '[' + ' '.join('#%x' % w for w in words) + ' ]'

    celulas_seq = part.cells.getSequenceFromMask(mask=(mask,))
    print("Celulas na fraqueza: %d" % len(celulas_seq))
    part.Set(cells=celulas_seq, name='Fraqueza')

    return pontos_retorno