# ============================================================================
# visualization.py
# ============================================================================

"""
Visualizações e gráficos para o balanço de energia
Inclui diagrama de Sankey e gráficos de distribuição
"""

import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List
from pathlib import Path

def create_sankey_diagram(balance_results: Dict[str, float], 
                         save_path: str = "results/figures/diagrama_sankey.html") -> go.Figure:
    """
    Cria diagrama de Sankey dos fluxos energéticos usando Plotly
    """
    # Definir nós (nodes)
    node_labels = [
        "Energia Elétrica",           # 0
        "Energia Vapor",              # 1  
        "Energia Química (MP)",       # 2
        "Sistema de Produção",        # 3 - nó central
        "Calor Rejeitado",           # 4
        "Perdas Térmicas",           # 5
        "Energia Produtos",          # 6
        "Trabalho Útil"              # 7
    ]
    
    # Extrair valores dos resultados
    E_eletrica = balance_results['E_entrada_eletrica']
    E_vapor = balance_results['E_entrada_vapor'] 
    E_quimica_in = balance_results['E_entrada_quimica']
    Q_rejeitado = balance_results['E_saida_calor']
    Q_perdas = balance_results['E_saida_perdas']
    E_produtos = balance_results['E_saida_produtos']
    W_util = balance_results['E_saida_trabalho']
    
    # Definir links (fluxos)
    source = []  # índices dos nós de origem
    target = []  # índices dos nós de destino  
    value = []   # valores dos fluxos
    
    # Entradas -> Sistema
    if E_eletrica > 0:
        source.append(0); target.append(3); value.append(E_eletrica)
    if E_vapor > 0:
        source.append(1); target.append(3); value.append(E_vapor)
    if E_quimica_in > 0:
        source.append(2); target.append(3); value.append(E_quimica_in)
    
    # Sistema -> Saídas
    if Q_rejeitado > 0:
        source.append(3); target.append(4); value.append(Q_rejeitado)
    if Q_perdas > 0:
        source.append(3); target.append(5); value.append(Q_perdas)
    if E_produtos > 0:
        source.append(3); target.append(6); value.append(E_produtos)
    if W_util > 0:
        source.append(3); target.append(7); value.append(W_util)
    
    # Criar o diagrama
    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = node_labels,
            color = ["lightblue", "orange", "lightgreen", "red", 
                    "pink", "gray", "yellow", "purple"]
        ),
        link = dict(
            source = source,
            target = target,
            value = value,
            color = "rgba(0,0,255,0.3)"
        )
    )])
    
    fig.update_layout(
        title_text="Diagrama de Sankey - Fluxos Energéticos (kWh/lote)",
        font_size=12,
        width=1200,
        height=600
    )
    
    # Salvar
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(save_path)
    
    return fig

def create_energy_breakdown_chart(electrical_results: Dict[str, float],
                                 thermal_results: Dict[str, float],
                                 save_path: str = "results/figures/distribuicao_energia.png") -> plt.Figure:
    """
    Cria gráfico de distribuição energética por categoria
    """
    # Preparar dados para o gráfico
    categorias = []
    valores = []
    
    # Energia elétrica por categoria (principais equipamentos)
    equipamentos = electrical_results['equipamentos']
    
    # Agrupar equipamentos por tipo
    fermentacao = equipamentos['FR-101']['kWh'] + equipamentos['BLW-101']['kWh']
    separacao = (equipamentos['BCFBD-101']['kWh'] + equipamentos['DS-101']['kWh'] + 
                equipamentos['V-109']['kWh'])
    secagem = equipamentos['TDR-101']['kWh']
    chiller = equipamentos['FT-101']['kWh']
    outros_equipamentos = (electrical_results['E_processo_total'] - 
                          fermentacao - separacao - secagem - chiller)
    utilidades = electrical_results['E_eletrica_total'] - electrical_results['E_processo_total']
    
    # Cargas térmicas por etapa
    esterilizacao = thermal_results['Q_esterilizacao_total']
    fermentacao_termica = thermal_results['Q_fermentacao_total']
    cristalizacao = thermal_results['Q_cristalizacao_total']
    secagem_termica = thermal_results['Q_secagem_total']
    
    # Dados para gráfico de barras
    categorias_elet = ['Fermentação', 'Separação', 'Secagem', 'Chiller', 'Outros Equip.', 'Utilidades']
    valores_elet = [fermentacao, separacao, secagem, chiller, outros_equipamentos, utilidades]
    
    categorias_term = ['Esterilização', 'Fermentação', 'Cristalização', 'Secagem']
    valores_term = [esterilizacao, fermentacao_termica, cristalizacao, secagem_termica]
    
    # Criar subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfico 1: Energia Elétrica
    bars1 = ax1.bar(categorias_elet, valores_elet, color='lightblue', edgecolor='navy')
    ax1.set_title('Distribuição da Energia Elétrica (kWh/lote)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Energia (kWh)', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars1, valores_elet):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, 
                f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 2: Cargas Térmicas
    bars2 = ax2.bar(categorias_term, valores_term, color='orange', edgecolor='red')
    ax2.set_title('Distribuição das Cargas Térmicas (kWh/lote)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Energia Térmica (kWh)', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars2, valores_term):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
                f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Salvar
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

def create_chiller_validation_chart(chiller_results: Dict[str, float],
                                   save_path: str = "results/figures/validacao_chiller.png") -> plt.Figure:
    """
    Cria gráfico comparando chiller original vs recalculado
    """
    original = chiller_results['Q_chiller_original']
    recalculado = chiller_results['Q_chiller_recalculado']
    desvio = chiller_results['desvio_chiller'] * 100  # em %
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categorias = ['Original\n(Tabela)', 'Recalculado\n(Q_total/COP)']
    valores = [original, recalculado]
    cores = ['lightblue', 'orange']
    
    bars = ax.bar(categorias, valores, color=cores, edgecolor='black', linewidth=2)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                f'{value:.1f} kWh', ha='center', va='bottom', fontweight='bold')
    
    # Adicionar linha de desvio
    ax.axhline(y=original, color='red', linestyle='--', alpha=0.7, label=f'Desvio: {desvio:.1f}%')
    
    ax.set_title('Validação do Consumo do Chiller', fontsize=16, fontweight='bold')
    ax.set_ylabel('Consumo Elétrico (kWh/lote)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Adicionar texto de status
    status = "✓ APROVADO" if desvio < 15 else "✗ REVISAR"
    color = "green" if desvio < 15 else "red"
    ax.text(0.5, max(valores) * 0.8, f'Status: {status}', 
            transform=ax.transData, ha='center', fontsize=14, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.3))
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

def export_results_to_excel(all_results: Dict[str, float], 
                           save_path: str = "results/tables/resultados_balanco_energia.xlsx") -> None:
    """
    Exporta todos os resultados para planilha Excel organizada
    """
    # Criar DataFrames organizados por categoria
    
    # 1. Energia Elétrica
    df_eletrica = pd.DataFrame({
        'Parâmetro': ['Consumo dos Equipamentos', 'Utilidades Fixas', 'Total Elétrico', 'Consumo Específico'],
        'Valor': [all_results['E_processo_total'], 3460, all_results['E_eletrica_total'], 
                 all_results['consumo_especifico']],
        'Unidade': ['kWh/lote', 'kWh/lote', 'kWh/lote', 'kWh/kg produto']
    })
    
    # 2. Cargas Térmicas
    thermal_keys = [k for k in all_results.keys() if k.startswith('Q_')]
    df_termica = pd.DataFrame({
        'Etapa/Parâmetro': [k.replace('Q_', '').replace('_', ' ').title() for k in thermal_keys],
        'Valor (kWh)': [all_results[k] for k in thermal_keys]
    })
    
    # 3. Balanço Energético
    df_balanco = pd.DataFrame({
        'Tipo': ['ENTRADAS', '', '', '', 'SAÍDAS', '', '', '', 'FECHAMENTO', ''],
        'Parâmetro': ['Energia Elétrica', 'Energia Vapor', 'Energia Química', 'TOTAL ENTRADA',
                     'Calor Rejeitado', 'Perdas Térmicas', 'Energia Produtos', 'TOTAL SAÍDA',
                     'Erro do Balanço (%)', 'Status'],
        'Valor': [all_results['E_entrada_eletrica'], all_results['E_entrada_vapor'], 
                 all_results['E_entrada_quimica'], all_results['E_entrada_total'],
                 all_results['E_saida_calor'], all_results['E_saida_perdas'],
                 all_results['E_saida_produtos'], all_results['E_saida_total'],
                 all_results['erro_balanco']*100, 'FECHADO' if all_results['balanco_fechado'] else 'ERRO'],
        'Unidade': ['kWh', 'kWh', 'kWh', 'kWh', 'kWh', 'kWh', 'kWh', 'kWh', '%', '-']
    })
    
    # 4. Equipamentos detalhados
    equipamentos = all_results['equipamentos']
    df_equipamentos = pd.DataFrame([
        {
            'Código': codigo,
            'Nome': dados['nome'],
            'Potência (kW)': dados['P_avg'],
            'Tempo (h)': dados['h'],
            'Consumo (kWh)': dados['kWh']
        }
        for codigo, dados in equipamentos.items()
    ])
    
    # Salvar no Excel
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
        df_eletrica.to_excel(writer, sheet_name='Energia Elétrica', index=False)
        df_termica.to_excel(writer, sheet_name='Cargas Térmicas', index=False)  
        df_balanco.to_excel(writer, sheet_name='Balanço Energético', index=False)
        df_equipamentos.to_excel(writer, sheet_name='Equipamentos', index=False)
