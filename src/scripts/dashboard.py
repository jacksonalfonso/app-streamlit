import streamlit as st
import pandas as pd
import numpy as np
import locale
from main import buscaDados
import altair as alt


##################################################################################
#### SETUP
##################################################################################

# Definir o locale para o Brasil
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
st.set_page_config(page_title="Dashboard Despesas", 
                page_icon="",
                layout="wide")

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
        data = data[data['Mês'].isin(meses_selecionados)]
    if fornecedores_selecionados != 'Todos':
        data = data[data['Nome Fornecedor'] == fornecedores_selecionados]
    if empenhos_selecionados != 'Todos':
        data = data[data['Empenho'] == empenhos_selecionados]
    
    return data

df=load_data()
dfdados = df

# st.write(dfdados)

# Filtros
todos_fornecedores = df['Nome Fornecedor'].unique().tolist()
todos_empenhos = df['Empenho'].unique().tolist()

dftemp = df.dropna(subset=['Data'])
dftemp = dftemp.sort_values(by='Data')
todos_meses = dftemp['Data'].dt.month.unique().tolist()


##################################################################################
#### UI
##################################################################################

st.title ('Dashboard Despesas Públicadas')
st.markdown("_Protótipo v0.0.1_")

# Sidebar com filtro
st.sidebar.header("Filtros")

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

# st.write(dffiltrado)

# Somar a coluna "Faturamento"
total_empenhado = dffiltrado["Valor Empenhado"].sum()
total_empenhado = locale.format_string("%.2f", total_empenhado, grouping=True)
total_liquidado = dffiltrado["Valor Liquidado"].sum()
total_liquidado = locale.format_string("%.2f", total_liquidado, grouping=True)
total_pago = dffiltrado["Valor Pago"].sum()
total_pago = locale.format_string("%.2f", total_pago, grouping=True)

#  ======================================== EMPENHADO POR MES ========================================
dftemp = dffiltrado.dropna(subset=['Data'])
dftemp = dftemp.sort_values(by='Data')
# todos_meses = dftemp['Data'].dt.strftime('%B').unique().tolist()

dftemp['ano_mes'] = dftemp['Data'].dt.to_period('M').astype(str)
df_grouped = dftemp.groupby('ano_mes')['Valor Empenhado'].sum().reset_index()

#  ======================================== FORNECEDOR ========================================
# Agrupar os dados por fornecedor e somar os valores pagos
df_groupedFornecedor = dffiltrado.groupby('Nome Fornecedor')['Valor Pago'].sum().reset_index()

# Ordenar os fornecedores pelos valores pagos em ordem decrescente e pegar os top 10
df_top_10_fornecedor = df_groupedFornecedor.sort_values(by='Valor Pago', ascending=False).head(10)
df_top_10_fornecedor['Valor Pago Formatted'] = df_top_10_fornecedor['Valor Pago'].apply(lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

# ======================================== FONTE DE RECURSO ========================================
# Agrupar os dados por fornecedor e somar os valores pagos
sCampoAgrupador = 'Fonte de Recurso'
df_groupedFonte = dffiltrado.groupby('Fonte de Recurso')['Valor Empenhado'].sum().reset_index()

# Ordenar os fornecedores pelos valores pagos em ordem decrescente e pegar os top 10
df_top_10_fonteRecurso = df_groupedFonte.sort_values(by='Valor Empenhado', ascending=False).head(10)
df_top_10_fonteRecurso['Valor Empenhado Formatted'] = df_top_10_fonteRecurso['Valor Empenhado'].apply(lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div style="background-color:#f5f5f5;padding:8px;border-radius:10px;text-align:center">
            <h5>Total Empenhado</h5>
            <h3 style="color:green;">{total_empenhado}</h3>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div style="background-color:#f5f5f5;padding:8px;border-radius:10px;text-align:center">
            <h5>Total Liquidado</h5>
            <h3 style="color:green;">{total_liquidado}</h3>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div style="background-color:#f5f5f5;padding:8px;border-radius:10px;text-align:center">
            <h5>Total Pago</h5>
            <h3 style="color:green;">{total_pago}</h3>
        </div>
    """, unsafe_allow_html=True)


st.divider()

# #  ======================================== EMPENHADO POR MES ========================================
# Criar o gráfico de barras com altair
chart = alt.Chart(df_grouped).mark_bar().encode(
    x=alt.X('ano_mes:N'),
    y=alt.Y('Valor Empenhado'),
    # color='Valor Empenhado',
    color=alt.Color('Valor Empenhado', legend=None)
).properties(
    title='Valor Empenhado por Ano-Mês'
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
    y=alt.Y(f'{sCampoAgrupador}:N'),
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
    y=f'{sCampoAgrupador}:N',         # Valores pagos no eixo Y
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
