# Justificativa das métricas — Dashboard 2

**Público-alvo do dashboard:** artista independente que está produzindo e vai lançar a próxima faixa e quer saber o que as músicas que fazem sucesso no gênero dele têm em comum.

**Definição de "hit" usada em todas as métricas:** música no quartil superior de popularidade da base (`track_popularity` ≥ 58, de 0 a 100), a mesma variável `popularidade_classe` criada na EDA ("Popular" x "Não popular").

**Widgets que controlam as métricas:** gêneros (multiselect) e ano de lançamento (slider) na barra lateral, mais o clique numa barra do gráfico "Taxa de hits por gênero", que restringe o recorte a um gênero.

## Métrica 1: Taxa de hits
- **Variável:** `popularidade_classe` (derivada de `track_popularity`)
- **O que mede:** a proporção de músicas do recorte que são hits, comparada (delta, em pontos percentuais) com a taxa da base inteira (25,6%).
- **Por que foi escolhida:** é a forma mais direta de mostrar o quanto é "difícil" emplacar uma música em cada gênero e época. A EDA mostrou que essa taxa varia muito por gênero (~38% no pop contra ~9% no edm).
- **Público-alvo:** artista independente.
- **Qual decisão pode ser apoiada por essa métrica?** Em qual gênero/subnicho posicionar o lançamento e quão realista é a expectativa de alcance. Num gênero com taxa baixa, a música compete com muitas outras que não chegam ao topo.
- **O que comunica ao público-alvo:** "de cada 100 músicas deste gênero, X estão entre as mais ouvidas", sem precisar entender a escala de popularidade do Spotify.

## Métrica 2: Duração típica de um hit
- **Variável:** `duration_ms` (exibida em minutos:segundos)
- **O que mede:** a mediana da duração dos hits do recorte, com o delta (em segundos) em relação à mediana das músicas que não são hits.
- **Por que foi escolhida:** a duração é uma decisão que o artista controla na produção e na edição da faixa. A EDA mostrou que as populares tendem a ser um pouco mais curtas. Usamos a mediana porque a duração é assimétrica (cauda de músicas longas), como visto no Shapiro-Wilk e no histograma.
- **Público-alvo:** artista independente.
- **Qual decisão pode ser apoiada por essa métrica?** Qual duração mirar na versão de lançamento (por exemplo, uma "radio edit" mais curta).
- **O que comunica ao público-alvo:** "um hit típico deste gênero dura cerca de 3:30", um alvo concreto para a produção.

## Métrica 3: Dançabilidade de um hit
- **Variável:** `danceability` (0 a 1)
- **O que mede:** a mediana da dançabilidade dos hits do recorte, com o delta em relação às músicas que não são hits.
- **Por que foi escolhida:** na EDA, a dançabilidade variou muito entre os gêneros (Kruskal-Wallis, com o rock bem abaixo do rap e do latin), e o artista consegue influenciá-la pelo ritmo e pela batida. Com o clique no gênero, mostra o patamar esperado dentro do gênero do artista.
- **Público-alvo:** artista independente.
- **Qual decisão pode ser apoiada por essa métrica?** Se o arranjo deve priorizar uma batida mais regular e "dançante", ou se o gênero dá espaço para faixas menos dançantes.
- **O que comunica ao público-alvo:** "os hits deste gênero têm dançabilidade em torno de 0,7 numa escala de 0 a 1", e se ela é maior ou menor do que a das demais músicas.

## Métrica 4: Energia de um hit
- **Variável:** `energy` (0 a 1)
- **O que mede:** a mediana da energia dos hits do recorte, com o delta em relação às músicas que não são hits.
- **Por que foi escolhida:** na EDA, `energy` foi uma das variáveis com diferença significativa entre populares e não populares (Mann-Whitney). As populares têm energia um pouco menor, um resultado contraintuitivo e útil para quem acha que "mais intenso" sempre vende mais.
- **Público-alvo:** artista independente.
- **Qual decisão pode ser apoiada por essa métrica?** O nível de intensidade da mixagem e do arranjo (camadas, volume, distorção) para o gênero escolhido.
- **O que comunica ao público-alvo:** "os hits deste gênero não são, em geral, mais enérgicos do que as outras músicas", ou seja, mais intensidade não garante sucesso.

## Visuais do Dashboard 2 (além das métricas)

1. **Taxa de hits por gênero** (barras, clicável): compara os gêneros e funciona como filtro para as métricas e os outros gráficos.
2. **Taxa de hits por duração** (barras por faixa de minutos, com a taxa média tracejada): mostra em qual faixa de duração a chance de ser hit é maior no recorte.
3. **Perfil sonoro: hits x não hits** (barras agrupadas): compara a média de dançabilidade, energia, valência, acústica, fala e "ao vivo" entre hits e não hits.
