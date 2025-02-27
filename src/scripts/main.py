import pandas as pd
import os
import glob

def buscaDados():
    # folder_path = 'c:\\Users\\jacks\OneDrive\\_TRABALHO\\_devProjetos\\github\\jackson.alfonso\\app-streamlit\\src\\data\\raw'
    folder_path = '.\\src\\data\\raw'

    files = glob.glob(os.path.join(folder_path, '*.csv'))

    if not files:
        print("Nenhum arquivo encontrato.")
    else:

        dfs = []

        for arquivo in files:
            
            try:
                df_tmp = pd.read_csv(arquivo,  sep=';',encoding='unicode_escape')
                
                filename = os.path.basename(arquivo)
                df_tmp['Valor Empenhado'] = df_tmp['Valor Empenhado'].str.replace('.', '').str.replace(',', '.').astype(float)
                df_tmp['Valor Anulado'] = df_tmp['Valor Anulado'].str.replace('.', '').str.replace(',', '.').astype(float)
                df_tmp['Valor Liquidado'] = df_tmp['Valor Liquidado'].str.replace('.', '').str.replace(',', '.').astype(float)
                df_tmp['Valor Pago'] = df_tmp['Valor Pago'].str.replace('.', '').str.replace(',', '.').astype(float)
                df_tmp['Dotação'] = df_tmp['Dotação'].str.replace('.', '').str.replace(',', '.').astype(float)
                df_tmp['Dotação Atual'] = df_tmp['Dotação Atual'].str.replace('.', '').str.replace(',', '.').astype(float)
                df_tmp['Empenhado até Hoje'] = df_tmp['Empenhado até Hoje'].str.replace('.', '').str.replace(',', '.').astype(float)
                df_tmp['Liquidado até Hoje'] = df_tmp['Liquidado até Hoje'].str.replace('.', '').str.replace(',', '.').astype(float)
                df_tmp['Pago até Hoje'] = df_tmp['Pago até Hoje'].str.replace('.', '').str.replace(',', '.').astype(float)
                
                
                df_tmp['Tipo'] = df_tmp['Tipo'].astype('category')
                df_tmp['N° Ficha'] = df_tmp['Tipo'].str.replace('.','').astype('category')
                df_tmp['Data'] = pd.to_datetime(df_tmp['Data'], format='%d/%m/%Y', errors='coerce') 
                df_tmp['Ano-Mês'] = df_tmp['Data'].dt.to_period('M')  # Formato YYYY-MM
                df_tmp['Ano'] = df_tmp['Data'].dt.year
                df_tmp['Mês'] = df_tmp['Data'].dt.month
                df_tmp['Dia'] = df_tmp['Data'].dt.day


                print(df_tmp.info())


                dfs.append(df_tmp)
            except Exception as e:
                print(f'Erro reportado: {e} Arquivo: {arquivo}')
                

        if dfs:
            df_matriz = pd.concat(dfs, ignore_index=True)
            print(df_matriz.info())

        return df_matriz.copy()