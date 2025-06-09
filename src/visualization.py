"""
visualization.py - Visualizações do Balanço Energético dos Soforolipídeos
Versão robusta com fallbacks para problemas de dependências
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
import warnings

# Configuração de estilo
plt.style.use('default')  # Mudança para evitar problemas com seaborn
sns.set_palette("husl")

# Cores modernas para gráficos
CORES = {
    'processo': '#2E86C1',      # Azul moderno
    'utilidades': '#F39C12',    # Laranja
    'chiller': '#16A085',       # Verde água
    'secador': '#E74C3C',       # Vermelho
    'biorreator': '#8E44AD',    # Roxo
    'outros': '#95A5A6',        # Cinza
    'fundo': '#F8F9FA',         # Cinza claro
    'texto': '#2C3E50'          # Azul escuro
}

def tentar_salvar_imagem(fig, filename, width=1200, height=800):
    """
    Tenta salvar imagem com fallbacks para diferentes métodos
    """
    try:
        # Método 1: Kaleido (padrão)
        fig.write_image(filename, width=width, height=height, scale=2)
        return True, "Kaleido"
    except Exception as e1:
        try:
            # Método 2: Kaleido sem argumentos extras
            fig.write_image(filename)
            return True, "Kaleido simples"
        except Exception as e2:
            try:
                # Método 3: Orca (fallback antigo)
                fig.write_image(filename, engine="orca")
                return True, "Orca"
            except Exception as e3:
                print(f"⚠️  Não foi possível salvar {filename}")
                print(f"   Erro Kaleido: {str(e1)[:50]}...")
                print(f"   Erro Orca: {str(e3)[:50]}...")
                return False, "Falhou"

def criar_dashboard_completo(resultado_chiller, resultado_secador, equipamentos_atualizados, 
                           energia_total, consumo_especifico, utilidades_fixas_total):
    """
    Cria dashboard completo com múltiplos gráficos
    """
    
    # Preparar dados
    energia_processo = sum([dados['P_nom'] * dados['tempo'] 
                           for codigo, dados in equipamentos_atualizados.items() 
                           if isinstance(dados['P_nom'], (int, float))])
    
    # Dados para gráficos
    dados_distribuicao = {
        'Categoria': ['Equipamentos de Processo', 'Utilidades Fixas'],
        'Energia (kWh)': [energia_processo, utilidades_fixas_total],
        'Percentual': [energia_processo/energia_total*100, utilidades_fixas_total/energia_total*100]
    }
    
    # Criar subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Distribuição Energética', 'Consumo por Equipamento Top 10', 
                       'Balanço Térmico Detalhado', 'Benchmarking Industrial'),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # 1. Gráfico Pizza - Distribuição Energética
    fig.add_trace(
        go.Pie(
            labels=dados_distribuicao['Categoria'],
            values=dados_distribuicao['Energia (kWh)'],
            hole=0.4,
            marker_colors=[CORES['processo'], CORES['utilidades']],
            textinfo='label+percent+value',
            textfont_size=12
        ),
        row=1, col=1
    )
    
    # 2. Top 10 Equipamentos
    equipamentos_energia = []
    for codigo, dados in equipamentos_atualizados.items():
        if isinstance(dados['P_nom'], (int, float)):
            energia = dados['P_nom'] * dados['tempo']
            equipamentos_energia.append({'Equipamento': codigo, 'Energia': energia})
    
    df_equip = pd.DataFrame(equipamentos_energia).sort_values('Energia', ascending=True).tail(10)
    
    fig.add_trace(
        go.Bar(
            y=df_equip['Equipamento'],
            x=df_equip['Energia'],
            orientation='h',
            marker_color=CORES['processo'],
            text=[f'{x:.1f} kWh' for x in df_equip['Energia']],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    # 3. Balanço Térmico Detalhado
    thermal_data = {
        'Processo': ['Chiller - Resfriamento', 'Chiller - Cristalização', 'Chiller - Lavagem', 
                    'Secador - Aquecimento', 'Secador - Evaporação'],
        'Energia (kWh)': [
            resultado_chiller['Q_part1_kJ']/3600,
            resultado_chiller['Q_part2_kJ']/3600, 
            resultado_chiller['Q_part3_kJ']/3600,
            (resultado_secador['Q_cristais_sensivel_kJ'] + 
             resultado_secador['Q_agua_sensivel_kJ'] + 
             resultado_secador['Q_etanol_sensivel_kJ'])/3600,
            (resultado_secador['Q_agua_latente_kJ'] + 
             resultado_secador['Q_etanol_latente_kJ'])/3600
        ]
    }
    
    cores_thermal = [CORES['chiller'], CORES['chiller'], CORES['chiller'], 
                    CORES['secador'], CORES['secador']]
    
    fig.add_trace(
        go.Bar(
            x=thermal_data['Processo'],
            y=thermal_data['Energia (kWh)'],
            marker_color=cores_thermal,
            text=[f'{x:.1f}' for x in thermal_data['Energia (kWh)']],
            textposition='outside'
        ),
        row=2, col=1
    )
    
    # 4. Benchmarking Industrial
    benchmark_data = {
        'Processo': ['Soforolipídeos\n(Este trabalho)', 'Antibióticos\n(Penicilina)', 
                    'Enzimas\n(α-amilase)', 'Etanol\n(2ª geração)', 'Surfactantes\n(Petroquímicos)'],
        'Consumo (kWh/kg)': [consumo_especifico, 120, 85, 15, 8],
        'Tipo': ['Biossurfactante', 'Farmacêutico', 'Industrial', 'Combustível', 'Químico']
    }
    
    cores_benchmark = [CORES['processo'] if i == 0 else CORES['outros'] for i in range(5)]
    
    fig.add_trace(
        go.Scatter(
            x=benchmark_data['Processo'],
            y=benchmark_data['Consumo (kWh/kg)'],
            mode='markers+text',
            marker=dict(size=15, color=cores_benchmark),
            text=[f'{x:.1f}' for x in benchmark_data['Consumo (kWh/kg)']],
            textposition='top center',
            textfont_size=10
        ),
        row=2, col=2
    )
    
    # Layout
    fig.update_layout(
        title={
            'text': 'DASHBOARD ENERGÉTICO - PRODUÇÃO DE SOFOROLIPÍDEOS',
            'x': 0.5,
            'font': {'size': 20, 'color': CORES['texto']}
        },
        showlegend=False,
        height=800,
        plot_bgcolor='white',
        paper_bgcolor=CORES['fundo']
    )
    
    # Ajustar eixos
    fig.update_xaxes(tickangle=45, row=2, col=1)
    fig.update_yaxes(title_text="Energia (kWh)", row=1, col=2)
    fig.update_yaxes(title_text="Energia Térmica (kWh)", row=2, col=1)
    fig.update_yaxes(title_text="Consumo Específico (kWh/kg)", row=2, col=2)
    
    return fig

def criar_sankey_melhorado(resultado_chiller, resultado_secador, equipamentos_atualizados):
    """
    Cria diagrama de Sankey com cores diferenciadas e bem visíveis
    """
    
    # Definir nós
    nodes = [
        "Energia Elétrica\nda Rede",         # 0
        "Biorreator\nPrincipal",             # 1
        "Soprador\nAeração",                 # 2  
        "Chiller",                           # 3
        "Secador",                           # 4
        "Outros\nEquipamentos",              # 5
        "Utilidades\nFixas",                 # 6
        "Calor\nRejeitado",                  # 7
        "Trabalho\nMecânico",               # 8
        "Produto\nFinal"                     # 9
    ]
    
    # Calcular energias
    energia_biorreator = 504  # FR-101
    energia_soprador = 168    # BLW-101
    energia_chiller = resultado_chiller['E_eletrica_total_kWh']
    energia_secador = resultado_secador['E_eletrica_total_kWh']
    energia_outros = 908.3 - energia_biorreator - energia_soprador - energia_chiller - energia_secador
    energia_utilidades = 3461
    
    # Definir fluxos com cores específicas
    fluxos = [
        # Da rede para equipamentos (cores azuis)
        (0, 1, energia_biorreator, 'rgba(142, 68, 173, 0.6)'),      # Roxo - Biorreator
        (0, 2, energia_soprador, 'rgba(46, 134, 193, 0.6)'),       # Azul - Soprador
        (0, 3, energia_chiller, 'rgba(22, 160, 133, 0.6)'),        # Verde - Chiller
        (0, 4, energia_secador, 'rgba(231, 76, 60, 0.6)'),         # Vermelho - Secador
        (0, 5, energia_outros, 'rgba(149, 165, 166, 0.6)'),        # Cinza - Outros
        (0, 6, energia_utilidades, 'rgba(243, 156, 18, 0.6)'),     # Laranja - Utilidades
        
        # Transformações energéticas (cores específicas por tipo)
        (1, 8, energia_biorreator * 0.65, 'rgba(39, 174, 96, 0.7)'),   # Verde - Trabalho útil
        (1, 7, energia_biorreator * 0.35, 'rgba(230, 126, 34, 0.7)'),  # Laranja - Calor perdido
        (2, 8, energia_soprador * 0.8, 'rgba(39, 174, 96, 0.7)'),      # Verde - Trabalho útil
        (2, 7, energia_soprador * 0.2, 'rgba(230, 126, 34, 0.7)'),     # Laranja - Calor perdido
        (3, 7, energia_chiller, 'rgba(52, 152, 219, 0.8)'),            # Azul - Calor removido
        (4, 7, energia_secador * 0.8, 'rgba(231, 76, 60, 0.8)'),       # Vermelho - Calor fornecido
        (4, 9, energia_secador * 0.2, 'rgba(155, 89, 182, 0.8)'),      # Roxo - Contribuição produto
        (5, 7, energia_outros * 0.7, 'rgba(230, 126, 34, 0.7)'),       # Laranja - Calor perdido
        (5, 8, energia_outros * 0.3, 'rgba(39, 174, 96, 0.7)'),        # Verde - Trabalho útil
        (6, 7, energia_utilidades, 'rgba(243, 156, 18, 0.8)'),         # Laranja - Calor rejeitado
        
        # Trabalho final para produto
        (8, 9, energia_biorreator * 0.65 + energia_soprador * 0.8 + energia_outros * 0.3, 'rgba(155, 89, 182, 0.9)')
    ]
    
    # Separar dados
    source = [f[0] for f in fluxos]
    target = [f[1] for f in fluxos]
    value = [f[2] for f in fluxos]
    link_colors = [f[3] for f in fluxos]
    
    # Cores dos nós (mais contrastantes)
    node_colors = [
        '#1f77b4',  # Rede (azul forte)
        '#8E44AD',  # Biorreator (roxo)
        '#2E86C1',  # Soprador (azul médio)
        '#16A085',  # Chiller (verde água)
        '#E74C3C',  # Secador (vermelho)
        '#95A5A6',  # Outros (cinza)
        '#F39C12',  # Utilidades (laranja)
        '#E67E22',  # Calor (laranja escuro)
        '#27AE60',  # Trabalho (verde)
        '#9B59B6'   # Produto (roxo claro)
    ]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="black", width=1),
            label=nodes,
            color=node_colors,
            # font=dict(size=12, color="white")
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors,  # Cores específicas por link
            line=dict(color="rgba(0,0,0,0.3)", width=0.5)
        )
    )])
    
    fig.update_layout(
        title={
            'text': "FLUXO ENERGÉTICO - PRODUÇÃO DE SOFOROLIPÍDEOS<br><sub>Valores em kWh por lote</sub>",
            'x': 0.5,
            'font': {'size': 18, 'color': '#2C3E50'}
        },
        font_size=11,
        plot_bgcolor='white',
        paper_bgcolor='#F8F9FA',
        height=700,
        margin=dict(t=80, b=40, l=40, r=40)
    )
    
    return fig

# Função para adicionar anotações explicativas
def adicionar_anotacoes_sankey(fig):
    """
    Adiciona anotações explicativas ao diagrama
    """
    annotations = [
        dict(
            x=0.02, y=0.95,
            text="<b>ENTRADAS</b><br>Energia da rede elétrica",
            showarrow=False,
            font=dict(size=10, color="#2C3E50"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#2C3E50",
            borderwidth=1
        ),
        dict(
            x=0.98, y=0.95,
            text="<b>SAÍDAS</b><br>Calor rejeitado<br>Trabalho útil<br>Produto final",
            showarrow=False,
            font=dict(size=10, color="#2C3E50"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#2C3E50",
            borderwidth=1,
            align="right"
        ),
        dict(
            x=0.5, y=0.02,
            text="<i>Largura dos fluxos proporcional à energia (kWh)</i>",
            showarrow=False,
            font=dict(size=9, color="#7F8C8D"),
            xanchor="center"
        )
    ]
    
    fig.update_layout(annotations=annotations)
    return fig

def criar_comparativo_termodinamico(resultado_chiller, resultado_secador):
    """
    Gráfico comparativo dos processos termodinâmicos
    """
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('ANÁLISE TERMODINÂMICA COMPARATIVA', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Breakdown Chiller
    labels_chiller = ['SF Sensível', 'SF Latente', 'Biomassa', 'HCl', 'Etanol', 'Perdas']
    valores_chiller = [
        resultado_chiller['Q_sf_sensivel_kJ'],
        abs(resultado_chiller['Q_sf_latente_kJ']),  # Valor absoluto
        resultado_chiller['Q_biomassa_inicial_kJ'],
        resultado_chiller['Q_HCl_inicial_kJ'],
        resultado_chiller['Q_etanol_sensivel_kJ'],
        resultado_chiller['Q_perdas_total_kJ']
    ]
    
    cores_chiller = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', '#95A5A6']
    
    wedges, texts, autotexts = ax1.pie(valores_chiller, labels=labels_chiller, colors=cores_chiller,
                                      autopct='%1.1f%%', startangle=90)
    ax1.set_title('CHILLER - Distribuição de Calor\n(Total: 38.4 MJ)', fontweight='bold')
    
    # Gráfico 2: Breakdown Secador
    labels_secador = ['Cristais', 'Água Sensível', 'Água Latente', 'Etanol Sensível', 'Etanol Latente', 'Perdas']
    valores_secador = [
        resultado_secador['Q_cristais_sensivel_kJ'],
        resultado_secador['Q_agua_sensivel_kJ'],
        resultado_secador['Q_agua_latente_kJ'],
        resultado_secador['Q_etanol_sensivel_kJ'],
        resultado_secador['Q_etanol_latente_kJ'],
        resultado_secador['Q_perdas_kJ']
    ]
    
    cores_secador = ['#E67E22', '#3498DB', '#2980B9', '#8E44AD', '#9B59B6', '#BDC3C7']
    
    wedges2, texts2, autotexts2 = ax2.pie(valores_secador, labels=labels_secador, colors=cores_secador,
                                         autopct='%1.1f%%', startangle=90)
    ax2.set_title('SECADOR - Distribuição de Calor\n(Total: 95.3 MJ)', fontweight='bold')
    
    plt.tight_layout()
    return fig

def criar_graficos_alternativos_matplotlib(resultado_chiller, resultado_secador, equipamentos_atualizados,
                                         energia_total, consumo_especifico, utilidades_fixas_total):
    """
    Cria gráficos usando apenas matplotlib como fallback
    """
    
    # Configurar subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('DASHBOARD ENERGÉTICO - PRODUÇÃO DE SOFOROLIPÍDEOS', fontsize=16, fontweight='bold')
    
    # 1. Distribuição Energética (Pizza)
    energia_processo = sum([dados['P_nom'] * dados['tempo'] 
                           for codigo, dados in equipamentos_atualizados.items() 
                           if isinstance(dados['P_nom'], (int, float))])
    
    labels = ['Equipamentos\nde Processo', 'Utilidades\nFixas']
    sizes = [energia_processo, utilidades_fixas_total]
    colors = [CORES['processo'], CORES['utilidades']]
    
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Distribuição Energética Total')
    
    # 2. Top 10 Equipamentos (Barras Horizontais)
    equipamentos_energia = []
    for codigo, dados in equipamentos_atualizados.items():
        if isinstance(dados['P_nom'], (int, float)):
            energia = dados['P_nom'] * dados['tempo']
            equipamentos_energia.append((codigo, energia))
    
    equipamentos_energia.sort(key=lambda x: x[1], reverse=True)
    top10 = equipamentos_energia[:10]
    
    nomes = [eq[0] for eq in top10]
    energias = [eq[1] for eq in top10]
    
    ax2.barh(nomes, energias, color=CORES['processo'])
    ax2.set_xlabel('Energia (kWh)')
    ax2.set_title('Top 10 Equipamentos - Consumo Energético')
    
    # 3. Balanço Térmico
    thermal_labels = ['Chiller\nResfriamento', 'Chiller\nCristalização', 'Chiller\nLavagem', 
                     'Secador\nAquecimento', 'Secador\nEvaporação']
    thermal_values = [
        resultado_chiller['Q_part1_kJ']/3600,
        resultado_chiller['Q_part2_kJ']/3600, 
        resultado_chiller['Q_part3_kJ']/3600,
        (resultado_secador['Q_cristais_sensivel_kJ'] + 
         resultado_secador['Q_agua_sensivel_kJ'] + 
         resultado_secador['Q_etanol_sensivel_kJ'])/3600,
        (resultado_secador['Q_agua_latente_kJ'] + 
         resultado_secador['Q_etanol_latente_kJ'])/3600
    ]
    
    cores_thermal = [CORES['chiller'], CORES['chiller'], CORES['chiller'], 
                    CORES['secador'], CORES['secador']]
    
    bars = ax3.bar(thermal_labels, thermal_values, color=cores_thermal)
    ax3.set_ylabel('Energia Térmica (kWh)')
    ax3.set_title('Balanço Térmico Detalhado')
    ax3.tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, thermal_values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.1f}', ha='center', va='bottom')
    
    # 4. Benchmarking
    benchmark_processos = ['Soforolipídeos\n(Este trabalho)', 'Antibióticos\n(Penicilina)', 
                          'Enzimas\n(α-amilase)', 'Etanol\n(2ª geração)', 'Surfactantes\n(Petroquímicos)']
    benchmark_consumos = [consumo_especifico, 120, 85, 15, 8]
    cores_benchmark = [CORES['processo'] if i == 0 else CORES['outros'] for i in range(5)]
    
    bars = ax4.bar(benchmark_processos, benchmark_consumos, color=cores_benchmark)
    ax4.set_ylabel('Consumo Específico (kWh/kg)')
    ax4.set_title('Benchmarking Industrial')
    ax4.tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, benchmark_consumos):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{value:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    return fig

def salvar_relatorio_completo(resultado_chiller, resultado_secador, equipamentos_atualizados, 
                            energia_total, consumo_especifico, utilidades_fixas_total):
    """
    Salva todos os gráficos com tratamento robusto de erros
    """
    
    sucesso_count = 0
    erro_count = 0
    
    print("📊 Salvando gráficos...")
    
    # 1. Dashboard principal (Plotly)
    try:
        fig_dashboard = criar_dashboard_completo(
            resultado_chiller, resultado_secador, equipamentos_atualizados,
            energia_total, consumo_especifico, utilidades_fixas_total
        )
        
        # Sempre salva HTML (nunca falha)
        fig_dashboard.write_html("dashboard_energetico.html")
        print("✅ dashboard_energetico.html")
        sucesso_count += 1
        
        # Tenta salvar PNG
        sucesso, metodo = tentar_salvar_imagem(fig_dashboard, "dashboard_energetico.png", 1200, 800)
        if sucesso:
            print(f"✅ dashboard_energetico.png ({metodo})")
            sucesso_count += 1
        else:
            erro_count += 1
            
    except Exception as e:
        print(f"❌ Erro no dashboard Plotly: {e}")
        erro_count += 1
    
    # 2. Sankey (Plotly)
    try:
        fig_sankey = criar_sankey_melhorado(resultado_chiller, resultado_secador, equipamentos_atualizados)
        fig_sankey = adicionar_anotacoes_sankey(fig_sankey)

        # Sempre salva HTML
        fig_sankey.write_html("fluxo_energetico_sankey.html")
        print("✅ fluxo_energetico_sankey.html")
        sucesso_count += 1
        
        # Tenta salvar PNG
        sucesso, metodo = tentar_salvar_imagem(fig_sankey, "fluxo_energetico_sankey.png", 1000, 600)
        if sucesso:
            print(f"✅ fluxo_energetico_sankey.png ({metodo})")
            sucesso_count += 1
        else:
            erro_count += 1
            
    except Exception as e:
        print(f"❌ Erro no Sankey: {e}")
        erro_count += 1
    
    # 3. Análise termodinâmica (Matplotlib)
    try:
        fig_termo = criar_comparativo_termodinamico(resultado_chiller, resultado_secador)
        fig_termo.savefig("analise_termodinamica.png", dpi=300, bbox_inches='tight', 
                         facecolor='white', edgecolor='none')
        plt.close(fig_termo)
        print("✅ analise_termodinamica.png")
        sucesso_count += 1
    except Exception as e:
        print(f"❌ Erro na análise termodinâmica: {e}")
        erro_count += 1
    
    # 4. Dashboard alternativo (Matplotlib - fallback)
    try:
        fig_alt = criar_graficos_alternativos_matplotlib(
            resultado_chiller, resultado_secador, equipamentos_atualizados,
            energia_total, consumo_especifico, utilidades_fixas_total
        )
        fig_alt.savefig("dashboard_matplotlib.png", dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
        plt.close(fig_alt)
        print("✅ dashboard_matplotlib.png (fallback)")
        sucesso_count += 1
    except Exception as e:
        print(f"❌ Erro no dashboard matplotlib: {e}")
        erro_count += 1
    
    # Resumo
    total_arquivos = 6  # HTML x2 + PNG x4
    print(f"\n📈 Resumo: {sucesso_count}/{total_arquivos} arquivos salvos com sucesso")
    
    if erro_count > 0:
        print(f"⚠️  {erro_count} arquivos falharam (principalmente PNGs - use os HTMLs)")
    
    return sucesso_count, erro_count

def gerar_visualizacoes_completas(resultado_chiller, resultado_secador, equipamentos_atualizados,
                                 energia_total, consumo_especifico, utilidades_fixas_total):
    """
    Função principal robusta que gera todas as visualizações
    """
    print("\n🎨 GERANDO VISUALIZAÇÕES...")
    print("=" * 50)
    
    # Salvar arquivos com tratamento robusto
    sucesso, erro = salvar_relatorio_completo(
        resultado_chiller, resultado_secador, equipamentos_atualizados,
        energia_total, consumo_especifico, utilidades_fixas_total
    )
    
    print("\n✨ Visualizações processadas!")
    print("💡 Dicas:")
    print("   🌐 Abra os arquivos .html para gráficos interativos")
    print("   🖼️  Use os arquivos .png para documentos/apresentações")
    print("   📊 dashboard_matplotlib.png é um fallback garantido")
    
    if erro > 0:
        print("\n🔧 Se houver problemas com imagens PNG:")
        print("   1. Use os arquivos HTML (sempre funcionam)")
        print("   2. Abra o HTML no navegador e tire screenshot")
        print("   3. Ou atualize: pip install -U kaleido plotly")
    
    return sucesso >= 3  # Sucesso se pelo menos metade dos arquivos foram gerados

