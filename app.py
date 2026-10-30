import altair as alt
import pandas as pd
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Spotify Songs: o que faz uma música popular?",
    layout="wide",
)

st.title("Spotify Songs: o que faz uma música popular?")

df = load_data()

# Variáveis quantitativas do estudo (mesma lista VARS_QUANT do notebook de EDA)
VARS_QUANT = ["danceability", "energy", "loudness", "speechiness", "acousticness",
              "instrumentalness", "liveness", "valence", "tempo", "duration_ms"]

# Identidade visual: mesma convenção da EDA (roxo = Popular, rosa = Não popular)
COR_POPULAR = "#6c3fa0"
COR_NAO_POPULAR = "#e9c6d4"
COR_HISTOGRAMA = COR_POPULAR
CORES_CLASSE = alt.Scale(domain=["Não popular", "Popular"], range=[COR_NAO_POPULAR, COR_POPULAR])

# Passo dos sliders por variável (as de 0 a 1 andam de 0,01; as demais têm escala própria)
PASSOS = {"loudness": 0.5, "tempo": 1.0, "duration_ms": 1000}

GENEROS = sorted(df["playlist_genre"].unique())
ANO_MIN, ANO_MAX = int(df["ano_lancamento"].min()), int(df["ano_lancamento"].max())

# Sidebar: filtros dos dois dashboards
with st.sidebar:
    st.header("Filtros")

    st.subheader("Dashboard 1: Laboratório")
    variaveis = st.multiselect(
        "Variáveis Quantitativas",
        options=VARS_QUANT,
        default=VARS_QUANT,
        help="Selecione as variáveis quantitativas que deseja analisar no laboratório.",
    )

    separar_por_classe = st.toggle(
        "Distinguir por Classe",
        value=False,
        help="Colore a distribuição pela classe (popularidade_classe: Popular ou Não popular).",
    )

    # Um slider de intervalo para cada variável selecionada (num expander, para a sidebar não ficar enorme)
    intervalos = {}
    expander_intervalos = st.expander("Intervalos das variáveis (sliders)", expanded=False)
    for var in variaveis:
        passo = PASSOS.get(var, 0.01)
        if var == "duration_ms":
            minimo, maximo, passo = int(df[var].min()), int(df[var].max()), int(passo)
        else:
            minimo, maximo = float(df[var].min()), float(df[var].max())
        intervalos[var] = expander_intervalos.slider(
            f"Intervalo de {var}",
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            step=passo,
            key=f"intervalo_{var}",
        )

    st.divider()
    st.subheader("Dashboard 2: Artista")
    generos = st.multiselect(
        "Gêneros",
        options=GENEROS,
        default=GENEROS,
        help="Gêneros das playlists que entram nos KPIs do artista.",
    )
    anos = st.slider(
        "Ano de lançamento",
        min_value=ANO_MIN,
        max_value=ANO_MAX,
        value=(ANO_MIN, ANO_MAX),
        step=1,
        help="Restringe as músicas pelo ano de lançamento do álbum.",
    )

aba_laboratorio, aba_artista = st.tabs(
    ["Dashboard 1: Laboratório de distribuição e correlação", "Dashboard 2: Painel do artista independente"]
)

# ---------------------------------------------------------------------------
# Dashboard 1: correlação (heatmap) à esquerda, distribuição (histograma) à direita
# ---------------------------------------------------------------------------
with aba_laboratorio:
    # Mantém só as músicas dentro de todos os intervalos escolhidos
    df_filtrado = df
    for var, (inicio, fim) in intervalos.items():
        df_filtrado = df_filtrado[df_filtrado[var].between(inicio, fim)]

    st.caption(f"{len(df_filtrado):,} de {len(df):,} músicas dentro dos intervalos escolhidos.".replace(",", "."))

    col_correlacao, col_distribuicao = st.columns([1.2, 1.5])

    # Legenda das classes em texto, para caber no espaço livre da grade de histogramas
    LEGENDA_CLASSE = (
        f"**Classe**  \n"
        f":color[■]{{foreground=\"{COR_NAO_POPULAR}\"}} Não popular  \n"
        f":color[■]{{foreground=\"{COR_POPULAR}\"}} Popular"
    )

    with col_correlacao:
        st.subheader("Correlação (Spearman)")

        if len(variaveis) < 2:
            st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
        elif len(df_filtrado) < 30:
            st.warning("Poucas músicas nos intervalos escolhidos para calcular a correlação.")
        else:
            # Matriz de correlação de Spearman das variáveis selecionadas, em formato longo (uma linha por célula)
            corr = (
                df_filtrado[variaveis]
                .corr(method="spearman")
                .rename_axis(index="var_y", columns="var_x")
                .stack()
                .rename("correlacao")
                .reset_index()
            )
            # Só o triângulo inferior, sem a diagonal (sempre 1): a matriz é simétrica, o resto é repetição
            ordem = {var: i for i, var in enumerate(variaveis)}
            corr = corr[corr["var_y"].map(ordem) > corr["var_x"].map(ordem)]

            # Com muitas variáveis, os rótulos do eixo X ficam inclinados e menores
            muitas = len(variaveis) > 5
            base = alt.Chart(corr).encode(
                x=alt.X(
                    "var_x:N",
                    title=None,
                    sort=variaveis[:-1],  # a última variável só aparece nas linhas
                    axis=alt.Axis(labelAngle=-45 if muitas else 0, labelFontSize=11 if muitas else 14,
                                  labelOverlap=False),
                ),
                y=alt.Y("var_y:N", title=None, sort=variaveis[1:],  # a primeira só nas colunas
                        axis=alt.Axis(labelFontSize=11 if muitas else 14, labelOverlap=False)),
            )
            heatmap = base.mark_rect().encode(
                color=alt.Color(
                    "correlacao:Q",
                    title="Spearman",
                    scale=alt.Scale(scheme="redblue", domain=[-1, 1], reverse=True),
                    legend=alt.Legend(titleFontSize=14, labelFontSize=13),
                ),
                tooltip=["var_x", "var_y", alt.Tooltip("correlacao:Q", format=".2f")],
            )
            valores = base.mark_text(fontSize=10 if muitas else 16).encode(
                text=alt.Text("correlacao:Q", format=".2f"),
                color=alt.condition(
                    "abs(datum.correlacao) > 0.5", alt.value("white"), alt.value("black")
                ),
            )

            st.altair_chart(
                (heatmap + valores).properties(height=460),
                width="stretch",
                alt="Mapa de calor (triângulo inferior, sem a diagonal) da correlação de Spearman entre as variáveis quantitativas selecionadas",
            )

    with col_distribuicao:
        st.subheader("Distribuição")

        if not variaveis:
            st.warning("Selecione pelo menos 1 variável para ver a distribuição.")
        elif df_filtrado.empty:
            st.warning("Nenhuma música dentro dos intervalos escolhidos.")
        else:
            # Com número par de variáveis não sobra espaço na grade: a legenda vai acima dela
            if separar_por_classe and len(variaveis) % 2 == 0:
                st.markdown(LEGENDA_CLASSE)

            # Um histograma por variável selecionada, em grade de 2 colunas (cada um com a sua escala)
            for inicio in range(0, len(variaveis), 2):
                colunas = st.columns(2)
                for coluna, var in zip(colunas, variaveis[inicio : inicio + 2]):
                    histograma = (
                        alt.Chart(df_filtrado[[var, "popularidade_classe"]])
                        .mark_bar()
                        .encode(
                            x=alt.X(f"{var}:Q", bin=alt.Bin(maxbins=20), title=var),
                            y=alt.Y("count()", title="Músicas"),
                            tooltip=[alt.Tooltip("count()", title="Músicas")],
                        )
                        .properties(height=200)
                    )
                    if separar_por_classe:
                        histograma = histograma.encode(
                            color=alt.Color(
                                "popularidade_classe:N",
                                title="Classe",
                                scale=CORES_CLASSE,
                                legend=None,
                            ),
                            tooltip=["popularidade_classe", alt.Tooltip("count()", title="Músicas")],
                        )
                    else:
                        histograma = histograma.mark_bar(color=COR_HISTOGRAMA)

                    with coluna:
                        st.altair_chart(histograma, width="stretch", alt=f"Histograma da variável {var}")

                # Número ímpar de variáveis: a legenda ocupa o espaço que sobrou na última linha
                if separar_por_classe and len(variaveis[inicio : inicio + 2]) == 1:
                    colunas[1].markdown(LEGENDA_CLASSE)

# ---------------------------------------------------------------------------
# Dashboard 2: KPIs para um artista independente
# ---------------------------------------------------------------------------
TAXA_HITS_GERAL = (df["popularidade_classe"] == "Popular").mean()

FAIXAS_DURACAO = [0, 2.5, 3, 3.5, 4, 4.5, float("inf")]
ROTULOS_DURACAO = ["< 2:30", "2:30–3:00", "3:00–3:30", "3:30–4:00", "4:00–4:30", "> 4:30"]

PERFIL_SONORO = {
    "danceability": "Dançabilidade",
    "energy": "Energia",
    "valence": "Valência (alegria)",
    "acousticness": "Acústica",
    "speechiness": "Fala",
    "liveness": "Ao vivo",
}


def formatar_minutos(minutos):
    """3.57 -> '3:34'."""
    total = int(round(minutos * 60))
    return f"{total // 60}:{total % 60:02d}"


def br(texto):
    """Troca o ponto decimal por vírgula: '0.68' -> '0,68'."""
    return texto.replace(".", ",")


def taxa_de_hits(serie_classe):
    return (serie_classe == "Popular").mean()


with aba_artista:
    st.subheader("Painel do artista independente")
    st.caption(
        "Para quem está produzindo e lançando a próxima faixa. "
        "**Hit** = música no quartil mais popular da base (popularidade ≥ 58 de 100). "
        "Clique numa barra de gênero para filtrar as métricas e os outros gráficos; clique fora das barras para limpar."
    )

    df_artista = df[df["playlist_genre"].isin(generos) & df["ano_lancamento"].between(*anos)]

    if df_artista.empty:
        st.warning("Nenhuma música com os gêneros e anos escolhidos. Ajuste os filtros na barra lateral.")
    else:
        # As métricas ficam no topo, mas são calculadas depois do clique no gráfico de gêneros
        area_metricas = st.container()
        col_genero, col_duracao = st.columns(2)

        # Visual 1: taxa de hits por gênero (clicável, leva a seleção para o Python)
        with col_genero:
            st.markdown("**Taxa de hits por gênero**")
            por_genero = (
                df_artista.groupby("playlist_genre")
                .agg(musicas=("track_id", "size"), taxa_hits=("popularidade_classe", taxa_de_hits))
                .reset_index()
            )
            clique = alt.selection_point(name="genero", fields=["playlist_genre"])
            barras_genero = (
                alt.Chart(por_genero)
                .mark_bar(color=COR_POPULAR)
                .encode(
                    x=alt.X("playlist_genre:N", title="Gênero",
                            sort=alt.SortField("taxa_hits", order="descending"), axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("taxa_hits:Q", title="Taxa de hits", axis=alt.Axis(format="%")),
                    opacity=alt.condition(clique, alt.value(1), alt.value(0.3)),
                    tooltip=[
                        alt.Tooltip("playlist_genre:N", title="Gênero"),
                        alt.Tooltip("taxa_hits:Q", title="Taxa de hits", format=".1%"),
                        alt.Tooltip("musicas:Q", title="Músicas"),
                    ],
                )
                .add_params(clique)
                .properties(height=300)
            )
            evento = st.altair_chart(barras_genero, key="barras_genero", on_select="rerun", width="stretch")

        # Sem seleção, a lista vem vazia e o recorte fica igual ao dos filtros da sidebar
        selecionados = [item["playlist_genre"] for item in evento.selection.get("genero", [])]
        selecionados = [g for g in selecionados if g in generos]
        df_recorte = df_artista[df_artista["playlist_genre"].isin(selecionados)] if selecionados else df_artista
        hits = df_recorte[df_recorte["popularidade_classe"] == "Popular"]
        nao_hits = df_recorte[df_recorte["popularidade_classe"] == "Não popular"]

        # Métricas (KPIs)
        with area_metricas:
            recorte = ", ".join(selecionados) if selecionados else "gêneros e anos da barra lateral"
            n_musicas = f"{len(df_recorte):,}".replace(",", ".")
            st.caption(f"Recorte atual: **{recorte}** · {n_musicas} músicas")
            if len(df_recorte) < 30:
                st.info("Poucas músicas neste recorte: as métricas abaixo podem variar muito. Interprete com cautela.")
            m1, m2, m3, m4 = st.columns(4)

            taxa = taxa_de_hits(df_recorte["popularidade_classe"])
            m1.metric(
                "Taxa de hits",
                br(f"{taxa:.1%}"),
                delta=br(f"{(taxa - TAXA_HITS_GERAL) * 100:+.1f}") + " p.p. vs. base toda",
                help="Proporção de músicas do recorte que são hits. Comparada com a taxa da base inteira (25,6%).",
            )

            if hits.empty or nao_hits.empty:
                for coluna in (m2, m3, m4):
                    coluna.metric("—", "—", help="Recorte sem hits ou sem não hits para comparar.")
            else:
                dur_hit = hits["duration_min"].median()
                dur_nao = nao_hits["duration_min"].median()
                m2.metric(
                    "Duração típica de um hit",
                    formatar_minutos(dur_hit),
                    delta=f"{(dur_hit - dur_nao) * 60:+.0f} s vs. não hits",
                    delta_color="off",
                    help="Mediana da duração dos hits, comparada com a mediana das demais músicas do recorte.",
                )
                danca_hit = hits["danceability"].median()
                m3.metric(
                    "Dançabilidade de um hit",
                    br(f"{danca_hit:.2f}"),
                    delta=br(f"{danca_hit - nao_hits['danceability'].median():+.2f}") + " vs. não hits",
                    delta_color="off",
                    help="Mediana da dançabilidade (0 a 1) dos hits, comparada com a das demais músicas.",
                )
                energia_hit = hits["energy"].median()
                m4.metric(
                    "Energia de um hit",
                    br(f"{energia_hit:.2f}"),
                    delta=br(f"{energia_hit - nao_hits['energy'].median():+.2f}") + " vs. não hits",
                    delta_color="off",
                    help="Mediana da energia (0 a 1) dos hits, comparada com a das demais músicas.",
                )

        # Visual 2: taxa de hits por faixa de duração
        with col_duracao:
            st.markdown("**Taxa de hits por duração**")
            por_duracao = (
                df_recorte.assign(faixa=pd.cut(df_recorte["duration_min"], FAIXAS_DURACAO, labels=ROTULOS_DURACAO))
                .groupby("faixa", observed=False)
                .agg(musicas=("track_id", "size"), taxa_hits=("popularidade_classe", taxa_de_hits))
                .reset_index()
            )
            por_duracao["faixa"] = por_duracao["faixa"].astype(str)
            por_duracao = por_duracao[por_duracao["musicas"] > 0]
            barras_duracao = (
                alt.Chart(por_duracao)
                .mark_bar(color=COR_POPULAR)
                .encode(
                    x=alt.X("faixa:N", title="Duração (min:seg)", sort=ROTULOS_DURACAO, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("taxa_hits:Q", title="Taxa de hits", axis=alt.Axis(format="%")),
                    tooltip=[
                        alt.Tooltip("faixa:N", title="Duração"),
                        alt.Tooltip("taxa_hits:Q", title="Taxa de hits", format=".1%"),
                        alt.Tooltip("musicas:Q", title="Músicas"),
                    ],
                )
            )
            linha_media = (
                alt.Chart(pd.DataFrame({"taxa": [taxa]}))
                .mark_rule(color=COR_NAO_POPULAR, strokeDash=[6, 4], size=2)
                .encode(y="taxa:Q", tooltip=[alt.Tooltip("taxa:Q", title="Taxa do recorte", format=".1%")])
            )
            st.altair_chart(
                (barras_duracao + linha_media).properties(height=300),
                width="stretch",
                alt="Taxa de hits por faixa de duração das músicas, com a taxa média do recorte tracejada",
            )
            st.caption("Linha tracejada: taxa de hits do recorte inteiro.")

        # Visual 3: perfil sonoro dos hits x não hits
        st.markdown("**Perfil sonoro: hits x não hits**")
        perfil = (
            df_recorte.groupby("popularidade_classe")[list(PERFIL_SONORO)]
            .mean()
            .rename(columns=PERFIL_SONORO)
            .rename_axis(columns="caracteristica")
            .stack()
            .rename("media")
            .reset_index()
        )
        barras_perfil = (
            alt.Chart(perfil)
            .mark_bar()
            .encode(
                x=alt.X("caracteristica:N", title=None, sort=list(PERFIL_SONORO.values()), axis=alt.Axis(labelAngle=0)),
                xOffset=alt.XOffset("popularidade_classe:N", sort=["Popular", "Não popular"]),
                y=alt.Y("media:Q", title="Média (0 a 1)", scale=alt.Scale(domain=[0, 1])),
                color=alt.Color("popularidade_classe:N", title="Classe", scale=CORES_CLASSE,
                                legend=alt.Legend(orient="top")),
                tooltip=[
                    alt.Tooltip("caracteristica:N", title="Característica"),
                    alt.Tooltip("popularidade_classe:N", title="Classe"),
                    alt.Tooltip("media:Q", title="Média", format=".2f"),
                ],
            )
            .properties(height=300)
        )
        st.altair_chart(
            barras_perfil,
            width="stretch",
            alt="Média das características sonoras (0 a 1) para hits e não hits no recorte",
        )
