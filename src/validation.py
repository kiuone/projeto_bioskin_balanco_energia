# ============================================================================
# validation.py
# ============================================================================

"""
Validações e verificações do balanço de energia
Aplicação da 1ª Lei da Termodinâmica e testes de consistência
"""

from typing import Dict, List, Tuple
from src import constants as C

def validate_energy_balance(electrical_results: Dict[str, float], 
                          thermal_results: Dict[str, float],
                          losses_results: Dict[str, float],
                          chemical_results: Dict[str, float]) -> Dict[str, float]:
    """
    Valida o fechamento do balanço energético aplicando a 1ª Lei da Termodinâmica
    """
    # ENTRADAS
    E_entrada_eletrica = electrical_results['E_eletrica_total']
    E_entrada_vapor = 0.0
    
    # Se usar caldeira, adicionar energia do vapor para esterilização
    if C.USE_BOILER:
        Q_aquecimento_total = (thermal_results['Q_aquecimento_meio'] + 
                              thermal_results['Q_aquecimento_oleo'] +
                              thermal_results['Q_latente_esterilizacao'])
        E_entrada_vapor = Q_aquecimento_total / C.eficiencia_caldeira
    
    E_entrada_quimica = chemical_results['E_quimica_entrada']
    E_entrada_total = E_entrada_eletrica + E_entrada_vapor + E_entrada_quimica
    
    # SAÍDAS
    E_saida_calor = thermal_results['Q_total_processo']
    E_saida_perdas = losses_results['perdas_termicas_total']
    E_saida_produtos = chemical_results['E_quimica_saida']
    E_saida_trabalho = 0.0  # Trabalho útil líquido desprezível
    E_saida_total = E_saida_calor + E_saida_perdas + E_saida_produtos + E_saida_trabalho
    
    # FECHAMENTO
    erro_balanco = abs(E_entrada_total - E_saida_total) / E_entrada_total
    balanco_fechado = erro_balanco < C.TOLERANCIA_BALANCO
    
    return {
        'E_entrada_eletrica': E_entrada_eletrica,
        'E_entrada_vapor': E_entrada_vapor,
        'E_entrada_quimica': E_entrada_quimica,
        'E_entrada_total': E_entrada_total,
        'E_saida_calor': E_saida_calor,
        'E_saida_perdas': E_saida_perdas,
        'E_saida_produtos': E_saida_produtos,
        'E_saida_trabalho': E_saida_trabalho,
        'E_saida_total': E_saida_total,
        'erro_balanco': erro_balanco,
        'balanco_fechado': balanco_fechado
    }

def validate_chiller_consistency(chiller_results: Dict[str, float]) -> Dict[str, bool]:
    """
    Valida a consistência do chiller recalculado
    """
    desvio_aceitavel = chiller_results['desvio_chiller'] < C.TOLERANCIA_CHILLER
    
    return {
        'chiller_consistente': desvio_aceitavel,
        'desvio_percentual': chiller_results['desvio_chiller']
    }

def validate_physical_ranges(all_results: Dict[str, float]) -> Dict[str, bool]:
    """
    Valida se todos os valores estão em faixas fisicamente coerentes
    """
    checks = {}
    
    # Energias devem ser positivas
    energy_keys = [k for k in all_results.keys() if 'E_' in k or 'Q_' in k]
    checks['energias_positivas'] = all(all_results[k] >= 0 for k in energy_keys)
    
    # Temperaturas devem estar em faixas razoáveis
    temps = [C.T_ambiente, C.T_fermentacao, C.T_cristalizacao, C.T_secagem]
    checks['temperaturas_fisicas'] = all(t >= -10 and t <= 150 for t in temps)
    
    # Consumo específico deve estar em faixa típica (50-200 kWh/kg)
    consumo_esp = all_results.get('consumo_especifico', 0)
    checks['consumo_especifico_razoavel'] = 30 <= consumo_esp <= 250
    
    # Erro do balanço deve ser menor que tolerância
    erro = all_results.get('erro_balanco', 1.0)
    checks['erro_balanco_aceitavel'] = erro < C.TOLERANCIA_BALANCO
    
    return checks

def validate_mass_balance_consistency() -> Dict[str, bool]:
    """
    Valida consistência com dados do balanço de massa
    """
    checks = {}
    
    # Verificar se CO2 está consistente com metabolismo
    # Relação típica: ~0.6 kg CO2/kg produto em fermentação de leveduras
    relacao_co2_produto = C.m_co2_produzido / C.m_soforolipideos_final
    checks['co2_produto_coerente'] = 0.5 <= relacao_co2_produto <= 2.0
    
    # Verificar se água evaporada é coerente
    checks['agua_evaporada_coerente'] = 10 <= C.agua_evaporada_secagem <= 100
    
    # Verificar se massas batem (entrada vs saída aproximadamente)
    massa_entrada_total = (C.m_sacarose + C.m_oleo_vegetal + C.m_ureia + 
                          C.m_sais_minerais + C.m_agua_total + C.m_hcl + C.m_etanol)
    massa_saida_total = (C.m_soforolipideos_final + C.m_biomassa_final + 
                        C.m_oleo_residual + C.m_fase_aquosa + C.m_co2_produzido)
    
    desvio_massa = abs(massa_entrada_total - massa_saida_total) / massa_entrada_total
    checks['balanco_massa_coerente'] = desvio_massa < 0.15  # 15% tolerância
    
    return checks

def test_energy_units(results_dict: Dict[str, float]) -> Dict[str, bool]:
    """
    Verifica se todas as energias estão em kWh (teste de unidades)
    """
    # Para este teste, assumimos que todas as chaves com 'E_' ou 'Q_' são energias em kWh
    energy_keys = [k for k in results_dict.keys() if 'E_' in k or 'Q_' in k]
    
    # Verificar se valores estão em faixas típicas para kWh (não kJ ou MJ)
    unit_checks = {}
    for key in energy_keys:
        value = results_dict[key]
        # kWh típicos para este processo: 0.1 a 10000 kWh
        # Se fosse kJ seria muito maior, se fosse MJ seria bem menor
        unit_checks[f'{key}_unidade_kWh'] = 0.001 <= value <= 50000
    
    unit_checks['todas_unidades_corretas'] = all(unit_checks.values())
    
    return unit_checks

def generate_validation_summary(all_validations: Dict[str, Dict]) -> str:
    """
    Gera resumo textual de todas as validações
    """
    summary = "=== RELATÓRIO DE VALIDAÇÕES ===\n\n"
    
    for validation_name, validation_results in all_validations.items():
        summary += f"{validation_name.upper()}:\n"
        for check_name, check_result in validation_results.items():
            status = "✓ PASSOU" if check_result else "✗ FALHOU"
            summary += f"  - {check_name}: {status}\n"
        summary += "\n"
    
    return summary