import pandas as pd
import plotly.express as px
import streamlit as st
import requests

url = 'https://labdados.com/produtos'
regioes = ['Brasil','Centro-Oeste','Nordeste','Norte','Sudeste','Sul']
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região',regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período',value=True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano',2020,2023)

query_string = {'regiao':regiao.lower(),'ano':ano}
response = requests.get(url,params=query_string)
dados_vendas = pd.DataFrame.from_dict(response.json())
dados_vendas['Data da Compra'] = pd.to_datetime(dados_vendas['Data da Compra'],format=r'%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores',dados_vendas['Vendedor'].unique())

if filtro_vendedores:
    dados_vendas = dados_vendas[dados_vendas['Vendedor'].isin(filtro_vendedores)]

st.set_page_config(layout="wide",initial_sidebar_state='expanded',page_title='DASHBOARD DE VENDAS')
st.title('DASHBOARD DE VENDAS 🛒')


def formata_receita(numero,prefixo=''):
    for unidade in ['', 'mil']:
        if numero <1000:
            return f'{prefixo} {numero:.2f} {unidade}'
        numero /= 1000
    return f'{prefixo} {numero:.2f} milhões'

## Tabelas
# Tabelas Receita
receitas_estados = dados_vendas.groupby('Local da compra')[['Preço']].sum()
receitas_estados = dados_vendas.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(receitas_estados,left_on='Local da compra',right_index=True).sort_values('Preço',ascending=False)
contagem_estados = dados_vendas.groupby('Local da compra')[['Preço']].count()

receitas_mensais = dados_vendas.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receitas_mensais['Ano'] = receitas_mensais['Data da Compra'].dt.year
receitas_mensais['Mês'] = receitas_mensais['Data da Compra'].dt.month_name()

receita_categoria = dados_vendas.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço',ascending=False)
# Tabelas Vendedores
maiores_vendedores = dados_vendas.groupby('Vendedor')['Preço'].agg(['sum','count'])

# Tabelas contagem
contagem_estados = dados_vendas.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(contagem_estados,left_on='Local da compra',right_index=True).sort_values('Preço',ascending=False)
contagem_estados = contagem_estados.rename(columns={'Preço': 'Contagem'})

contagem_mensal = dados_vendas.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count().reset_index()
contagem_mensal['Ano'] = contagem_mensal['Data da Compra'].dt.year
contagem_mensal['Mês'] = contagem_mensal['Data da Compra'].dt.month_name()

contagem_categoria = dados_vendas.groupby('Categoria do Produto',as_index=False)['Preço'].count().sort_values('Preço',ascending=False)
## Gráficos

fig_mapa_receita = px.scatter_geo(data_frame=receitas_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_data={'lat':False,'lon':False},
                                  hover_name='Local da compra',
                                  title='Receita por estado')

fig_receita_mensal  = px.line(receitas_mensais,
                              x='Mês',y='Preço',
                              markers=True,
                              range_y=(0,receitas_mensais.max()),
                              color='Ano',title='Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estados = px.bar(receitas_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='TOP Estados maior receita')
fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categoria = px.bar(receita_categoria,
                               x=receita_categoria.index,
                               y='Preço',
                               text_auto=True,
                               title='Receita por categoria')
fig_receita_categoria.update_layout(yaxis_title = 'Receita')
##
fig_contagem_mapa = px.scatter_geo(contagem_estados,
                         lat='lat',
                         lon='lon',
                         scope='south america',
                         size='Contagem',
                         template='seaborn',
                         hover_data={'lat': False,'lon': False},
                         hover_name='Local da compra',
                         title='Contagem de vendas por estado')

fig_contagem_mensal = px.line(contagem_mensal,
                             x='Mês',
                             y='Preço',
                             color='Ano',markers=True,
                             range_y=(0,receita_categoria.max()),                             
                             title='Quantidade de vendas mensal')

fig_top_contagem_mensal = px.bar(contagem_estados.head(),
                                 x='Local da compra',y='Contagem',text_auto=True,title='Top Estados com mais vendas')

fig_contagem_categoria = px.bar(contagem_categoria,
                                x='Preço',y='Categoria do Produto',text_auto=True,title='Categorias mais vendidas')
fig_contagem_categoria.update_yaxes(autorange='reversed')


## Visão Streamlit    
aba1,aba2,aba3 = st.tabs(['Receita','Quantidade de vendas','Vendedores'])


with aba1:
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita total',formata_receita(dados_vendas['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita)
        st.plotly_chart(fig_receita_estados)
    with coluna2:
        st.metric('Quantidade de vendas',formata_receita(dados_vendas.shape[0]))
        st.plotly_chart(fig_receita_mensal)
        st.plotly_chart(fig_receita_categoria)

with aba2:
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita total',formata_receita(dados_vendas['Preço'].sum(),'R$'))
        st.plotly_chart(fig_contagem_mapa)
        st.plotly_chart(fig_top_contagem_mensal)
    with coluna2:
        st.metric('Quantidade de vendas',formata_receita(dados_vendas.shape[0]))
        st.plotly_chart(fig_contagem_mensal)
        st.plotly_chart(fig_contagem_categoria)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores',2,10,5)
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita total',formata_receita(dados_vendas['Preço'].sum(),'R$'))
        fig_receita_vendedores = px.bar(maiores_vendedores[['sum']].sort_values('sum',ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y=maiores_vendedores[['sum']].sort_values('sum',ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title='Maiores vendedores')
        fig_receita_vendedores.update_layout(yaxis_title='Vendedores').update_yaxes(autorange='reversed')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de vendas',formata_receita(dados_vendas.shape[0]))
        fig_contagem_vendedores = px.bar(maiores_vendedores[['count']].sort_values('count',ascending=False).head(qtd_vendedores),
                                        y=maiores_vendedores[['count']].sort_values('count',ascending=False).head(qtd_vendedores).index,
                                        x='count',
                                        text_auto=True,
                                        title='Piores vendedores')
        fig_contagem_vendedores.update_layout(yaxis_title='Vendedores')
        st.plotly_chart(fig_contagem_vendedores)
        



