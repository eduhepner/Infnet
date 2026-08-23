# -----------------------------------------------------

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import pydeck as pdk
import seaborn as sns
import streamlit as st
from plotly.subplots import make_subplots

file1 = pd.read_csv(
    "./tp2/HIST_PAINEL_COVIDBR_2021_Parte1_05set2025.csv", sep=";", encoding="utf-8"
)
file2 = pd.read_csv(
    "./tp2/HIST_PAINEL_COVIDBR_2021_Parte2_05set2025.csv", sep=";", encoding="utf-8"
)
df = pd.concat([file1, file2], ignore_index=True)

st.markdown(
    "### 1 - Importância da Visualização de Dados: Explique a importância da visualização de dados no contexto de uma pandemia como a COVID-19. \
            Como essas visualizações podem ajudar gestores de saúde pública e a população em geral a tomar decisões informadas?"
)

st.text(
    "R. Muitas vezes as informações, por mais que estejam lá, não são tão claras. Com gráficos há uma maior facilidade de analisar e ver tendências, \
tornando a análise mais fácil de ser feita e interpretada. Junto a isso temos o fato de que, como no caso em questão da COVID-19, as pessoas que \
tem essas informações vão precisar transmití-las para pessoas sem um conhecimento técnico de análise, e com gráficos isso fica muito mais fácil, \
ajudando nessa comunicação e auxiliando os médicos e gestores a enxergarem a real situação e as tendências da epidemia para que pudessem tomar \
as melhores decisões em relação a isso."
)


st.title("Painel COVID-19")
st.header("Informações da pandemia no ano 2021")

st.dataframe(df)

st.divider()

# 2 - Gráfico de Barras com Streamlit: Usando os dados de casos novos de COVID-19 por semana epidemiológica de notificação, crie um gráfico
#  de barras em Streamlit que mostre a evolução semanal dos casos em um determinado estado. Indique o estado escolhido e explique sua escolha.

st.subheader("Evolução semanal de casos para o Estado do Rio de Janeiro")

df_rj = df[(df["estado"] == "RJ") & (df["codmun"].isna())]
df_rj = df_rj.groupby("semanaEpi")["casosNovos"].sum().reset_index()
st.bar_chart(df_rj, x="semanaEpi", y="casosNovos")
# R. Foi escolhido o estado do Rio de Janeiro por ser meu Estado, além de ter uma grande população urbana, o que ajuda a ter uma análise mais robusta.

st.divider()
# 3 - Gráfico de Linha com Streamlit: Crie um gráfico de linha utilizando Streamlit para representar o número de óbitos acumulados por COVID-19
#  ao longo das semanas epidemiológicas de notificação para todo o Brasil. Explique como a curva de óbitos acumulados pode ser interpretada.

st.subheader("Número acumulado de óbitos por semana no país")
st.line_chart(
    df[df["regiao"] == "Brasil"].groupby(["semanaEpi"])["obitosAcumulado"].max()
)
# R. Uma vez que são óbitos acumulados, é natural que a linha esteja sempre em uma ascendente, e podemos ver que isso se acentua a partir da semana 10.
# Entretanto, podemos ver que na semana 53 a linha tem uma queda brusca para um nível abaixo do inicial, o que indica erro nos dados. Se verificarmos
# os dados, podemos ver que a semana 53 é, na verdade, o início do ano, nos dias 1 e 2 de janeiro.

st.divider()
# 4 - Gráfico de Área com Streamlit: Utilizando os dados de casos acumulados por COVID-19, crie um gráfico de área em Streamlit para comparar a
# evolução dos casos em três estados diferentes. Explique as diferenças observadas entre os estados escolhidos.

st.subheader("Evolução comparativa de casos entre RJ, SP e MG")
df_q4 = df[(df["estado"] == "RJ") | (df["estado"] == "SP") | (df["estado"] == "MG")]
df_q4 = df_q4.groupby(["data", "estado"])["casosAcumulado"].max().reset_index()

st.area_chart(df_q4, x="data", y="casosAcumulado", color="estado")
# R. Podemos notar que São Paulo, estado mais populoso do Brasil, domina o gráfico, até prejudicando a visualização dos demais estados. Entretando notamos, de forma
# geral, um aumento progressivo no número acumulado de casos dos três Estados, que desacelera nas semanas finais do ano. Enquanto SP está disparado na frente,
# RJ e MG começam muito próximos, e vão se afastando ao longo do ano, com MG tendo mais casos que o RJ ao longo do tempo.

st.divider()
# 5 - Mapa com Streamlit: Crie um mapa interativo utilizando a função st.map do Streamlit que mostre a distribuição dos casos acumulados de COVID-19
#  por município em um estado específico. Explique como esse tipo de visualização pode ajudar na análise geográfica da pandemia.

st.subheader("As 5 principais cidades do RJ em casos acumulados")

df_q5 = df[(df["estado"] == "RJ") & (df["codmun"].notna())]
df_q5 = df_q5.groupby("municipio")["casosAcumulado"].max()
df_q5 = df_q5.sort_values(ascending=False).head(5).reset_index()

latitudes = {
    "Rio de Janeiro": -22.9068,
    "São Gonçalo": -22.8269,
    "Niterói": -22.8960,
    "Campos dos Goytacazes": -21.7657,
    "Volta Redonda": -22.4830,
}

longitudes = {
    "Rio de Janeiro": -43.1729,
    "São Gonçalo": -43.0545,
    "Niterói": -43.2076,
    "Campos dos Goytacazes": -41.3239,
    "Volta Redonda": -44.1040,
}

df_q5["latitude"] = df_q5["municipio"].map(latitudes)
df_q5["longitude"] = df_q5["municipio"].map(longitudes)
# tinha ficado completamente desproporcional, tentei o log e ficaram todos praticamente iguais
# então usei a raiz que mostrou alguma diferença ao aproximar
df_q5["casosAcumulado"] = np.sqrt(df_q5["casosAcumulado"])

st.map(
    df_q5,
    latitude="latitude",
    longitude="longitude",
    size="casosAcumulado",
)

# R. Esse tipo de visualização, onde conseguimos ver a disribuição dos casos no mapa, ajuda a perceber e identificar os principais
# focos da doença, ou seja, áreas que necessitam de mais atenção. Dessa forma é possível fazer um combate mais focado da doença
# nas localidades onde é necessário. Também ajuda identificar, de acordo com a localidade e suas especificidades,  possíveis fatores
# que podem estar contribuindo  para a disseminação da doença.


st.divider()
# 6 - Visualização com Matplotlib: Utilize a biblioteca Matplotlib para criar um gráfico de barras que mostre a comparação entre os casos novos e os
# óbitos novos de COVID-19 por estado na semana epidemiológica mais recente disponível. Explique o que os dados sugerem sobre a relação entre casos e óbitos.

st.subheader("Comparação entre os casos novos e óbitos novos mais recentes")

df_q6 = pd.read_csv(
    "./tp2/HIST_PAINEL_COVIDBR_2025_Parte2_05set2025.csv", sep=";", encoding="utf-8"
)
df_q6 = df_q6[df_q6["semanaEpi"] == df_q6["semanaEpi"].max() - 1]
df_q6 = df_q6[(df_q6["codmun"].isna()) & (df_q6["coduf"] != 76)][
    ["estado", "casosNovos", "obitosNovos"]
].sort_values("estado")
df_q6 = df_q6.groupby("estado").sum().reset_index()
# coloquei log apenas pra conseguir enxergar e responder, pois a escala estava muito diferente
df_q6["casosNovos"] = np.log1p(df_q6["casosNovos"])
df_q6["obitosNovos"] = np.log1p(df_q6["obitosNovos"])

fig, ax = plt.subplots()
df_q6.plot(kind="bar", x="estado", y=["casosNovos", "obitosNovos"], ax=ax)

st.pyplot(fig)

# R. Uma vez que a semana epidemiológica mais recente disponível está zerada, usei a semana anterior a ela.
# Os dados sugerem que não há uma relação direta clara entre os casos e óbitos. Podemos ver que alguns estados
# apresentam um número elevado de casos, mas não registram óbitos, como por exemplo São Paulo, o estado mais populoso.
# Isso indica que a relação entre casos e óbitos não pode ser medida sem levar em conta fatores de risco, sociais,
# entre outros.

st.divider()
# 7 - Boxplot com Seaborn: Usando a biblioteca Seaborn, crie um boxplot que compare a distribuição dos casos novos de COVID-19 por semana epidemiológica
# entre três regiões do Brasil (Norte, Nordeste, Sudeste). Explique as principais diferenças observadas.

st.subheader(
    "Distribuição de novos casos por semana entre as regiões Norte, Nordeste e Sudeste"
)

df_q7 = df[
    (df["regiao"] == "Norte")
    | (df["regiao"] == "Nordeste")
    | (df["regiao"] == "Sudeste")
]
df_q7 = df_q7[df_q7["codmun"].isna()]
df_q7 = df_q7.groupby(["regiao", "semanaEpi"])["casosNovos"].sum().reset_index()

sns.set_theme(style="darkgrid")
fig, ax = plt.subplots()
sns.boxplot(data=df_q7, x="regiao", y="casosNovos")
st.pyplot(fig)

# R. Analisando o boxplot podemos notar diferenças claras. A região norte possui uma distribuição concentrada em um número baixo de casos,
# que pode ser percebido pela mediana centralizada e caixa achatada, com valores abaixo de 50 mil.
# Já a região nordeste possui uma maior variação na quantidade de novos casos a cada semana. A parte acima da mediana apresenta maior
# dispersão entre valores.
# A região sudeste possui um número mais elevado de casos no geral, onde a metade inferior dos dados apresenta maior variabilidade. Podemos
# notar, também, que 25% das semanas (Q2 ao Q3) tiveram valores elevados de casos, ficando aproximadamente entre 125 e 175 mil casos.

st.divider()
# 8 - Gráfico de Área com Altair: Crie um gráfico de área em Altair para mostrar a evolução dos casos novos de COVID-19 por semana epidemiológica de
# notificação em uma determinada região do Brasil. Explique a escolha da região e as tendências observadas nos dados.

st.subheader("Evolução semanal de novos casos na região Sudeste")

df_q8 = df[(df["regiao"] == "Sudeste") & (df["codmun"].isna())]
df_q8 = df_q8.groupby("semanaEpi")["casosNovos"].sum().reset_index()

q8_graph = alt.Chart(df_q8).mark_area().encode(x="semanaEpi", y="casosNovos")
st.altair_chart(q8_graph)

# R. Foi escolhida a região Sudeste pois é uma região altamente populosa e que sofreu grande impacto da covid.
# Podemos ver que o número de novos casos subiu e ficou relativamente estável e, a partir da semana 24, teve
# uma tendência de forte queda. Ainda podemos perceber um aumento brusco na semana 37, que logo se normaliza e volta
# a tendÇencia de queda anterior.

st.divider()
# 9 - Heatmap com Altair: Desenvolva um heatmap em Altair que mostre a correlação entre casos novos, óbitos novos e leitos hospitalares ocupados
# (caso os dados estejam disponíveis) em um determinado estado. Explique as possíveis correlações observadas.

st.subheader("Correlação entre casos novos e óbitos novos")

df_rj = df[(df["estado"] == "RJ") & (df["codmun"].isna())]
df_corr = df_rj[["casosNovos", "obitosNovos"]].corr()
df_corr = df_corr.reset_index()
df_corr = df_corr.melt(id_vars="index", var_name="coluna", value_name="correlacao")

heatmap = (
    alt.Chart(df_corr)
    .mark_rect()
    .encode(x="index:N", y="coluna:N", color="correlacao:Q")
)
st.altair_chart(heatmap)

# R. Foi identificada uma correlação de aproximadamente 0,35 entre casos novos e óbitos novos, correlação considerada fraca. Uma vez que temos
# # apenas duas variáveis, Isso significa que uma variável explica pouco a outra.


st.divider()
# 10 - Gráfico de Pizza com Plotly: Usando Plotly, crie um gráfico de pizza (pie chart) que mostre a distribuição percentual dos casos acumulados
# de COVID-19 entre as cinco regiões do Brasil. Explique o que os dados revelam sobre a distribuição geográfica dos casos.

st.subheader("Distribuição dos casos acumulados por região")

df_q10 = df[(df["regiao"] != "Brasil") & (df["codmun"].isna())]
df_q10 = df_q10.groupby(["regiao", "estado"])["casosAcumulado"].max().reset_index()
df_q10 = df_q10.groupby("regiao")["casosAcumulado"].sum().reset_index()

q10_graph = px.pie(
    df_q10,
    names=df_q10["regiao"],
    values=df_q10["casosAcumulado"],
)

st.plotly_chart(q10_graph)

# R. De acordo com o gráfico podemos perceber uma certa relação entre o número de casos por região e a população dela. A maior fatia pertence
# à região Sudeste, região mais populosa do país. Em seguida temos Nordeste e Sul que, respectivamente, são segunda e terceira regiões mais populosas.
# Isso sugere que o número de casos acompanha o número de habitantes da região.


st.divider()
# 11 - Subplots com Plotly: Crie subplots em Plotly que mostrem, lado a lado, gráficos de barras comparando os casos novos e os óbitos novos de
# COVID-19 por semana epidemiológica em duas diferentes regiões do Brasil. Explique as diferenças observadas entre as regiões.

regiao1 = "Sudeste"
regiao2 = "Norte"
st.subheader(
    f"Comparativo de casos novos e os óbitos novos por semana entre as regiões {regiao1} e {regiao2}"
)

df_q11 = df[(df["regiao"] != "Brasil") & (df["codmun"].isna())]
df_q11 = (
    df_q11.groupby(["regiao", "semanaEpi"])[["casosNovos", "obitosNovos"]]
    .sum()
    .reset_index()
)

df_q11_regiao1 = df_q11[df_q11["regiao"] == regiao1]
df_q11_regiao2 = df_q11[df_q11["regiao"] == regiao2]

fig_regiao1 = px.bar(df_q11_regiao1, x="semanaEpi", y=["casosNovos", "obitosNovos"])
fig_regiao2 = px.bar(df_q11_regiao2, x="semanaEpi", y=["casosNovos", "obitosNovos"])

fig = make_subplots(rows=1, cols=2, subplot_titles=(regiao1, regiao2))

for trace in fig_regiao1.data:
    trace.showlegend = True
    fig.add_trace(trace, row=1, col=1)

for trace in fig_regiao2.data:
    trace.showlegend = False
    fig.add_trace(trace, row=1, col=2)
st.plotly_chart(fig)

# R. De acordo com o gráfico as regiões apresentam tendências parecidas, mas números absolutos muito distantes, diferença percebida pela escala dos gráficos.
# Levando em conta essa diferença e analisando relativamente, a região norte começa com um número elevado de casos e óbitos já na semana 3, enquanto a
# região sudeste começa com o número de casos em queda e o número de óbitos baixo, ambos crescendo de forma brusca entre as semanas 12 e 15.
# Então, a região norte já começa numa descendente de casos e óbitos, enquanto a região sudeste permanece com número de casos elevados até a semana
# 24, quando os números começam a cair. Também é notável que, embora o número de casos continuasse alto na região sudeste até a semana 25, o número
# de óbitos já começou a reduzir a partir da semana 15.
# Além disso, podemos perceber um pico de novos casos na região sudeste na semana 37, enquanto na região norte há um leve aumento do número de casos
# nas semanas finais dos dados, que logo reduzem novamente.


st.divider()
# 12 - Mapa Interativo com PyDeck: Utilize PyDeck para criar um mapa interativo que mostre a densidade populacional ajustada para os casos acumulados
# de COVID-19 por município em uma determinada região do Brasil. Explique como a densidade populacional pode influenciar a disseminação da COVID-19.

regiao = "Sudeste"
df_q12 = df[(df["regiao"] == regiao) & (df["municipio"].notna())]
df_q12 = (
    df_q12.groupby(["estado", "municipio"])
    .agg({"populacaoTCU2019": "max", "casosAcumulado": "max"})
    .reset_index()
)
df_q12["por_habitante"] = (
    df_q12["casosAcumulado"] / df_q12["populacaoTCU2019"]
) * 10000

df_q12 = df_q12[df_q12["municipio"].isin(latitudes.keys())]

df_q12["latitude"] = df_q12["municipio"].map(latitudes)
df_q12["longitude"] = df_q12["municipio"].map(longitudes)

view_state = pdk.ViewState(
    latitude=df_q12["latitude"].mean(), longitude=df_q12["longitude"].mean(), zoom=7
)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_q12,
    get_position=["longitude", "latitude"],
    get_radius="por_habitante",
    get_fill_color=[255, 0, 0],
)

deck = pdk.Deck(
    map_style="road",
    initial_view_state=view_state,
    layers=[layer],
)

st.pydeck_chart(deck)


# R. Uma vez que a COVID é uma doença de alto contágio, a tendência é que, quanto maior a densidade populacional (mais pessoas em determinado espaço),
# mais pessoas compartilham o mesmo espaço. Sendo assim, uma alta densidade populacional tende a uma disseminação mais fácil, com uma quantidade maior de casos.
