from flask import Flask
import os

import gspread
import requests
from flask import Flask, request
import gspread
import zipfile
import json
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

#Criando função que baixa arquivo
def baixar_arquivo(url, endereco):
    resposta = requests.get(url)
    if resposta.status_code == requests.codes.OK:
        with open(endereco, 'wb') as novo_arquivo:
            novo_arquivo.write(resposta.content)
        print("Donwload finalizado. Salvo em: {}".format(endereco))
    else:
        resposta.raise_for_status()
        
#baixando arquivo despesas
baixar_arquivo('https://www.camara.leg.br/cotas/Ano-2022.csv.zip','CSV')

with zipfile.ZipFile('CSV') as z:
  print(z.namelist(),sep='\n')

with zipfile.ZipFile('CSV') as z:
  with z.open('Ano-2022.csv') as f:
    despesas = pd.read_csv(f, sep=';', low_memory=False)
    
despesas['numMes'] = despesas['numMes'].astype(int)

gastos = despesas['vlrLiquido'].sum()

#Quais deputados mais gastaram?
gastadores = despesas.groupby(['txNomeParlamentar', 'sgUF'])['vlrLiquido'].sum()
gastadoresBR_top10 = gastadores.nlargest(10, keep='first')
gastadoresBR_top10 = pd.DataFrame(gastadoresBR_top10)
gastadoresBR_top10 = gastadoresBR_top10.reset_index()
gastadoresBR_top10

gastadores = despesas.groupby(['txNomeParlamentar', 'sgUF'])['vlrLiquido'].sum()
gastadores = pd.DataFrame(gastadores)
gastadores = gastadores.reset_index()

#Deputado/a que mais gastou
maiorgastador = gastadoresBR_top10.iloc[0]['txNomeParlamentar']

#Deputado/a que menos gastou
gastadores = despesas.groupby(['txNomeParlamentar', 'sgUF'])['vlrLiquido'].sum()
gastadores = pd.DataFrame(gastadores)
gastadores = gastadores.sort_values(by='vlrLiquido')
gastadores = gastadores.reset_index()

menorgastador = gastadores.iloc[0]['txNomeParlamentar']

#Média de Gastos de deputados por estado
estadosBr = despesas.groupby('sgUF')['vlrLiquido'].mean()
estadosBr.sort_values(ascending=False)
estados = pd.DataFrame(estadosBr)
estados = estados.reset_index()

#Analisando PLs

baixar_arquivo('https://dadosabertos.camara.leg.br/arquivos/proposicoesAutores/csv/proposicoesAutores-2022.csv','proposicoesAutores-2022.csv')
proposicoes = pd.read_csv('proposicoesAutores-2022.csv',
                          sep = ';', low_memory=False)

#Quais deputados mais apresentaram PLs?
autores = proposicoes.groupby('nomeAutor').count()
autores = pd.DataFrame(autores)
autores = autores.sort_values(by='idProposicao', ascending = False)
autores = autores.reset_index()

maior_autor = autores.iloc[0]['nomeAutor']

menor_autor = autores.iloc[-1]['nomeAutor']

# Criando site

app = Flask(__name__)

menu = """
<a href="/">Página inicial</a> | <a href="/sobre">Sobre</a> | <a href="/gastosceap">GastosCEAP</a> |<a href="/projetosdelei">ProjetosdeLei</a> <a href="/contato">Contato</a> | 
<br>
"""

@app.route("/sobre")
def sobre():
  return menu + "Aqui vai o conteúdo da página Sobre"

@app.route("/contato")
def contato():
  return menu + "Aqui vai o conteúdo da página Contato"

@app.route("/gastosCEAP")
def gastos():
  return f"Em 2022, o total gasto pelos(as) deputados federais foi igual à R${gastos}. \n A média de gastos da cota parlamentar por deputado(a) foi de R${mediaBr}, o(a) deputado(a) que mais gastou foi {maiorgastador}, o(a) que menos gastou foi {menorgastador}."
