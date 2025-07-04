#Massas (kg)
m_cristais_umidos = 81.8             # cristais após centrifugação
m_cristais_secos = 80.8              # produto final seco
m_sf_cristalizar = 90.6              # soforolipídeos após cristalização
m_sf_inicial = 95.6                  # SF antes cristalização
m_agua_evaporar = 1.0                # água residual a ser evaporada
m_etanol_lavagem = 75.42             # etanol para lavagem
m_etanol_evaporar = 1.0              # etanol a evaporar no secador
m_biomassa_inicial = 25.52           # biomassa do decantador
m_biomassa_residual = 1.0            # biomassa residual após drenagem  
m_HCl_inicial = 37.75                # HCl total adicionado
m_HCl_residual = 2.0                 # HCl residual após drenagem


#Temperaturas (°C)
T_entrada_secador = 4                # cristais saem do chiller a 4°C
T_secagem = 45                       # temperatura de secagem
T_vapor_saida = 45                   # temperatura do vapor de água
T_entrada_chiller = 28                # temperatura do caldo pós-fermentação
T_cristalizacao = 4                   # temperatura de cristalização
T_ambiente = 25                       # temperatura ambiente para perdas

#Tempos de Operação (h)
t_resfriamento_28_4 = 5              # tempo para resfriar de 28°C para 4°C
t_manutencao_cristalizacao = 6       # tempo mantendo a 4°C (cristalização)
t_manutencao_lavagem = 2             # tempo mantendo a 4°C (lavagem etanol)
t_secagem = 12                       # tempo total de secagem

# Calores específicos (kJ/kg·K)
Cp_soforolipideos = 1.6              # calor específico dos soforolipídeos
Cp_agua = 4.18                       # calor específico da água
Cp_biomassa = 3.5                    # biomassa (levedura)
Cp_HCl_solucao = 3.8                 # solução HCl 36%
Cp_etanol_70 = 1.86                   # etanol 70% a 4°C

# Calor latente de cristalização dos soforolipídeos
L_cristalizacao_SL = 28.9            # kJ/kg (positivo - energia liberada)
L_vap_agua_45C = 2400                # kJ/kg
L_etanol_70 = 850                    # kJ/kg (latente evaporação - estimativa)

# Eficiência do chiller
COP_chiller = 3.0                    # coeficiente de performance

# Eficiência do secador
eficiencia_secador = 0.8             # 80% eficiente (20% perdas)

# Fatores de dissipação mecânica (fração que vira calor)
fator_agitacao_calor = 0.35         # agitador FR-101
fator_aeracao_calor = 0.20          # soprador BLW-101  
fator_bomba_calor = 0.20            # bombas PUMPS

# Perdas térmicas para o ambiente (estimadas)
Q_perdas_V102 = 0.5                # tanque cristalização (kW)
Q_perdas_TDR101 = 2.0              # secador de bandeja (kW)

#Potência nominal (kW) e tempo de operação dos equipamentos (h)
# equipamentos_processo = {
#     'SFR-101': {'P_nom': 0.15, 'tempo': 24},    # Shake-flask 
#     'SFR-102': {'P_nom': 1.0,  'tempo': 48},    # Seed fermentor 
#     'V-104':   {'P_nom': 0.5,  'tempo': 8},     # Tanque óleo 
#     'DE-101':  {'P_nom': 0.4,  'tempo': 2},     # Filtro cartucho 
#     'FR-101':  {'P_nom': 3.0,  'tempo': 168},   # Biorreator (otimizado)
#     'BLW-101': {'P_nom': 1.0,  'tempo': 168},   # Soprador integrado 
#     'AF-101':  {'P_nom': 0.35, 'tempo': 168},   # Filtro HEPA  
#     'V-109':   {'P_nom': 3.0,  'tempo': 3},     # Decantador 
#     'SC-101':  {'P_nom': 1.5,  'tempo': 1},     # Rosca 
#     'V-102':   {'P_nom': 2.0,  'tempo': 12},    # Precipitação 
#     'BCFBD-101': {'P_nom': 6.0, 'tempo': 4},    # Centrífuga cesto 
#     'DS-101':  {'P_nom': 4.0,  'tempo': 4},     # Centrífuga disco 
#     'FT-101':  {'P_nom': 'CALCULAR', 'tempo': 13}, # Chiller - calcular
#     'TDR-101': {'P_nom': 'CALCULAR', 'tempo': 12}, # Secador - calcular
#     'PUMPS':   {'P_nom': 5.0,  'tempo': 2}      # Bombas transferência 
# }

equipamentos_processo = {
    'SFR-101':   {'P_nom': 0.15, 'tempo': 24},    # Shake-flask – valor Grok
    'SFR-102':   {'P_nom': 1.00, 'tempo': 48},    # Seed fermentor – valor Grok
    'V-104':     {'P_nom': 0.50, 'tempo': 8},     # Tanque de óleo – valor Grok
    'DE-101':    {'P_nom': 0.40, 'tempo': 2},     # Filtro cartucho – valor Grok
    'FR-101':    {'P_nom': 3.00, 'tempo': 168},   # Biorreator (agitador) – consenso GPT / Gemini
    'BLW-101':   {'P_nom': 1.00, 'tempo': 168},   # Soprador de aeração – consenso unânime
    'AF-101':    {'P_nom': 0.35, 'tempo': 168},   # Filtro HEPA – valor Grok
    'V-109':     {'P_nom': 3.00, 'tempo': 3},     # Decantador – valor Grok mantido
    'SC-101':    {'P_nom': 1.50, 'tempo': 1},     # Rosca – valor Grok
    'V-102':     {'P_nom': 2.00, 'tempo': 12},    # Tanque de precipitação – valor Grok
    'BCFBD-101': {'P_nom': 6.00, 'tempo': 4},     # Centrífuga de cesto – consenso GPT / Gemini / Grok
    'DS-101':    {'P_nom': 4.00, 'tempo': 4},     # Centrífuga de discos – consenso unânime
    'FT-101':    {'P_nom':'CALCULAR', 'tempo': 13},    # Chiller (4 °C), COP ≈ 3 – cálculo a partir da carga confirmada
    'TDR-101':   {'P_nom': 'CALCULAR', 'tempo': 12},    # Secador de bandejas – balanço latent+perdas
    'PUMPS':     {'P_nom': 5.00, 'tempo': 2}      # Bombas de transferência – valor Grok
}

# Consumos independentes do processo
utilidades_fixas = {
    'HVAC': 1596,                    # climatização (9.5 kW × 168h)
    'iluminacao': 840,               # iluminação (5.0 kW × 168h)  
    'bombas_CW': 504,                # bombas água resfriamento (3.0 kW × 168h)
    'caldeira_BOP': 302,             # caldeira standby (1.8 kW × 168h)
    'instrumentacao': 101,           # PLCs e automação (0.6 kW × 168h)
    'laboratorio': 118               # equipamentos lab (0.7 kW × 168h)
}

E_utilidades_fixas_total = 3461     # kWh/lote

# Conversões energéticas
kJ_para_kWh = 1/3600                # 1 kWh = 3600 kJ
kWh_para_kJ = 3600                  # 1 kWh = 3600 kJ

