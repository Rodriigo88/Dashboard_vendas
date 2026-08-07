import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data

def converte_csv(df):
    return df.to_csv(index=False,sep=';').encode('utf-8')


def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!',icon='✅')
    time.sleep(5)
    sucesso.empty()


st.set_page_config(layout='wide')
st.title('Dados Brutos')

url = 'https://labdados.com/produtos'
response = requests.get(url)
dados_vendas = pd.DataFrame.from_dict(response.json())
dados_vendas['Data da Compra'] = pd.to_datetime(dados_vendas['Data da Compra'], format=r'%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas',list(dados_vendas.columns),list(dados_vendas.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos',dados_vendas['Produto'].unique(),dados_vendas['Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco_produto = st.slider('Selecione o preço',0,5000,(0,5000))
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data',(dados_vendas['Data da Compra'].min(),dados_vendas['Data da Compra'].max()))
with st.sidebar.expander('Categoria do produto'):
    categoria_compra = st.multiselect('Selecione a categoria do produto',dados_vendas['Categoria do Produto'].unique(),dados_vendas['Categoria do Produto'].unique())

frete_max = int(dados_vendas['Frete'].max())
with st.sidebar.expander('Preço do frete'):
    preco_frete = st.slider('Selecione o preço do frete',0,frete_max,(0,frete_max))
with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecione o vendedor',dados_vendas['Vendedor'].unique(),dados_vendas['Vendedor'])
with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o local da compra',dados_vendas['Local da compra'].unique(),dados_vendas['Local da compra'].unique())

ava_max = int(dados_vendas['Avaliação da compra'].max())
with st.sidebar.expander('Avaliação da compra'):   
    avaliacao_compra = st.slider('Selecione a avaliação',0,ava_max,(0,ava_max))
with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',dados_vendas['Tipo de pagamento'].unique(),dados_vendas['Tipo de pagamento'].unique())

qtd_parcelas_max = int(dados_vendas['Quantidade de parcelas'].max())
with st.sidebar.expander('Quantidade de parcelas'):
        qtde_parcelas = st.slider('Selecione a quantidade de parcelas',0,qtd_parcelas_max,(0,qtd_parcelas_max))

filtro = '''
Produto in @produtos and \
@preco_produto[0] <= Preço <= @preco_produto[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
`Categoria do Produto` in @categoria_compra and \
@preco_frete[0] <= Frete <= @preco_frete[1] and \
Vendedor in @vendedor and \
`Local da compra` in @local_compra and \
`Avaliação da compra` in @avaliacao_compra and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtde_parcelas[0] <= `Quantidade de parcelas` <= @qtde_parcelas[1]
'''

dados_filtrados = dados_vendas.query(filtro)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')
st.markdown('Esvreva um nome para o arquivo')
coluna1,coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('',label_visibility='collapsed',value='dados')
    nome_arquivo += '.csv'
with coluna2:   
    st.download_button(label='Fazer download da tabela em csv',data=converte_csv(dados_filtrados), file_name=nome_arquivo,mime='text/csv',on_click=mensagem_sucesso())