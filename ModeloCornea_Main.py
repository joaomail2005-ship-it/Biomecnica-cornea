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

import sys
import os

caminho_pasta = r"C:\Users\joaom\Projetos_biomec\src" 
if caminho_pasta not in sys.path:
    sys.path.insert(0, caminho_pasta)
print("hora do commit?")
try:
    import Geometria as geometria
    import Fraqueza as fraqueza   
    import Condicoes as condicoes
    import MalhaMat as malhaMat
    
    print(">>> SUCESSO: Todos os modulos carregados e recarregados! <<<")
except ImportError as e:
    print("[ERRO] Falha ao importar os modulos: ", e,"Verifique o -caminho da pasta- definido nas primeiras linhas do arquivo main")


#CRIANDO O JOB
def job():
    mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
        explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
        memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=OFF, 
        multiprocessingMode=DEFAULT, name='Job-1', nodalOutputPrecision=SINGLE, 
        numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=
        ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
    
    #mdb.jobs['Job-1'].submit()
    #mdb.jobs['Job-1'].waitForCompletion()

def main():

    parametros = {
        "geometria": {
            "S": 0.63,
            "H": 2.52,
            "L": 11.6
        },
        "fraqueza": {
            "pfraq": (0, 2.52, 0),
            "rfraq": 3.5
        },
        "malha": {
            "devFact": 0.05,
            "minSizeFact": 0.05,
            "elementSize": 0.1
        },
        "material": {
            "Esaudavel": 14.3,
            "Rsaudavel": 0.45,
            "Efraco": 7.8,
            "Rfraco": 0.45
        },
        "carga": {
            "pressao": 0.00399
        }
    }

    geo = parametros["geometria"]
    fraq = parametros["fraqueza"]
    malha = parametros["malha"]
    mat = parametros["material"]
    carga = parametros["carga"]

    model = mdb.models['Model-1']

    cord_iniciais = geom.calculo_cordenadas(
        geo["S"], geo["H"], geo["L"]
    )

    geometria.cria_geometria(
        model,
        cord_iniciais,
        geo["L"]
    )

    pontos_fraq = fraqueza.criar_fraqueza(
        cord_iniciais,
        fraq["pfraq"],
        fraq["rfraq"],
        geo["S"],
        geo["L"]
    )

    malhaMat.criar_malha(
        malha["devFact"],
        malha["minSizeFact"],
        malha["elementSize"]
    )

    malhaMat.criar_materiais_linElastico(
        mat["Esaudavel"],
        mat["Rsaudavel"],
        mat["Efraco"],
        mat["Rfraco"]
    )

    condicoes.aplicar_condicoes(
        carga["pressao"],
        geo["S"],
        geo["L"],
        fraq["rfraq"],
        fraq["pfraq"],
        cord_iniciais,
        pontos_fraq
    )
    job()

main()
# Save by joaom on 2026_03_23-16.50.02; build Unofficial Packaging Version 2017_11_07-14.21.41 127140
