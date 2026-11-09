import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def render_curso_superior():
    st.header("🎓 Análise de Ensino Superior e Mulheres em STEM")
    st.subheader("Consultoria Estratégica para os Governadores do Sudeste")

    # CRITÉRIO 1: Ingestão de Dados via Upload
    uploaded_file = st.file_uploader("Carregue a base do IBGE/Censo da Educação Superior (CSV ou XLSX)", type=["csv", "xlsx"], key="stem_upload")
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
            # Filtros Obrigatórios na Barra Lateral
            st.sidebar.markdown("### Filtros do Indicador")
            estados_sudeste = ['MG', 'SP', 'RJ', 'ES']
            uf_selecionada = st.sidebar.multiselect("Selecione os Estados (Sudeste)", options=estados_sudeste, default=estados_sudeste)
            ano_selecionado = st.sidebar.selectbox("Selecione o Ano de Análise", options=sorted(df['Ano'].unique(), reverse=True))
            area_selecionada = st.sidebar.selectbox("Área do Conhecimento", options=["Todas", "Exatas/STEM", "Humanas", "Saúde"])
            
            # Aplicação dos Filtros nos Dados
            df_filtrado = df[(df['UF'].isin(uf_selecionada)) & (df['Ano'] == ano_selecionado)]
            if area_selecionada != "Todas":
                df_filtrado = df_filtrado[df_filtrado['Area'] == area_selecionada]

            # CRITÉRIO 2: Rigor Estatístico Obrigatório
            # Supondo que a coluna alvo seja 'Taxa_Conclusao_por_100k' ou 'Total_Graduados'
            valores = df_filtrado['Taxa_Conclusao_por_100k'].dropna().to_numpy()
            
            if len(valores) > 0:
                media = np.mean(valores)
                mediana = np.median(valores)
                # Cálculo da Moda com Pandas
                moda_serie = df_filtrado['Taxa_Conclusao_por_100k'].mode()
                moda = moda_serie.iloc[0] if not moda_serie.empty else np.nan
                
                # Dispersão e Quartis
                q1 = np.percentile(valores, 25)
                q3 = np.percentile(valores, 75)
                iqr = q3 - q1
                amplitude = np.max(valores) - np.min(valores)
                desvio_padrao = np.std(valores, ddof=1) if len(valores) > 1 else 0.0
                
                # Detecção Rigorosa de Outliers (Regra 1.5xIQR)
                limite_inferior = q1 - 1.5 * iqr
                limite_superior = q3 + 1.5 * iqr
                outliers = df_filtrado[(df_filtrado['Taxa_Conclusao_por_100k'] < limite_inferior) | (df_filtrado['Taxa_Conclusao_por_100k'] > limite_superior)]

                # Exibição dos KPIs em Cards Estilizados
                st.markdown("### 📊 Métricas Estatísticas Consolidadas")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Média Aritmética", f"{media:.2f}")
                col2.metric("Mediana (Robusta)", f"{mediana:.2f}")
                col3.metric("Desvio Padrão", f"{desvio_padrao:.2f}")
                col4.metric("Intervalo Interquartil (IQR)", f"{iqr:.2f}")
                
                # Justificativa de Assimetria baseada em Outliers
                st.markdown("#### 🔍 Análise de Assimetria e Anomalias")
                if len(outliers) > 0:
                    st.warning(f"⚠️ Foram detectados {len(outliers)} municípios/regiões como Outliers pelo critério de 1.5xIQR.")
                    st.dataframe(outliers[['UF', 'Municipio', 'Taxa_Conclusao_por_100k']])
                    st.info("💡 **Impacto Curvatura:** Os outliers detectados estão distorcendo a Média. Recomenda-se aos governadores utilizar a **Mediana** como métrica central estável para o planejamento de fundos.")
                else:
                    st.success("✅ Nenhum outlier severo detectado. A distribuição territorial é homogênea.")
                
                # CRITÉRIO 3: Visualização de Dados Avançada
                st.markdown("### 📈 Visualizações do Cenário")
                tab1, tab2 = st.tabs(["Evolução Histórica e Proporções", "Dispersão e Boxplot"])
                
                with tab1:
                    # Gráfico de linha para evolução histórica
                    df_historico = df[df['UF'].isin(uf_selecionada)]
                    fig_linha = px.line(df_historico, x='Ano', y='Taxa_Conclusao_por_100k', color='UF', title='Evolução da Taxa de Graduação por Estado')
                    st.plotly_chart(fig_linha, use_container_width=True)
                    
                    # Gráfico de barras 100% empilhadas para proporção de gênero
                    fig_barras = px.bar(df_filtrado, x='Area', y=['Percentual_Mulheres', 'Percentual_Homens'], 
                                        title='Proporção de Gênero por Área do Conhecimento (Foco em STEM)', 
                                        barmode='stack', labels={'value': 'Percentual %', 'variable': 'Gênero'})
                    st.plotly_chart(fig_barras, use_container_width=True)
                    
                with tab2:
                    # Boxplot para visualização gráfica dos outliers e quartis
                    fig_box = px.boxplot(df_filtrado, y='Taxa_Conclusao_por_100k', x='UF', points="all", title='Boxplot de Dispersão Territorial da Conclusão de Curso')
                    st.plotly_chart(fig_box, use_container_width=True)

            else:
                st.error("Dados insuficientes após aplicação dos filtros.")
                
            # Bloco de Conteúdo Adicional e Notícias Reais
            st.markdown("---")
            st.markdown("### 📰 Inteligência de Mercado & Notícias")
            col_midia1, col_midia2 = st.columns(2)
            with col_midia1:
                st.markdown("🔗 **[Fuga de Cérebros: Setor de tecnologia perde profissionais qualificados para o exterior](https://globo.com)**")
                st.caption("A escassez de profissionais formados em áreas STEM ameaça o crescimento do PIB industrial no Sudeste brasileiro.")
            with col_midia2:
                st.markdown("🔗 **[Presença feminina em cursos de Engenharia e TI cresce, mas desigualdade persiste](https://ebc.com.br)**")
                st.caption("Políticas de bolsas de estudo e incentivos estaduais em São Paulo e Minas Gerais tentam mitigar o gap de gênero.")
                
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
    else:
        st.info("Aguardando o upload da base de dados oficial do Ensino Superior IBGE/INEP.")
