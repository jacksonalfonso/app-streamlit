import streamlit as st
import pandas as pd
import numpy as np
import locale
from main import buscaDados
import altair as alt
from streamlit_extras.stylable_container import stylable_container


##################################################################################
#### SETUP
##################################################################################

# Definir o locale para o Brasil
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
st.set_page_config(page_title="Dashboard Despesas", 
                page_icon="",
                layout="wide",
                initial_sidebar_state="collapsed")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


st.sidebar.header('Dashboard Despesa `Versão 1.0`')

st.sidebar.subheader('Filtros Disponíveis')

##################################################################################
#### LOAD DATA
##################################################################################
@st.cache_data
def load_data():
    data = buscaDados()
    return data

@st.cache_data
def transform_data(data, meses_selecionados, fornecedores_selecionados, empenhos_selecionados):
    if meses_selecionados:
        data = data[data['MesNome'].isin(meses_selecionados)]
    if fornecedores_selecionados != 'Todos':
        data = data[data['Nome Fornecedor'] == fornecedores_selecionados]
    if empenhos_selecionados != 'Todos':
        data = data[data['Empenho'] == empenhos_selecionados]
    
    return data

df=load_data()
dfdados = df

# with st.expander("Dados RAW"):
#         st.write(dfdados)
       
# Filtros
todos_fornecedores = df['Nome Fornecedor'].unique().tolist()
todos_empenhos = df['Empenho'].unique().tolist()

dftemp = df.dropna(subset=['Data'])
dftemp = dftemp.sort_values(by='Data')
todos_meses = dftemp['Data'].dt.strftime('%B').unique().tolist()

exercicio_analise = dftemp['Data'].dt.year.unique()

##################################################################################
#### FILTROS E PARAMETROS
##################################################################################

st.title (f'Dashboard Despesas Publicadas - Exercício {exercicio_analise}')
st.markdown("_Protótipo v0.0.1_")

meses_selecionados = st.sidebar.multiselect(
    "Selecione um Mês",
    todos_meses,
    todos_meses,
)

# Filtro de fornecedores (selectbox)
fornecedor_selecionado = st.sidebar.selectbox(
    'Escolha um Fornecedor (ou Todos):',
    ['Todos'] + todos_fornecedores  # Adiciona a opção "Todos"
)

# Filtro de Número Empenho (selectbox)
empenho_selecionado = st.sidebar.selectbox(
    'Escolha um Empenho (ou Todos):',
    ['Todos'] + todos_empenhos
)

dffiltrado = transform_data(dfdados, meses_selecionados, fornecedor_selecionado, empenho_selecionado)

# Somar a coluna "Faturamento"

alteracao_dotacao = dffiltrado["Alteração Dotação"].sum()
alteracao_dotacao = locale.format_string("%.2f", alteracao_dotacao, grouping=True)
dotacao_inicial = dffiltrado["Dotação"].sum()
dotacao_inicial = locale.format_string("%.2f", dotacao_inicial, grouping=True)
dotacao_atualizada = dffiltrado["Dotação Atual"].sum()
dotacao_atualizada = locale.format_string("%.2f", dotacao_atualizada, grouping=True)
reforco_empenho = dffiltrado["Reforço"].sum()
reforco_empenho = locale.format_string("%.2f", reforco_empenho, grouping=True)
anulacao_dotacao = dffiltrado["Valor Anulado"].sum()
anulacao_dotacao = locale.format_string("%.2f", anulacao_dotacao, grouping=True)
dotacao_disponivel = dffiltrado["Dotação Atual"].sum()-dffiltrado["Valor Anulado"].sum()
dotacao_disponivel = locale.format_string("%.2f", dotacao_disponivel, grouping=True)

total_empenhado = dffiltrado["Valor Empenhado"].sum()
total_empenhado = locale.format_string("%.2f", total_empenhado, grouping=True)
total_liquidado = dffiltrado["Valor Liquidado"].sum()
total_liquidado = locale.format_string("%.2f", total_liquidado, grouping=True)
total_pago = dffiltrado["Valor Pago"].sum()
total_pago = locale.format_string("%.2f", total_pago, grouping=True)

#  ======================================== EMPENHADO POR MES ========================================
dftemp = dffiltrado.dropna(subset=['Data'])
dftemp = dftemp.sort_values(by='Data')

dftemp['ano_mes'] = dftemp['Data'].dt.to_period('M').astype(str)
df_grouped = dftemp.groupby('ano_mes')['Valor Empenhado'].sum().reset_index()

#  ======================================== FORNECEDOR ========================================
df_groupedFornecedor = dffiltrado.groupby('Nome Fornecedor')['Valor Pago'].sum().reset_index()

df_top_10_fornecedor = df_groupedFornecedor.sort_values(by='Valor Pago', ascending=False).head(10)
df_top_10_fornecedor['Valor Pago Formatted'] = df_top_10_fornecedor['Valor Pago'].apply(lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

# ======================================== FONTE DE RECURSO ========================================
df_groupedFonte = dffiltrado.groupby('Fonte de Recurso')['Valor Empenhado'].sum().reset_index()

df_top_10_fonteRecurso = df_groupedFonte.sort_values(by='Valor Empenhado', ascending=False).head(10)
df_top_10_fonteRecurso['Valor Empenhado Formatted'] = df_top_10_fonteRecurso['Valor Empenhado'].apply(lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

#========================================== NOME DA FUNÇÃO ===========================================
df_groupedNomeFuncao = dffiltrado.groupby('Nome da Função')['Valor Empenhado'].sum().reset_index()

st.sidebar.markdown('''
                    ----
                    🎖️ 
                    Criadores: Jackson Ribeiro & Fernando Zanardi''')

##################################################################################
#### UI
##################################################################################

col1, col2, col3, col4 = st.columns(4)
# dotacao_inicial
# dotacao_atualizada
# reforco_empenho
col1.metric('Dotação Inicial', value=f"{dotacao_inicial}")    
col2.metric('Alteração de Dotação', value=f"{alteracao_dotacao}")    
col3.metric('Dotaçao Atualizada', value=f"{dotacao_atualizada}")    
col4.metric('Dotação Disponível', value=f"{dotacao_disponivel}")    

# st.divider()

col6, col7, col8 = st.columns(3)

col6.metric('Total Empenhado', value=f"{total_empenhado}")    
col7.metric('Total Liquidado', value=f"{total_liquidado}")    
col8.metric('Total Pago', value=f"{total_pago}")    


st.divider()


col1, col2 = st.columns(2, gap='large')

with col1:
    # #  ======================================== EMPENHADO POR MES ========================================
    # Criar o gráfico de barras com altair
    chart = alt.Chart(df_grouped).mark_bar().encode(
        x=alt.X('ano_mes:N'),
        y=alt.Y('Valor Empenhado'),
        # color='Valor Empenhado',
        color=alt.Color('Valor Empenhado', legend=None)
    ).properties(
        title='Total Empenhado por Ano-Mês'
    ).configure_legend(
        titleOrient='top'  # Remover a legenda à direita
    )
    # Exibir o gráfico no Streamlit
    st.altair_chart(chart, use_container_width=True)

with col2:
        # #  ======================================== EMPENHADO POR MES ========================================
    # Criar o gráfico de barras com altair
    chart = alt.Chart(df_groupedNomeFuncao).mark_bar().encode(
        x=alt.X('Valor Empenhado:Q'),
        y=alt.Y('Nome da Função:N'),
        color=alt.Color('Valor Empenhado', legend=None)
    ).properties(
        title='Total Empenhado por Função'
    ).configure_legend(
        titleOrient='top'  # Remover a legenda à direita
    )
    # Exibir o gráfico no Streamlit
    st.altair_chart(chart, use_container_width=True)

#  ======================================== FORNECEDOR ========================================
# Criar o gráfico Altair de barras
bars = alt.Chart(df_top_10_fornecedor).mark_bar().encode(
    x=alt.X('Valor Pago:Q'),
    y=alt.Y('Nome Fornecedor:N', sort=alt.SortField('Valor Pago', order='descending'))
    
).properties(
    title='Top 10 Pagamentos por Fornecedor'
)

# Adicionar o texto (valores) nas barras
text = alt.Chart(df_top_10_fornecedor).mark_text(
    align='left',
    baseline='middle',
    dx=3  # Distância do texto em relação à barra
).encode(
    x='Valor Pago:Q',
    y='Nome Fornecedor:N',
    text='Valor Pago Formatted:N'
)

# Combinar as barras com os textos
chart = bars + text

chart = chart.configure_axis(
    grid=False,          # Se quiser desabilitar a grade também
    labelAngle=0,       # Alinha as legendas dos eixos horizontalmente
    title=None,          # Título do eixo X
    labels=True,          # Remove os rótulos do eixo X
    labelLimit=256  # Aumenta o limite de caracteres na legenda
).configure_legend(
    labelLimit=256  # Aumenta o limite de caracteres na legenda
)

# Exibir o gráfico no Streamlit
st.write(chart)


# ======================================== FONTE DE RECURSO ========================================
# Criar o gráfico Altair de barras
bars = alt.Chart(df_top_10_fonteRecurso).mark_bar().encode(
    x='Valor Empenhado:Q',         # Fornecedor no eixo X
    y=alt.Y('Fonte de Recurso:N'),
).properties(
    title='Empenhado por Fonte de Recurso'
)

# Adicionar o texto (valores) nas barras
text = alt.Chart(df_top_10_fonteRecurso).mark_text(
    align='left',
    baseline='middle',
    dx=5  # Distância do texto em relação à barra
).encode(
    x='Valor Empenhado:Q',
    y='Fonte de Recurso:N',         # Valores pagos no eixo Y
    text='Valor Empenhado Formatted:N'
)

# Combinar as barras com os textos
chart = bars + text

chart = chart.configure_axis(
    grid=False,          # Se quiser desabilitar a grade também
    labelAngle=0,       # Alinha as legendas dos eixos horizontalmente
    title=None,          # Título do eixo X
    labels=True,          # Remove os rótulos do eixo X
    labelLimit=256  # Aumenta o limite de caracteres na legenda
).configure_legend(
    labelLimit=256  # Aumenta o limite de caracteres na legenda
)

# Exibir o gráfico no Streamlit
st.write(chart)


st.divider()

with st.expander("Clique aqui para ver o Detalhamento do Movimento"):
    st.write('''
        Detalhamento dos valores, de acordo com filtros aplicados sobre os dados, para acompanhametno detalhado da despesa.
    ''')
    st.write(dffiltrado)
