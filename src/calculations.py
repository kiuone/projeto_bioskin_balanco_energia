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


def calcular_energia_chiller(Q_removido_kJ, COP):
    """
    Calcula energia elétrica do chiller: E = Q_removido / COP
    Conversão automática kJ → kWh
    """
    energia_kWh = Q_removido_kJ / (COP * 3600)
    return energia_kWh


def balanco_chiller_completo(m_soforolipideos_kg, Cp_soforolipideos, T_inicial, T_final,
                            L_cristalizacao_kJ_kg, perdas_ambiente_kW, 
                            t_resfriamento_h, t_manutencao_h, COP):
    """
    Balanço térmico completo do chiller conforme seus cálculos
    
    PARTE 1: Resfriamento 28°C → 4°C + cristalização
    PARTE 2: Manutenção a 4°C (6h cristalização + 2h lavagem)
    """
    # PARTE 1: Resfriamento + cristalização (5h)
    Q_sensivel = m_soforolipideos_kg * Cp_soforolipideos * (T_inicial - T_final)
    Q_latente = m_soforolipideos_kg * (-L_cristalizacao_kJ_kg)  # negativo = calor liberado
    Q_part1 = Q_sensivel - Q_latente  # subtrai porque cristalização libera calor
    
    # PARTE 2: Manutenção a 4°C (8h total)
    Q_part2 = perdas_ambiente_kW * t_manutencao_h * 3600  # kW×h → kJ
    
    # Total
    Q_total_remover = Q_part1 + Q_part2
    
    # Energia elétrica
    E_eletrica_total = calcular_energia_chiller(Q_total_remover, COP)
    E_eletrica_part1 = calcular_energia_chiller(Q_part1, COP)
    E_eletrica_part2 = calcular_energia_chiller(Q_part2, COP)
    
    return {
        'Q_sensivel_kJ': Q_sensivel,
        'Q_latente_kJ': Q_latente,
        'Q_part1_kJ': Q_part1,
        'Q_part2_kJ': Q_part2,
        'Q_total_remover_kJ': Q_total_remover,
        'E_eletrica_total_kWh': E_eletrica_total,
        'E_eletrica_part1_kWh': E_eletrica_part1,
        'E_eletrica_part2_kWh': E_eletrica_part2
    }


def balanco_secador_completo(m_agua_kg, Cp_agua, T_agua_inicial, T_evaporacao,
                           L_vap_agua_kJ_kg, perdas_ambiente_kW, tempo_h, eficiencia):
    """
    Balanço térmico do secador conforme seus cálculos
    
    Cristais: 81.8 kg (não precisa Cp porque mantém temperatura constante)
    Água: 1.0 kg (4°C → 45°C → vapor)
    """
    # Calor sensível para aquecer água até evaporação
    Q_agua_sensivel = m_agua_kg * Cp_agua * (T_evaporacao - T_agua_inicial)
    
    # Calor latente para vaporizar água
    Q_agua_latente = m_agua_kg * L_vap_agua_kJ_kg
    
    # Total útil
    Q_agua_total = Q_agua_sensivel + Q_agua_latente
    
    # Perdas para ambiente
    Q_perdas = perdas_ambiente_kW * tempo_h * 3600  # kW×h → kJ
    
    # Calor total a fornecer
    Q_total_fornecer = Q_agua_total + Q_perdas
    
    # Energia elétrica (considerando eficiência)
    E_eletrica_total = Q_total_fornecer / (eficiencia * 3600)  # kJ → kWh
    
    return {
        'Q_agua_sensivel_kJ': Q_agua_sensivel,
        'Q_agua_latente_kJ': Q_agua_latente,
        'Q_agua_total_kJ': Q_agua_total,
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