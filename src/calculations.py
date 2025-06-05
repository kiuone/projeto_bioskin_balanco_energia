# ============================================================================
# calculations.py
# ============================================================================

"""
Cálculos energéticos para o balanço de energia - Produção de Soforolipídeos
Aplicação rigorosa da 1ª Lei da Termodinâmica
"""

import copy
from typing import Dict, Tuple
from src import constants as C

def calculate_sensible_heat(massa: float, cp: float, delta_t: float) -> float:
    """
    Calcula calor sensível: Q = m × Cp × |ΔT|
    
    Args:
        massa: massa em kg
        cp: calor específico em kJ/kg·K
        delta_t: diferença de temperatura em °C
    
    Returns:
        Calor sensível em kWh
    """
    return (massa * cp * abs(delta_t)) * C.kJ_para_kWh

def calculate_latent_heat(massa: float, delta_h: float) -> float:
    """
    Calcula calor latente: Q = m × ΔH
    
    Args:
        massa: massa em kg
        delta_h: entalpia específica em kJ/kg
    
    Returns:
        Calor latente em kWh
    """
    return (massa * delta_h) * C.kJ_para_kWh

def calculate_metabolic_heat(co2_mass: float, dh_metabolic: float) -> float:
    """
    Calcula calor metabólico baseado na produção de CO2
    
    Args:
        co2_mass: massa de CO2 produzida em kg
        dh_metabolic: calor metabólico específico em kJ/mol O2
    
    Returns:
        Calor metabólico em kWh
    """
    n_co2_mol = (co2_mass * 1000) / C.peso_molecular_co2  # mol
    n_o2_mol = n_co2_mol  # assumindo estequiometria 1:1
    return (n_o2_mol * dh_metabolic) * C.kJ_para_kWh

def calculate_electrical_energy() -> Dict[str, float]:
    """
    Calcula energia elétrica total incluindo equipamentos otimizados
    """
    # Cópia dos equipamentos base para modificação
    equipamentos = copy.deepcopy(C.equipamentos_base)
    
    # Se não usar caldeira, adicionar aquecedor elétrico para esterilização
    if not C.USE_BOILER:
        equipamentos['EL-STER'] = {
            'nome': 'Aquecedor elétrico esterilização',
            'P_nom': 25.0,
            'P_avg': 25.0,
            'h': 3.0,
            'kWh': 75.0  # 25 kW × 3 h = 75 kWh
        }
    
    # Calcular consumo total dos equipamentos
    E_processo_total = sum([equip['kWh'] for equip in equipamentos.values()])
    E_eletrica_total = E_processo_total + C.E_utilidades_fixas
    consumo_especifico = E_eletrica_total / C.m_soforolipideos_final
    
    return {
        'equipamentos': equipamentos,
        'E_processo_total': E_processo_total,
        'E_eletrica_total': E_eletrica_total,
        'consumo_especifico': consumo_especifico
    }

def calculate_thermal_loads() -> Dict[str, float]:
    """
    Calcula todas as cargas térmicas por etapa do processo
    """
    # ESTERILIZAÇÃO
    # Aquecimento
    Q_aquecimento_meio = calculate_sensible_heat(
        C.m_meio_fermentador, C.Cp_meio_aquoso, 
        C.T_esterilizacao_meio - C.T_ambiente
    )
    Q_aquecimento_oleo = calculate_sensible_heat(
        C.m_oleo_vegetal, C.Cp_oleo_soja,
        C.T_esterilizacao_oleo - C.T_ambiente
    )
    
    # Calor latente de condensação do vapor (55 kg de água evaporada)
    Q_latente_esterilizacao = calculate_latent_heat(
        C.agua_evaporada_secagem, C.DH_vap_agua_45C
    )
    
    # Resfriamento pós-esterilização
    Q_resfriamento_meio = calculate_sensible_heat(
        C.m_meio_fermentador, C.Cp_meio_aquoso,
        C.T_esterilizacao_meio - C.T_fermentacao
    )
    Q_resfriamento_oleo = calculate_sensible_heat(
        C.m_oleo_vegetal, C.Cp_oleo_soja,
        C.T_esterilizacao_oleo - C.T_fermentacao
    )
    
    Q_esterilizacao_total = (Q_aquecimento_meio + Q_aquecimento_oleo + 
                           Q_latente_esterilizacao + Q_resfriamento_meio + 
                           Q_resfriamento_oleo)
    
    # FERMENTAÇÃO
    # Calor metabólico
    Q_metabolico = calculate_metabolic_heat(C.m_co2_produzido, C.DH_metabolico)
    
    # Dissipação de trabalho mecânico (frações que viram calor no processo)
    Q_agitacao_dissipada = C.equipamentos_base['FR-101']['kWh'] * C.fator_agitacao_calor
    Q_aeracao_dissipada = C.equipamentos_base['BLW-101']['kWh'] * C.fator_aeracao_calor
    Q_bombas_dissipada = C.equipamentos_base['PUMPS']['kWh'] * C.fator_bomba_calor
    
    Q_fermentacao_total = (Q_metabolico + Q_agitacao_dissipada + 
                          Q_aeracao_dissipada + Q_bombas_dissipada)
    
    # CRISTALIZAÇÃO
    # Resfriamento sensível
    Q_resfriamento_cristalizacao = calculate_sensible_heat(
        C.m_fase_solida_decantador, C.Cp_meio_bifasico,
        C.T_fermentacao - C.T_cristalizacao
    )
    
    # Calor latente de cristalização (apenas 85 kg de SL que cristalizam)
    massa_SL_cristalizada = 85.0  # kg - conforme correção
    Q_latente_cristalizacao = calculate_latent_heat(
        massa_SL_cristalizada, C.DH_cristalizacao_SL
    )
    
    Q_cristalizacao_total = Q_resfriamento_cristalizacao + Q_latente_cristalizacao
    
    # SECAGEM
    # Aquecimento dos cristais
    Q_aquecimento_cristais = calculate_sensible_heat(
        C.m_cristais_pos_centrifugacao, C.Cp_soforolipideos,
        C.T_secagem - C.T_cristalizacao
    )
    
    # Vaporização da água residual (55 kg)
    Q_vaporizacao_agua = calculate_latent_heat(
        C.agua_evaporada_secagem, C.DH_vap_agua_45C
    )
    
    Q_secagem_total = Q_aquecimento_cristais + Q_vaporizacao_agua
    
    # TOTAL
    Q_total_processo = (Q_esterilizacao_total + Q_fermentacao_total + 
                       Q_cristalizacao_total + Q_secagem_total)
    
    return {
        # Esterilização
        'Q_aquecimento_meio': Q_aquecimento_meio,
        'Q_aquecimento_oleo': Q_aquecimento_oleo,
        'Q_latente_esterilizacao': Q_latente_esterilizacao,
        'Q_resfriamento_meio': Q_resfriamento_meio,
        'Q_resfriamento_oleo': Q_resfriamento_oleo,
        'Q_esterilizacao_total': Q_esterilizacao_total,
        
        # Fermentação
        'Q_metabolico': Q_metabolico,
        'Q_agitacao_dissipada': Q_agitacao_dissipada,
        'Q_aeracao_dissipada': Q_aeracao_dissipada,
        'Q_bombas_dissipada': Q_bombas_dissipada,
        'Q_fermentacao_total': Q_fermentacao_total,
        
        # Cristalização
        'Q_resfriamento_cristalizacao': Q_resfriamento_cristalizacao,
        'Q_latente_cristalizacao': Q_latente_cristalizacao,
        'Q_cristalizacao_total': Q_cristalizacao_total,
        
        # Secagem
        'Q_aquecimento_cristais': Q_aquecimento_cristais,
        'Q_vaporizacao_agua': Q_vaporizacao_agua,
        'Q_secagem_total': Q_secagem_total,
        
        # Total
        'Q_total_processo': Q_total_processo
    }

def calculate_heat_losses(thermal_results: Dict[str, float]) -> Dict[str, float]:
    """
    Calcula perdas térmicas baseadas em percentuais fixos por etapa
    """
    perdas_esterilizacao = thermal_results['Q_esterilizacao_total'] * C.perdas_esterilizacao_pct
    perdas_fermentacao = thermal_results['Q_fermentacao_total'] * C.perdas_fermentacao_pct
    perdas_cristalizacao = thermal_results['Q_cristalizacao_total'] * C.perdas_cristalizacao_pct
    perdas_secagem = thermal_results['Q_secagem_total'] * C.perdas_secagem_pct
    
    perdas_termicas_total = (perdas_esterilizacao + perdas_fermentacao + 
                           perdas_cristalizacao + perdas_secagem)
    
    return {
        'perdas_esterilizacao': perdas_esterilizacao,
        'perdas_fermentacao': perdas_fermentacao,
        'perdas_cristalizacao': perdas_cristalizacao,
        'perdas_secagem': perdas_secagem,
        'perdas_termicas_total': perdas_termicas_total
    }

def calculate_chemical_energy() -> Dict[str, float]:
    """
    Calcula energia química das matérias-primas e produtos (HHV)
    """
    if not C.INCLUDE_HHV:
        return {
            'E_quimica_entrada': 0.0,
            'E_quimica_saida': 0.0,
            'E_quimica_liquida': 0.0
        }
    
    # Energia química de entrada
    E_quimica_entrada = (
        C.m_sacarose * C.HHV_sacarose +
        C.m_oleo_vegetal * C.HHV_oleo_vegetal
    ) * C.MJ_para_kWh
    
    # Energia química de saída
    E_quimica_saida = (
        C.m_soforolipideos_final * C.HHV_soforolipideos +
        C.m_biomassa_final * C.HHV_biomassa
    ) * C.MJ_para_kWh
    
    E_quimica_liquida = E_quimica_entrada - E_quimica_saida
    
    return {
        'E_quimica_entrada': E_quimica_entrada,
        'E_quimica_saida': E_quimica_saida,
        'E_quimica_liquida': E_quimica_liquida
    }

def update_chiller_consumption(equipamentos: Dict[str, Dict], Q_total_processo: float) -> Dict[str, float]:
    """
    Recalcula e atualiza o consumo do chiller baseado na carga térmica total
    """
    Q_chiller_original = equipamentos['FT-101']['kWh']
    Q_chiller_recalculado = Q_total_processo / C.COP_chiller
    
    # Sobrescrever valor na tabela de equipamentos
    equipamentos['FT-101']['kWh'] = Q_chiller_recalculado
    equipamentos['FT-101']['P_avg'] = Q_chiller_recalculado / equipamentos['FT-101']['h']
    
    desvio_chiller = abs(Q_chiller_recalculado - Q_chiller_original) / Q_chiller_original
    
    return {
        'Q_chiller_original': Q_chiller_original,
        'Q_chiller_recalculado': Q_chiller_recalculado,
        'desvio_chiller': desvio_chiller
    }