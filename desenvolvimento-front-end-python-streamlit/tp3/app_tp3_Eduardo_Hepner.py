import io
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

#####################################################################################
# Uso do auxílio de IA:
#  - Tag de identificação de um XLS: "application/vnd.ms-excel"
#  - Processo de salvamento em .XLS: writer
#  - Entender como mudar a cor do fundo e da fonte para que pudesse usar a cor
#    escolhida no color picker, além de entender o parâmetro 'key' do color picker
#    (e demais widgets) e sua relação com o session state
#  - Ordenar os meses no X do st.line_chart, que estava trocando pra ordem alfabética
#####################################################################################

#####################################################################################
# 1 - Escolha dos Datasets e Explicação do Objetivo e Motivação:
# Escolha um ou mais datasets do portal Data Rio. Explique o objetivo e a motivação
# por trás da escolha dos dados e quais funcionalidades e visualizações serão
# implementadas.
#
# R. Foram escolhidos datasets provenientes do portal Data.Rio seção turismo,
# conforme instrução no enunciado, relacionados à quantidade e origem de visitantes
# do Rio de Janeiro, pelas vias marítima e aérea. Escolhi esses dois datasets pois
# apresentam a mesma estrutura e, dessa forma, o tratamento dos dados pode ser feito
# de forma que funcione para ambos.
#####################################################################################


st.set_page_config(page_title="TP3 - App Turismo", page_icon="🏝️")
icon_aereo = "✈️"
icon_maritimo = "🚢"

MESES = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]


#####################################################################################
# 8 - Utilizar Funcionalidade de Cache:
# Utilize a funcionalidade de cache do Streamlit para armazenar os dados carregados
# dos arquivos XLS, evitando a necessidade de recarregá-los a cada nova interação.
#####################################################################################
@st.cache_data(ttl=600, show_spinner=False)
def processar_xls(arquivo):
    time.sleep(3)  # para visualização do spinner
    n = 0
    df = pd.read_excel(arquivo, header=None, sheet_name=n)
    aba = pd.ExcelFile(arquivo).sheet_names[n]
    titulo = df.loc[2, 0].split(" - ")
    titulo = f"{titulo[1]} - {titulo[2]} - {aba}"
    if "aérea" in titulo:
        icone = icon_aereo
    elif "marítima" in titulo:
        icone = icon_maritimo
    else:
        icone = "🏝️"
    titulo = f"{icone} {titulo}"

    df = df.loc[7:, :].reset_index(drop=True)
    # tratamento do arquivo
    df.columns = [
        "País",
        "Total",
        *MESES,
    ]

    # tirando linha total
    df = df.drop(0)

    # tirando coluna total
    df = df.drop(columns=["Total"])  # df.drop('Total', axis=1)

    # # tirando fim do arquivo
    df = df.iloc[:62, :].reset_index(drop=True)

    # substituindo o - por 0 para transformar o tipo da coluna para numerico
    df = df.replace("-", 0)
    df[df.columns[1:]] = df[df.columns[1:]].astype(int)

    # adicionando coluna continente
    df.loc[:5, "Continente"] = "África"
    df.loc[6:10, "Continente"] = "América Central"
    df.loc[11:14, "Continente"] = "América do Norte"
    df.loc[15:27, "Continente"] = "América do Sul"
    df.loc[28:32, "Continente"] = "Ásia"
    df.loc[33:52, "Continente"] = "Europa"
    df.loc[53:55, "Continente"] = "Oceania"
    df.loc[56:60, "Continente"] = "Oriente Médio"
    df.loc[61, "Continente"] = "Não especificado"

    # tirando linhas de continentes
    df = df.drop([0, 6, 11, 15, 28, 33, 53, 56])
    df = df[
        [
            "Continente",
            "País",
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        ]
    ]

    # removendo espaços adicionais
    df["País"] = df["País"].str.strip()

    df = df.set_index(["Continente"])
    #####################################################################################
    # 6 - Utilizar Barra de Progresso:
    # Adicione uma barra de progresso para indicar o carregamento dos dados enquanto o
    # arquivo XLS é processado e exibido na interface.
    #####################################################################################
    # para visualização da barra
    barra = st.progress(0.2, "Progresso", 100)
    i = 0
    for i in range(1, 101, 5):
        time.sleep(0.1)
        barra.progress(i, f"Loading: {i}%...", 100)
    barra.empty()
    return titulo, df


def grafico_linhas(df):
    if "País" in df.columns:
        filtro = df["País"] == "Outros"
        df.loc[filtro, "País"] = f"Outros - " + df.loc[filtro].index
        df = df.reset_index(drop=True).set_index("País")
    df = df.T
    df.index = pd.Categorical(df.index, categories=df.index, ordered=True)
    return st.line_chart(df)


def processar_comparativo(df, opcoes):
    paises = []
    continentes = []
    for i in opcoes:
        if i in df["País"].values:
            paises.append(i)
        else:
            continentes.append(i)
    df_comp = df[df["País"].isin(paises)].reset_index(drop=True)
    df_comp = df_comp.rename(columns={"País": "Localidade"})

    if continentes:
        df_continentes = df[MESES].groupby(df.index, sort=False).sum()
        df_continentes = (
            df_continentes.loc[continentes]
            .reset_index()
            .rename(columns={"Continente": "Localidade"})
        )
        df_comp = pd.concat([df_comp, df_continentes], ignore_index=True)

    df_comp = df_comp.reset_index(drop=True).set_index("Localidade")
    return df_comp


# Cores padrão do Streamlit
COR_FUNDO_DEFAULT = "#FFFFFF"
COR_TEXTO_DEFAULT = "#31333F"


def restaurar_cores():
    st.session_state["cor_fundo"] = COR_FUNDO_DEFAULT
    st.session_state["cor_texto"] = COR_TEXTO_DEFAULT


st.title("TP3 - Desenvolvimento Front-End com Python (com Streamlit)")

#####################################################################################
# 9 - Persistir Dados Usando Session State:
# Implemente a persistência de dados na aplicação utilizando Session State para
# manter as preferências do usuário (seleções e filtros escolhidos) durante a
# navegação.
#####################################################################################
#####################################################################################
# 7 - Utilizar Color Picker:
# Adicione um color picker à interface que permita ao usuário personalizar a cor de
# fundo do painel e das fontes exibidas na aplicação.
#####################################################################################
if "cor_fundo" not in st.session_state:
    st.session_state["cor_fundo"] = COR_FUNDO_DEFAULT

if "cor_texto" not in st.session_state:
    st.session_state["cor_texto"] = COR_TEXTO_DEFAULT

col1, col2, col3, col4 = st.columns([0.15, 0.15, 1, 1], vertical_alignment="bottom")
with col1:
    st.color_picker("Cor do fundo", key="cor_fundo")

with col2:
    st.color_picker("Cor do texto", key="cor_texto")

with col3:
    st.button("Restaurar", on_click=restaurar_cores)


st.markdown(
    f"""
<style>
    .stApp {{
        background-color: {st.session_state['cor_fundo']};
        color: {st.session_state['cor_texto']};
    }}

    h1, h2, h3 {{
        color: {st.session_state['cor_texto']};
    }}
</style>
""",
    unsafe_allow_html=True,
)


st.subheader("📋 Faça upload do seus arquivos .xls:")


#####################################################################################
# 2 - Realizar Upload de Arquivo XLS:
# Crie uma interface em Streamlit que permita ao usuário fazer o upload de um arquivo
# XLS contendo dados de turismo do portal Data.Rio.
#####################################################################################

arquivos = st.file_uploader(
    "Carregar Arquivos", type=["xls"], accept_multiple_files=True
)

#####################################################################################
# 3 - Filtro de Dados e Seleção:
# Exiba o dataset para o usuário e implemente três seletores diferentes (radio,
# checkbox, dropdowns) na interface que permitam ao usuário filtrar os dados
# carregados e selecionar as colunas ou linhas que deseja visualizar.
#####################################################################################
if arquivos:
    options = [arquivos[i].name for i in range(len(arquivos))]

    # Seletor 1: selectbox dropdown
    selecionado = st.selectbox(
        "Selecione o arquivo: ", options, key="arquivo_selecionado"
    )

    for arquivo in arquivos:
        if arquivo.type != "application/vnd.ms-excel":
            st.write("Tipo de arquivo não suportado!")
        elif arquivo.name == selecionado:
            #####################################################################################
            # 6 - Utilizar Spinner:
            # Adicione um spinner para indicar o carregamento dos dados enquanto o arquivo XLS
            # é processado e exibido na interface.
            #####################################################################################
            with st.spinner("Processando..."):
                titulo, df = processar_xls(arquivo)
            st.header(titulo)

            # Seletor 2: checkbox
            option_continentes = st.checkbox(
                "Apenas continentes", key="apenas_continentes"
            )

            st.header("Visão geral")
            df_filtrado = (
                df[MESES].groupby(df.index, sort=False).sum()
                if option_continentes
                else df
            )

            m1, m2, m3 = st.columns(3)

            with m1:
                metric_continentes = st.empty()

            with m2:
                metric_paises = st.empty()

            with m3:
                metric_visitantes = st.empty()

            # Seletor 3: multiselect
            continentes = df_filtrado.index.unique()

            selecao_continente = st.multiselect(
                "Selecione os continentes:",
                continentes,
                default=continentes,
                key="continentes_selecionados",
                label_visibility="collapsed",
            )

            if not selecao_continente:
                st.warning("Selecione pelo menos um continente.")
                # st.stop()
            else:
                df_filtrado = df_filtrado.loc[selecao_continente]

                #####################################################################################
                # 9 - Persistir Dados Usando Session State:
                # Implemente a persistência de dados na aplicação utilizando Session State para
                # manter as preferências do usuário (seleções e filtros escolhidos) durante a
                # navegação.
                #####################################################################################
                n_continentes = len(df_filtrado.index.unique())
                if "continentes_old" not in st.session_state:
                    st.session_state["continentes_old"] = n_continentes
                #####################################################################################
                # 12 - Exibir Métricas Básicas:
                # Implemente a exibição de métricas básicas (como contagem de registros, médias,
                # somas) diretamente na interface para fornecer um resumo rápido dos dados
                # carregados.
                #####################################################################################
                metric_continentes.metric(
                    "Continentes",
                    n_continentes,
                    delta=n_continentes - st.session_state["continentes_old"],
                )
                st.session_state["continentes_old"] = n_continentes

                n_paises = len(df.loc[selecao_continente]["País"])
                if "paises_old" not in st.session_state:
                    st.session_state["paises_old"] = n_paises
                metric_paises.metric(
                    "Países", n_paises, delta=n_paises - st.session_state["paises_old"]
                )
                st.session_state["paises_old"] = n_paises

                total = df_filtrado[MESES].sum().sum()
                if "total_old" not in st.session_state:
                    st.session_state["total_old"] = total
                metric_visitantes.metric(
                    "Visitantes anuais",
                    f"{total:,}".replace(",", "."),
                    delta=total - st.session_state["total_old"],
                )
                st.session_state["total_old"] = total

                #####################################################################################
                # 4 - Criar Visualizações de Dados - Tabelas:
                # Crie uma tabela interativa que exiba os dados filtrados de acordo com os seletores
                # carregados e permita ao usuário ordenar e filtrar as colunas diretamente pela
                # interface.
                #####################################################################################
                st.dataframe(df_filtrado)

                #####################################################################################
                # 5 - Desenvolver Serviço de Download de Arquivos:
                # Implemente um serviço que permita ao usuário fazer o download dos dados filtrados
                # em formato XLS diretamente pela interface da aplicação.
                #####################################################################################
                buffer = io.BytesIO()
                df_filtrado.to_excel(buffer)
                st.download_button(
                    "📥 Download", buffer.getvalue(), "visitantes_rj.xlsx"
                )

                st.divider()
                st.subheader("Linha do tempo")

                grafico_linhas(df_filtrado)

                st.divider()
                st.subheader("Distribuição")
                #####################################################################################
                # 11 - Criar Visualizações de Dados - Gráficos Avançados:
                # Adicione gráficos avançados (histograma e scatter plot) para fornecer insights mais
                # profundos sobre os dados.
                #####################################################################################
                df_hist = df_filtrado.copy()
                df_hist["Total"] = df_hist[MESES].sum(axis=1)
                fig = px.histogram(df_hist, x="Total", nbins=10)
                st.plotly_chart(fig)

                st.divider()

            st.header("Comparativos")

            if st.session_state["apenas_continentes"]:
                opcoes_comparar = df.index.unique()
            else:
                opcoes_comparar = sorted(df["País"].unique())

            # opcoes_comparar = [
            #     item
            #     for item in opcoes_comparar
            #     if item not in st.session_state["comparativo"]
            # ]

            if "comparativo" not in st.session_state:
                st.session_state["comparativo"] = []

            col1, col2, col3, col4 = st.columns(
                [3, 2, 2, 6], vertical_alignment="bottom"
            )
            with col1:
                opcao = st.selectbox("Escolha a localidade:", options=opcoes_comparar)
            with col2:
                if (st.button("Adicionar")) and (
                    opcao not in st.session_state["comparativo"]
                ):
                    st.session_state["comparativo"].append(opcao)
            with col3:
                if st.button("Limpar"):
                    st.session_state["comparativo"] = []

            if st.session_state["comparativo"]:
                df_comp = processar_comparativo(df, st.session_state["comparativo"])

                #####################################################################################
                # 10 - Criar Visualizações de Dados - Gráficos Simples:
                # Desenvolva gráficos simples (barras, linhas, e pie charts) para visualização dos
                # dados carregados, utilizando o Streamlit.
                #####################################################################################
                st.subheader("Visitantes totais por localidade")
                col_bar, col_pie = st.columns(2, vertical_alignment="top")

                with col_bar:
                    df_comp_sum = df_comp.sum(axis=1)
                    st.bar_chart(df_comp_sum)

                with col_pie:
                    fig = px.pie(
                        df_comp_sum, names=df_comp_sum.index, values=df_comp_sum.values
                    )
                    st.plotly_chart(fig)

                st.divider()
                st.subheader("Visitantes por mês")

                mes1, mes2 = st.columns(2, vertical_alignment="top")
                with mes1:
                    opcao1 = st.selectbox(
                        "Escolha o primeiro mês:", options=MESES, index=0
                    )
                with mes2:
                    opcao2 = st.selectbox(
                        "Escolha o segundo mês:", options=MESES, index=1
                    )

                fig = px.scatter(df_comp, x=opcao1, y=opcao2, hover_name=df_comp.index)
                st.plotly_chart(fig)

else:
    st.write("Nenhum arquivo foi carregado!")
