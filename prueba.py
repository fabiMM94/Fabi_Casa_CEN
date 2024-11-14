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

 #------------ Remueve acentos 
def remove_accents(input_str):
    # Normalizar el string a su forma combinada
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    # Filtrar y mantener solo los caracteres que no son diacríticos
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
# ----------- Crea data de zonas 


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
    elif 10 <= n + 7 <= 23.2 or 7 <= n - 7 <= 23.2:
        return 13.2    
    elif 0.1 <= n + 2 <= 4 or 0.1 <= n -2 <= 4:
        return 0.6     
    else:
        return None  # Si no cae en ninguna categoría

# Ruta de la carpeta en la que deseas buscar los archivos HTML
ruta_carpeta = '.'

# Listar todos los archivos con extensión .html en la carpeta
archivos_html = [archivo for archivo in os.listdir(ruta_carpeta) if archivo.endswith('.html')]

# Aqui coloco el nombre del archivo como string
#archivo = "2024.11.08 1047 SEN 2030 Norte_BVG Norte_lf.html"
#archivo = "SEN 2025 VRE Peak 85 VRE_g1_10 steps_lf.html"
excel = "Datos_nom_v1.xlsx"
V_nominal = pd.read_excel(excel)
c=0
for archivo in archivos_html:
     # leo Excel y HTML
 
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
    df_GEN_F['Vnom [kV]'] = df_GEN_F["V [kV]"].apply(analizar_numero) #Arreglo



    #aqui la colummna device la expando para obtener 3 columnas de tal forma que coincida con lo anterior
    Nombres = df_GEN['Device'].str.split('/', expand=True)
    if  len(Nombres.columns) > 3 :
        Nombres.columns = ['Name1', 'Name2', 'NameLF',"Name4"]
        # Esto entrega la tabla de resultados de todas las centrales del HTML
        df_GEN_Final = pd.concat([Nombres,df_GEN_F], axis=1)
        df_GEN_Final = df_GEN_Final.drop(columns=['Name4']) #no tiene nada util
    else : 
        Nombres.columns = ['Name1', 'Name2', 'NameLF']
        df_GEN_Final = pd.concat([Nombres,df_GEN_F], axis=1)





    # PARCHES
    df_GEN_Final.loc[df_GEN_Final['Name1'].str.contains('CCSS|CS', case=False, na=False), 'Vnom [kV]'] = 15
    df_GEN_Final.loc[df_GEN_Final['Name1'].isin(['LF_CS_U15']), 'Vnom [kV]'] = 13.8
    df_GEN_Final.loc[df_GEN_Final['Name1'].isin(['Central_IEM_CTM3'	]), 'Vnom [kV]'] = 20
    df_GEN_Final.loc[df_GEN_Final['Name1'].isin(['Central_EL_Paso'	]), 'Vnom [kV]'] = 10.5

    ##------------------------Sobre escribo datos nominales------------------------------------
    
    N = len(df_GEN_Final)
    for fila in range(N):
        Name1= df_GEN_Final.at[fila,"Name1"]
        Name2= df_GEN_Final.at[fila,"Name2"]
        NameLF= df_GEN_Final.at[fila,"NameLF"]
        result = V_nominal[(V_nominal['Name1'] == Name1) &
                                 (V_nominal['Name2'] == Name2) & 
                                 (V_nominal['NameLF'] == NameLF)]
        if len(result)== 1:
            df_GEN_Final.at[fila,"Vnom [kV]"] =result["Tensión Nominal [kV]"]
        else: 
            continue 
    # Escribo V pu 
    df_GEN_Final['Tensión [pu]'] = df_GEN_Final["V [kV]"]/df_GEN_Final['Vnom [kV]']
 
    Tabla_LF_GEN=df_GEN_Final
    Tabla_LF_GEN
   







#-------------------------------- CARGAS -------------------------------------------------------
    df= pd.read_html(archivo)
    columnas = ["V [kV]","P [MW]","Q [MVAr]"]
    #columnas = ['Tensión en Bornes [kV]','Potencia Activa [MW]', 'Potencia Reactiva [Mvar]']
    columnas2 = ['Name1','Name2', 'EMTP Load Flow Component']
    df2 = pd.DataFrame(columns=columnas2)
    
    # Crear el DataFrame vacío con las columnas definidas
    df_FINAL = pd.DataFrame(columns=columnas)
    df=pd.DataFrame(df[0])
    # Se procede a transformar el dataframe de html para que este legible 

    #obtengo el nombre las columnas y las reescribo
    fila_cero = df.iloc[0] 
    df.columns =fila_cero.to_list()
    #borro la fila 0 que tenia los nombres de las columnas
    df = df.iloc[1:]
    # reseteo los indices desde 0 y luego borro la primera columna indice
    df=pd.DataFrame(df.reset_index())
    lista_columnas = fila_cero.to_list()
    #  obtengo solo las 5 primeras importantes
    lista_columnas= lista_columnas[:5] 
    df2 = df[lista_columnas[:5]]
    # Crear una lista que solo contenga las centrales y no las cargas 


    valores_filtrar2 = ['PQload']
    df_filtrado2 = df2[df2['Type'].isin(valores_filtrar2)]
 
    #valores_filtrar = ['PVbus', 'Slack', 'PQbus']
    #df_filtrado = df2[df2['Type'].isin(valores_filtrar)]

    df_FINAL["P [MW]"]=df_filtrado2['P (W)'].apply(Transformación_MW_MVAR)
    df_FINAL["Q [MVAr]"]=df_filtrado2['Q (VAR)'].apply(Transformación_MW_MVAR)
    df_FINAL["V [kV]"] = df_filtrado2["Vabc (kVRMSLL,deg) phasor"].apply(separar_numeros)
    df_FINAL['Vnom [kV]'] = df_FINAL["V [kV]"].apply(analizar_numero)
    df_FINAL['V [pu]'] = df_FINAL["V [kV]"]/df_FINAL['Vnom [kV]']
  

    nuevo_df2 =df_filtrado2["Device"] 
    # Esto entrega la tabla de resultados de todas las centrales del HTML
    
    df_Resultados2 = pd.concat([nuevo_df2, df_FINAL], axis=1)



    #---------------------------- saco los acentos 
    #df_Resultados['Name1'] = df_Resultados['Name1'].apply(lambda x: unidecode(x))
    #df_Resultados['Name2'] = df_Resultados['Name2'].apply(lambda x: unidecode(x))


    ##------------------------------------------------------------------------------------------
   
    # que me entregue las columnas de 3 en 3
    df_Resultados2 = df_Resultados2.iloc[::3]
    #reseteo los indices 
    df_Resultados2 = df_Resultados2.reset_index(drop=True)
    #borro el nombre "Load_a del string de su"
    df_Resultados2['Device'] = df_Resultados2['Device'].str.replace('/Load_a', '', regex=False)
    

    Tabla_LF_cargas= pd.DataFrame(df_Resultados2)



    ## Escribo Excel--------------------------------------------------------------- 
    c=c+1
    archivo= archivo.replace('.html', '')

    Nombre_del_archivo="Datos"+str(c)+"_"+archivo
    with pd.ExcelWriter(Nombre_del_archivo+'.xlsx') as writer:
        Tabla_LF_GEN.to_excel(writer, sheet_name='DataGEN'+str(c),index=False) 
        Tabla_LF_cargas.to_excel(writer, sheet_name='LFcargas'+str(c),index=False)   
    