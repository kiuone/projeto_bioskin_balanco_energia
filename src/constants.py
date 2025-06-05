# ============================================================================
# constants.py
# ============================================================================

"""
Constantes e dados fixos para o balanço de energia - Produção de Soforolipídeos
Todos os valores baseados no balanço de massa e rota de produção validados
"""

# Flags de configuração
USE_BOILER = False      # True = caldeira, False = aquecimento elétrico
INCLUDE_HHV = False     # True = inclui energia química, False = só utilidades

# ============================================================================
# MASSAS DO PROCESSO (kg por lote) - DO BALANÇO DE MASSA
# ============================================================================

# Matérias-primas
m_sacarose = 178.74
m_oleo_vegetal = 160.0
m_ureia = 25.38
m_sais_minerais = 1.88
m_agua_total = 508.0  # CORRIGIDO
m_hcl = 37.76
m_etanol = 75.42

# Produtos finais
m_soforolipideos_bruto = 95.59
m_soforolipideos_final = 80.8
m_biomassa_final = 25.52
m_oleo_residual = 105.23
m_fase_aquosa = 376.47
m_co2_produzido = 105.8
m_agua_produzida = 48.71

# Massas por etapa
m_meio_fermentador = 907.62  # massa total do meio no fermentador principal
m_fase_solida_decantador = 121.12  # biomassa + soforolipídeos
m_cristais_pos_precipitacao = 90.6
m_cristais_pos_lavagem = 84.2
m_cristais_pos_centrifugacao = 81.8

# Águas específicas
agua_evaporada_secagem = 55.0  # CORRIGIDO - água evaporada na secagem

# ============================================================================
# VOLUMES E DENSIDADES
# ============================================================================

# Volumes por etapa (L)
V_frasco = 5
V_seed = 100
V_fermentador = 1000
V_meio_fermentador = 739

# Densidades (kg/m³)
rho_meio_aquoso = 1080
rho_meio_bifasico = 1228
rho_oleo = 920
rho_agua = 1000
rho_soforolipideos = 1050

# ============================================================================
# CONDIÇÕES DE PROCESSO
# ============================================================================

# Temperaturas (°C)
T_ambiente = 25
T_esterilizacao_meio = 121
T_esterilizacao_oleo = 109
T_fermentacao = 28
T_cristalizacao = 4
T_secagem = 45

# Tempos de processo (h)
t_fermentacao = 168
t_esterilizacao = 1.0
t_cristalizacao = 12
t_secagem = 10

# Condições operacionais
pH_fermentacao = 4.5
pH_cristalizacao = 2.0
aeracao_vvm = 0.75
pressao_fermentacao = 1.0  # bar

# ============================================================================
# EQUIPAMENTOS OTIMIZADOS
# ============================================================================

# Estrutura: {codigo: {nome, P_nom_kW, P_avg_kW, h, kWh}}
equipamentos_base = {
    'SFR-101': {'nome': 'Shake-flask agitador', 'P_nom': 0.15, 'P_avg': 0.15, 'h': 24, 'kWh': 3.6},
    'SFR-102': {'nome': 'Seed-fermentor agitador', 'P_nom': 1.0, 'P_avg': 0.75, 'h': 48, 'kWh': 36.0},
    'V-104': {'nome': 'Tanque óleo agitador', 'P_nom': 0.5, 'P_avg': 0.5, 'h': 8, 'kWh': 4.0},
    'DE-101': {'nome': 'Bomba cartucho', 'P_nom': 0.4, 'P_avg': 0.4, 'h': 2, 'kWh': 0.8},
    'FR-101': {'nome': 'Agitador 1 m³', 'P_nom': 3.0, 'P_avg': 3.0, 'h': 168, 'kWh': 504.0},
    'BLW-101': {'nome': 'Soprador baixa pressão', 'P_nom': 1.0, 'P_avg': 1.0, 'h': 168, 'kWh': 168.0},
    'FT-101': {'nome': 'Chiller (COP=3)', 'P_nom': 5.0, 'P_avg': 2.0, 'h': 168, 'kWh': 336.0},  # SERÁ RECALCULADO
    'HX-101': {'nome': 'Bombas CW', 'P_nom': 2.0, 'P_avg': 2.0, 'h': 4, 'kWh': 8.0},
    'V-109': {'nome': 'Decanter', 'P_nom': 3.0, 'P_avg': 3.0, 'h': 3, 'kWh': 9.0},
    'SC-101': {'nome': 'Rosca transportadora', 'P_nom': 1.5, 'P_avg': 1.5, 'h': 1, 'kWh': 1.5},
    'V-102': {'nome': 'Precipitação/mistura', 'P_nom': 2.0, 'P_avg': 2.0, 'h': 12, 'kWh': 24.0},
    'BCFBD-101': {'nome': 'Centrífuga cesto', 'P_nom': 6.0, 'P_avg': 6.0, 'h': 4, 'kWh': 24.0},
    'DS-101': {'nome': 'Centrífuga disco', 'P_nom': 4.0, 'P_avg': 4.0, 'h': 4, 'kWh': 16.0},
    'TDR-101': {'nome': 'Secador elétrico', 'P_nom': 6.0, 'P_avg': 6.0, 'h': 12, 'kWh': 72.0},
    'PUMPS': {'nome': 'Bombas transferência', 'P_nom': 5.0, 'P_avg': 5.0, 'h': 2, 'kWh': 10.0}
}

# Utilidades fixas
E_utilidades_fixas = 3460  # kWh por batelada

# ============================================================================
# PROPRIEDADES TERMODINÂMICAS
# ============================================================================

# Calores específicos (kJ/kg·K)
Cp_agua = 4.18
Cp_oleo_soja = 1.94
Cp_meio_aquoso = 4.18  # fração água > 80%
Cp_meio_bifasico = 3.4  # estimativa ponderada
Cp_soforolipideos = 1.5
Cp_biomassa = 3.5
Cp_etanol = 2.46

# Entalpias específicas (kJ/kg)
DH_vap_agua_45C = 2400  # calor latente vaporização água a 45°C
DH_cristalizacao_SL = 85  # calor latente cristalização soforolipídeos
DH_fusao_gelo = 334

# Calor metabólico (kJ/mol O2)
DH_metabolico = 450  # para leveduras oleaginosas

# Poderes caloríficos superiores - HHV (MJ/kg)
HHV_sacarose = 16.7
HHV_oleo_vegetal = 37.0
HHV_soforolipideos = 25.0  # estimado
HHV_biomassa = 20.0  # estimado

# ============================================================================
# EFICIÊNCIAS E FATORES DE CONVERSÃO
# ============================================================================

COP_chiller = 3.0
eficiencia_motor = 0.90
eficiencia_caldeira = 0.85
fator_agitacao_calor = 0.32  # fração do trabalho de agitação que vira calor no caldo
fator_aeracao_calor = 0.20   # fração do trabalho de aeração que vira calor no caldo
fator_bomba_calor = 0.90     # CORRIGIDO - fração do trabalho de bombeamento que vira calor

# Percentuais de perdas térmicas por etapa
perdas_esterilizacao_pct = 0.035  # 3.5%
perdas_fermentacao_pct = 0.015    # 1.5%
perdas_cristalizacao_pct = 0.040  # 4.0%
perdas_secagem_pct = 0.080        # 8.0%

# ============================================================================
# CONSTANTES FÍSICAS E CONVERSÕES
# ============================================================================

R_gas = 8.314  # J/mol·K
peso_molecular_co2 = 44.01  # g/mol
peso_molecular_o2 = 32.0   # g/mol

# Conversões
kJ_para_kWh = 1/3600  # 1 kWh = 3600 kJ
MJ_para_kWh = 1/3.6   # 1 kWh = 3.6 MJ

# Tolerâncias para validação
TOLERANCIA_BALANCO = 0.02      # 2%
TOLERANCIA_CHILLER = 0.15      # 15%
TOLERANCIA_METABOLISMO = 0.10  # 10%