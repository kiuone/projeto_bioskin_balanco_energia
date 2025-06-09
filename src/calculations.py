"""
calculations.py - Funções para Balanço Energético dos Soforolipídeos
Todas as fórmulas baseadas em primeiros princípios termodinâmicos
"""

def calcular_calor_sensivel(massa_kg, cp_kJ_kg_K, delta_T_K):
    """
    Calcula calor sensível: Q = m × Cp × ΔT
    
    Args:
        massa_kg: massa da substância (kg)
        cp_kJ_kg_K: calor específico (kJ/kg·K)
        delta_T_K: variação de temperatura (K ou °C)
    
    Returns:
        Calor sensível em kJ
    """
    return massa_kg * cp_kJ_kg_K * delta_T_K


def calcular_calor_latente(massa_kg, L_kJ_kg):
    """
    Calcula calor latente: Q = m × L
    
    Args:
        massa_kg: massa da substância (kg)
        L_kJ_kg: calor latente específico (kJ/kg)
    
    Returns:
        Calor latente em kJ
    """
    return massa_kg * L_kJ_kg


def calcular_energia_eletrica_equipamento(potencia_kW, tempo_h):
    """
    Calcula energia elétrica: E = P × t
    
    Args:
        potencia_kW: potência do equipamento (kW)
        tempo_h: tempo de operação (h)
    
    Returns:
        Energia elétrica em kWh
    """
    return potencia_kW * tempo_h


def calcular_potencia_chiller(calor_removido_kJ, COP, tempo_h):
    """
    Calcula potência elétrica do chiller: P = Q_removido / (COP × tempo)
    
    Args:
        calor_removido_kJ: calor total a ser removido (kJ)
        COP: coeficiente de performance do chiller
        tempo_h: tempo de operação (h)
    
    Returns:
        dict com potência média (kW) e energia total (kWh)
    """
    calor_removido_kWh = calor_removido_kJ / 3600  # conversão kJ → kWh
    energia_eletrica_kWh = calor_removido_kWh / COP
    potencia_media_kW = energia_eletrica_kWh / tempo_h
    
    return {
        'potencia_media_kW': potencia_media_kW,
        'energia_total_kWh': energia_eletrica_kWh,
        'calor_removido_kWh': calor_removido_kWh
    }


def calcular_potencia_secador(calor_fornecido_kJ, eficiencia, tempo_h):
    """
    Calcula potência elétrica do secador: P = Q_fornecido / (eficiência × tempo)
    
    Args:
        calor_fornecido_kJ: calor total a ser fornecido (kJ)
        eficiencia: eficiência do secador (0-1)
        tempo_h: tempo de operação (h)
    
    Returns:
        dict com potência média (kW) e energia total (kWh)
    """
    calor_fornecido_kWh = calor_fornecido_kJ / 3600  # conversão kJ → kWh
    energia_eletrica_kWh = calor_fornecido_kWh / eficiencia
    potencia_media_kW = energia_eletrica_kWh / tempo_h
    
    return {
        'potencia_media_kW': potencia_media_kW,
        'energia_total_kWh': energia_eletrica_kWh,
        'calor_util_kWh': calor_fornecido_kWh
    }


def calcular_dissipacao_mecanica(energia_eletrica_kWh, fator_dissipacao):
    """
    Calcula calor gerado por dissipação mecânica
    
    Args:
        energia_eletrica_kWh: energia elétrica consumida (kWh)
        fator_dissipacao: fração que vira calor (0-1)
    
    Returns:
        Calor dissipado em kJ
    """
    return energia_eletrica_kWh * fator_dissipacao * 3600  # kWh → kJ


def calcular_perdas_termicas(potencia_perdas_kW, tempo_h):
    """
    Calcula perdas térmicas para o ambiente
    
    Args:
        potencia_perdas_kW: potência de perdas (kW)
        tempo_h: tempo de operação (h)
    
    Returns:
        Perdas térmicas em kJ
    """
    return potencia_perdas_kW * tempo_h * 3600  # kW×h → kJ


def calcular_energia_chiller(Q_removido_kJ, COP):
    """
    Calcula energia elétrica do chiller: E = Q_removido / COP
    Conversão automática kJ → kWh
    """
    energia_kWh = Q_removido_kJ / (COP * 3600)
    return energia_kWh


def balanco_chiller_completo(m_sf_inicial, m_biomassa_inicial, m_HCl_inicial,
                            m_biomassa_residual, m_HCl_residual, m_sf_cristalizar, m_etanol_lavagem,
                            Cp_soforolipideos, Cp_biomassa, Cp_HCl_solucao, Cp_etanol_70,
                            T_inicial, T_final, T_ambiente, L_cristalizacao_SL,
                            perdas_ambiente_kW, t_resfriamento_28_4, t_manutencao_cristalizacao, 
                            t_manutencao_lavagem, COP):
    """
    Balanço térmico CORRETO do chiller - cada componente separado conforme fluxo real
    
    PARTE 1 (5h): Resfriamento 28°C → 4°C + cristalização SF
    PARTE 2 (6h): Manutenção componentes residuais a 4°C  
    PARTE 3 (2h): Resfriamento etanol + manutenção total a 4°C
    """
    
    # PARTE 1: Resfriamento inicial + cristalização (5h)
    Q_sf_sensivel = m_sf_inicial * Cp_soforolipideos * (T_inicial - T_final)
    Q_sf_latente = m_sf_inicial * (-L_cristalizacao_SL)  # negativo = energia liberada
    Q_biomassa_inicial = m_biomassa_inicial * Cp_biomassa * (T_inicial - T_final)
    Q_HCl_inicial = m_HCl_inicial * Cp_HCl_solucao * (T_inicial - T_final)
    Q_perdas_resfriamento = perdas_ambiente_kW * t_resfriamento_28_4 * 3600
    
    Q_part1 = Q_sf_sensivel - Q_sf_latente + Q_biomassa_inicial + Q_HCl_inicial + Q_perdas_resfriamento
    
    # PARTE 2: Manutenção componentes residuais (6h)
    Q_perdas_cristalizacao = perdas_ambiente_kW * t_manutencao_cristalizacao * 3600
    Q_part2 = Q_perdas_cristalizacao
    
    # PARTE 3: Resfriamento etanol + manutenção (2h)
    Q_etanol_sensivel = m_etanol_lavagem * Cp_etanol_70 * (T_ambiente - T_final)
    Q_perdas_lavagem = perdas_ambiente_kW * t_manutencao_lavagem * 3600
    Q_part3 = Q_etanol_sensivel + Q_perdas_lavagem
    
    # Total
    Q_total_remover = Q_part1 + Q_part2 + Q_part3
    
    # Energia elétrica
    E_eletrica_total = calcular_energia_chiller(Q_total_remover, COP)
    
    return {
        'Q_sf_sensivel_kJ': Q_sf_sensivel,
        'Q_sf_latente_kJ': Q_sf_latente,
        'Q_biomassa_inicial_kJ': Q_biomassa_inicial,
        'Q_HCl_inicial_kJ': Q_HCl_inicial,
        'Q_etanol_sensivel_kJ': Q_etanol_sensivel,
        'Q_perdas_total_kJ': Q_perdas_resfriamento + Q_perdas_cristalizacao + Q_perdas_lavagem,
        'Q_part1_kJ': Q_part1,
        'Q_part2_kJ': Q_part2,
        'Q_part3_kJ': Q_part3,
        'Q_total_remover_kJ': Q_total_remover,
        'E_eletrica_total_kWh': E_eletrica_total,
        'm_parte2_kg': m_biomassa_residual + m_HCl_residual + m_sf_cristalizar,
        'm_parte3_kg': m_biomassa_residual + m_HCl_residual + m_sf_cristalizar + m_etanol_lavagem
    }


def balanco_secador_completo(m_cristais_umidos, m_agua_evaporar, m_etanol_evaporar,
                           Cp_soforolipideos, Cp_agua, Cp_etanol_70,
                           T_inicial, T_final, L_vap_agua_45C, L_etanol_70,
                           perdas_ambiente_kW, tempo_h, eficiencia):
    """
    Balanço térmico CORRETO do secador - incluindo etanol
    
    Cristais: aquecimento 4°C → 45°C
    Água: aquecimento + vaporização  
    Etanol: aquecimento + vaporização
    """
    # Calor sensível para aquecer cristais
    Q_cristais_sensivel = m_cristais_umidos * Cp_soforolipideos * (T_final - T_inicial)
    
    # Calor para água: sensível + latente
    Q_agua_sensivel = m_agua_evaporar * Cp_agua * (T_final - T_inicial)
    Q_agua_latente = m_agua_evaporar * L_vap_agua_45C
    
    # Calor para etanol: sensível + latente  
    Q_etanol_sensivel = m_etanol_evaporar * Cp_etanol_70 * (T_final - T_inicial)
    Q_etanol_latente = m_etanol_evaporar * L_etanol_70
    
    # Total útil
    Q_total_util = Q_cristais_sensivel + Q_agua_sensivel + Q_agua_latente + Q_etanol_sensivel + Q_etanol_latente
    
    # Perdas para ambiente
    Q_perdas = perdas_ambiente_kW * tempo_h * 3600  # kW×h → kJ
    
    # Calor total a fornecer
    Q_total_fornecer = Q_total_util + Q_perdas
    
    # Energia elétrica (considerando eficiência)
    E_eletrica_total = Q_total_fornecer / (eficiencia * 3600)  # kJ → kWh
    
    return {
        'Q_cristais_sensivel_kJ': Q_cristais_sensivel,
        'Q_agua_sensivel_kJ': Q_agua_sensivel,
        'Q_agua_latente_kJ': Q_agua_latente,
        'Q_etanol_sensivel_kJ': Q_etanol_sensivel,
        'Q_etanol_latente_kJ': Q_etanol_latente,
        'Q_total_util_kJ': Q_total_util,
        'Q_perdas_kJ': Q_perdas,
        'Q_total_fornecer_kJ': Q_total_fornecer,
        'E_eletrica_total_kWh': E_eletrica_total
    }


def converter_kJ_para_kWh(valor_kJ):
    """Converte kJ para kWh"""
    return valor_kJ / 3600


def converter_kWh_para_kJ(valor_kWh):
    """Converte kWh para kJ"""
    return valor_kWh * 3600


def calcular_energia_total_equipamentos(equipamentos_dict):
    """
    Calcula energia total de uma lista de equipamentos
    
    Args:
        equipamentos_dict: dicionário {codigo: {'P_nom': kW, 'tempo': h}}
    
    Returns:
        dict com energia por equipamento e total
    """
    energias = {}
    total = 0
    
    for codigo, dados in equipamentos_dict.items():
        energia = calcular_energia_eletrica_equipamento(dados['P_nom'], dados['tempo'])
        energias[codigo] = energia
        total += energia
    
    energias['TOTAL'] = total
    return energias