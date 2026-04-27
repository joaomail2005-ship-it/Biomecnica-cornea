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
    import Job as job
    
    print(">>> SUCESSO: Todos os modulos carregados e recarregados! <<<")
except ImportError as e:
    print("[ERRO] Falha ao importar os modulos: ", e,"Verifique o -caminho da pasta- definido nas primeiras linhas do arquivo main")

'''
    - entender melhor fomra de escolher e tirar dados do job
'''
def main():
    posfraq = (0, 1, 1)
    matfraq = (7.8, 7.8, 14.3)
    
    for i in range(3):
        nome_modelo = "Modelo_Simulacao_{}".format(i)
        nome_part = "Part-1" 
        nome_job = "Job_Simulacao_{}".format(i)
        
        if nome_modelo not in mdb.models:
            mdb.Model(name=nome_modelo)

        modelo = mdb.models[nome_modelo]
        
        # Dicionário de parâmetros da iteração atual
        parametros = {
            "geometria": {
                "S": 0.63,
                "H": 2.52,
                "L": 11.6
            },
            "fraqueza": {
                "pfraq": (posfraq[i], 2.52, 0),
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
                "Efraco": matfraq[i],
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

        cord_iniciais = geometria.calculo_cordenadas(
            geo["S"], geo["H"], geo["L"]
        )
        
        geometria.cria_geometria(
            modelo, nome_part, 
            cord_iniciais, geo["L"]
        )

        part = modelo.parts[nome_part]
        
        pontos_fraq = fraqueza.criar_fraqueza(
            modelo, part, 
            cord_iniciais, fraq["pfraq"], fraq["rfraq"], geo["S"], geo["L"]
        )

        malhaMat.criar_malha(
            modelo, part, 
            malha["devFact"], malha["minSizeFact"], malha["elementSize"]
        )

        malhaMat.criar_materiais_linElastico(
            modelo,part, 
            mat["Esaudavel"], mat["Rsaudavel"], mat["Efraco"], mat["Rfraco"]
        )

        condicoes.aplicar_condicoes(
            modelo, part, 
            carga["pressao"], geo["S"], geo["L"], fraq["rfraq"], fraq["pfraq"], cord_iniciais, pontos_fraq
        )
        
        # O módulo do job também precisa receber o modelo e o nome do job
        job.criar_job(nome_modelo, nome_job)


main()
# Save by joaom on 2026_03_23-16.50.02; build Unofficial Packaging Version 2017_11_07-14.21.41 127140
