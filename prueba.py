from pathlib import Path
import os
import sys
import pandas as pd
from unidecode import unidecode
import unicodedata
import numpy as np
import math as m
import re



# FUNCIONES IMPORTANTES
 # FUNCIONES IMPORTANTES
 #------------ Remueve acentos 
def remove_accents(input_str):
    # Normalizar el string a su forma combinada
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    # Filtrar y mantener solo los caracteres que no son diacríticos
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
# ----------- Crea data de zonas 
def Zone_data(Hoja,type):
    #excel = "diccionario_Benja/Diccionario_EMTP_DIgSILENT_BVega_v4.xlsx"
    excel = "diccionario_Benja/Zonas_DIgSILENT.xlsx"
    data= pd.read_excel(excel,sheet_name=Hoja)
    if type == "PV":
        columnas_deseadas = ['Name1', 'Name2','Zona DIgSILENT','Nombre DIgSILENT']  # Reemplaza con los nombres de las columnas que deseas
    elif type == "WP":
         columnas_deseadas = ['Name1','Zona DIgSILENT','Nombre DIgSILENT']     
    elif type == "SG":
        columnas_deseadas = ['Name1', 'Name2','Name3','Zona DIgSILENT','Nombre DIgSILENT']    
    elif type == "PMGD":
        columnas_deseadas = ['Name1', 'Name2','Zona DIgSILENT','Nombre DIgSILENT']  
    elif type == "CCSS":
        columnas_deseadas = ['Name1', 'Name2','Zona DIgSILENT','Nombre DIgSILENT']    
    elif type =="Cargas":
        columnas_deseadas = ['Carga EMTP','Zona DIgSILENT']   
        
    # Filtra el DataFrame para que contenga solo las columnas deseadas
    dataframe_filtrado = data[columnas_deseadas]
    #return dataframe_filtrado.dropna()   
    return dataframe_filtrado   

def Transformación_MW_MVAR(cadena):
    #cadena_sin_mas = cadena[1:]
    #final= float(cadena_sin_mas)/(10**6)
    final= float(cadena)/(10**6)
    final=round(final,2)
    return (final)
def obtener_V_op(cadena):
    numeros = re.findall(r'[+-]?\d+\.\d+E[+-]?\d+', cadena)
    indices_pares = [i for i in range(len(numeros)) if i % 2 == 0]
    valores_pares = [numeros[i] for i in indices_pares]
    lista_V = [round(float(elemento),2) for elemento in valores_pares]
    if lista_V[0] == lista_V[1] == lista_V[2]:
        return lista_V[0]
    else:
        return "desbanceado"
# toma un el string que tiene "V+anglo y me entrega solo el "V y redondeado" 
def separar_numeros(s):
    numeros = re.findall(r'[+-]?\d+\.\d+E[+-]?\d+', s)
    if numeros:
        numero_1 = float(numeros[0])  # Convertir a float
        return round(numero_1, 2)
# obtengo cual es la tension nominal a partir del resultado
def analizar_numero(n):
    if 90 <= n + 20 <= 130 or 90 <= n - 20 <= 130:
        return 110
    elif 200 <= n + 20 <= 240 or 200 <= n - 20 <= 240:
        return 220
    elif 46 <= n + 20 <= 86 or 46 <= n - 20 <= 86:
        return 66
    elif 3 <= n + 10 <= 23.2 or 3 <= n - 10 <= 23.2:
        return 13.2    
    else:
        return None  # Si no cae en ninguna categoría



# Aqui coloco el nombre del archivo como string
#archivo =  "SEN 2025 VRE Peak 04072024 DBC 85 GFM New - H1_v4_lf.html"
archivo = "SEN 2025 VRE Peak 85 VRE_g1_10 steps_lf.html"
excel = "Datos_nom_v1.xlsx"

# leo Excel y HTML
V_nominal = pd.read_excel(excel)
df= pd.read_html(archivo)
df=pd.DataFrame(df[0]) # Lo hago legible
#obtengo el nombre las columnas y las reescribo
fila_cero = df.iloc[0] 
df.columns =fila_cero.to_list()
#borro la fila 0 que tenia los nombres de las columnas
df = df.iloc[1:]

# reseteo los indices desde 0 y luego borro la primera columna indice
df=pd.DataFrame(df.reset_index())
#  obtengo solo las 5 primeras importantes 
# Central, Tipo, V ,P Q
lista_columnas = fila_cero.to_list()
lista_columnas= lista_columnas[:5] 
df = df[lista_columnas[:5]]

#--------------Data Generacion-------------------
valores_filtrar = ['PVbus', 'Slack', 'PQbus']
df_GEN = df[df['Type'].isin(valores_filtrar)]
# Data frame vacio de columnas definidas
columnas = ["V [kV]","P [MW]","Q [MVAr]"]
df_GEN_F = pd.DataFrame(columns=columnas)

df_GEN_F['P [MW]']=df_GEN['P (W)'].apply(Transformación_MW_MVAR)
df_GEN_F['Q [MVAr]']=df_GEN['Q (VAR)'].apply(Transformación_MW_MVAR)
df_GEN_F["V [kV]"] = df_GEN["Vabc (kVRMSLL,deg) phasor"].apply(obtener_V_op)




columnas2 = ["Name1","Name2","Name3","NameLF"]

with pd.ExcelWriter('Resultados_.xlsx') as writer:

    df_GEN.to_excel(writer, sheet_name='LFcargas',index=False)
           