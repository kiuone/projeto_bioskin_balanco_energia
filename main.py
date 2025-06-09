"""
main.py - Balanço Energético Completo dos Soforolipídeos
Execução principal dos cálculos de energia elétrica e térmica
"""
from src import constants as C
from src import calculations as calc
from copy import deepcopy

def main():
    print("="*60)
    print("BALANÇO ENERGÉTICO - PRODUÇÃO DE SOFOROLIPÍDEOS")
    print("="*60)
    
    # ================================================================
    # 1. BALANÇO TÉRMICO DO CHILLER
    # ================================================================
    print("\n1. CÁLCULO DO CHILLER (FT-101)")
    print("-" * 40)
    
    # Calcular balanço térmico do chiller
    resultado_chiller = calc.balanco_chiller_completo(
        m_soforolipideos_kg=C.m_soforolipideos_cristalizar,  # 90.6 kg
        Cp_soforolipideos=C.Cp_soforolipideos,               # 1.6 kJ/kg·K
        T_inicial=C.T_entrada_chiller,                       # 28°C
        T_final=C.T_cristalizacao,                           # 4°C
        L_cristalizacao_kJ_kg=C.L_cristalizacao_SL,          # 28.9 kJ/kg
        perdas_ambiente_kW=C.Q_perdas_V102,                  # 0.5 kW
        t_resfriamento_h=C.t_resfriamento_28_4,              # 5h
        t_manutencao_h=C.t_manutencao_cristalizacao + C.t_manutencao_lavagem,  # 6+2=8h
        COP=C.COP_chiller                                    # 3.0
    )
    
    # Mostrar resultados do chiller
    print(f"Q sensível (resfriamento): {resultado_chiller['Q_sensivel_kJ']:.1f} kJ")
    print(f"Q latente (cristalização): {resultado_chiller['Q_latente_kJ']:.1f} kJ (liberado)")
    print(f"Q parte 1 (resfriamento + cristalização): {resultado_chiller['Q_part1_kJ']:.1f} kJ")
    print(f"Q parte 2 (manutenção 8h): {resultado_chiller['Q_part2_kJ']:.1f} kJ")
    print(f"Q TOTAL removido: {resultado_chiller['Q_total_remover_kJ']:.1f} kJ")
    print(f"Energia elétrica TOTAL: {resultado_chiller['E_eletrica_total_kWh']:.2f} kWh")
    
    # Calcular potência média do chiller
    tempo_total_chiller = C.t_resfriamento_28_4 + C.t_manutencao_cristalizacao + C.t_manutencao_lavagem  # 13h
    potencia_media_chiller = resultado_chiller['E_eletrica_total_kWh'] / tempo_total_chiller
    print(f"Potência média: {potencia_media_chiller:.2f} kW")
    print(f"Tempo total operação: {tempo_total_chiller} h")
    
    # ================================================================
    # 2. BALANÇO TÉRMICO DO SECADOR
    # ================================================================
    print("\n2. CÁLCULO DO SECADOR (TDR-101)")
    print("-" * 40)
    
    # Calcular balanço térmico do secador
    resultado_secador = calc.balanco_secador_completo(
        m_agua_kg=C.m_agua_evaporar,                         # 1.0 kg
        Cp_agua=C.Cp_agua,                                   # 4.18 kJ/kg·K
        T_agua_inicial=C.T_entrada_secador,                  # 4°C
        T_evaporacao=C.T_secagem,                            # 45°C
        L_vap_agua_kJ_kg=C.L_vap_agua_45C,                   # 2400 kJ/kg
        perdas_ambiente_kW=C.Q_perdas_TDR101,                # 2.0 kW
        tempo_h=C.t_secagem,                                 # 12h
        eficiencia=C.eficiencia_secador                      # 0.8
    )
    
    # Mostrar resultados do secador
    print(f"Q água sensível (4→45°C): {resultado_secador['Q_agua_sensivel_kJ']:.1f} kJ")
    print(f"Q água latente (vaporização): {resultado_secador['Q_agua_latente_kJ']:.1f} kJ")
    print(f"Q água total útil: {resultado_secador['Q_agua_total_kJ']:.1f} kJ")
    print(f"Q perdas ambiente (12h): {resultado_secador['Q_perdas_kJ']:.1f} kJ")
    print(f"Q TOTAL fornecido: {resultado_secador['Q_total_fornecer_kJ']:.1f} kJ")
    print(f"Energia elétrica TOTAL: {resultado_secador['E_eletrica_total_kWh']:.2f} kWh")
    
    # Calcular potência média do secador
    potencia_media_secador = resultado_secador['E_eletrica_total_kWh'] / C.t_secagem
    print(f"Potência média: {potencia_media_secador:.2f} kW")
    print(f"Tempo total operação: {C.t_secagem} h")
    
    # ================================================================
    # 3. ATUALIZAR EQUIPAMENTOS COM POTÊNCIAS CALCULADAS
    # ================================================================
    print("\n3. ATUALIZANDO POTÊNCIAS CALCULADAS")
    print("-" * 40)
    
    # Fazer cópia dos equipamentos para não modificar o original
    equipamentos_atualizados = deepcopy(C.equipamentos_processo)
    
    # Atualizar chiller
    equipamentos_atualizados['FT-101']['P_nom'] = potencia_media_chiller
    print(f"FT-101 (Chiller): {potencia_media_chiller:.2f} kW")
    
    # Atualizar secador
    equipamentos_atualizados['TDR-101']['P_nom'] = potencia_media_secador
    print(f"TDR-101 (Secador): {potencia_media_secador:.2f} kW")
    
    # ================================================================
    # 4. CALCULAR ENERGIA TOTAL DE TODOS OS EQUIPAMENTOS
    # ================================================================
    print("\n4. ENERGIA ELÉTRICA POR EQUIPAMENTO")
    print("-" * 40)
    
    # Calcular energia de cada equipamento
    energias_equipamentos = calc.calcular_energia_total_equipamentos(equipamentos_atualizados)
    
    # Mostrar resultados individuais
    total_processo = 0
    for codigo, energia in energias_equipamentos.items():
        if codigo != 'TOTAL':
            dados = equipamentos_atualizados[codigo]
            print(f"{codigo:12} | {dados['P_nom']:6.2f} kW × {dados['tempo']:3.0f} h = {energia:7.2f} kWh")
            total_processo += energia
    
    print("-" * 55)
    print(f"{'TOTAL PROCESSO':12} | {' ':13} = {total_processo:7.2f} kWh")
    
    # ================================================================
    # 5. RESUMO ENERGÉTICO FINAL
    # ================================================================
    print("\n5. RESUMO ENERGÉTICO TOTAL")
    print("=" * 40)
    
    # Energias por categoria
    energia_processo = total_processo
    energia_utilidades = C.E_utilidades_fixas_total
    energia_total = energia_processo + energia_utilidades
    
    print(f"Equipamentos de Processo: {energia_processo:8.1f} kWh ({energia_processo/energia_total*100:.1f}%)")
    print(f"Utilidades Fixas:         {energia_utilidades:8.1f} kWh ({energia_utilidades/energia_total*100:.1f}%)")
    print("-" * 45)
    print(f"TOTAL POR LOTE:           {energia_total:8.1f} kWh")
    
    # Consumo específico
    massa_produto_final = C.m_cristais_secos  # 80.8 kg
    consumo_especifico = energia_total / massa_produto_final
    print(f"\nConsumo específico:       {consumo_especifico:8.1f} kWh/kg produto")
    
    # ================================================================
    # 6. VERIFICAÇÕES DE CONSISTÊNCIA
    # ================================================================
    print("\n6. VERIFICAÇÕES")
    print("-" * 40)
    
    # Comparar com valores esperados (seus cálculos manuais)
    chiller_esperado = 6057 / (3.0 * 3600) + (0.5 * 8 * 3600) / (3.0 * 3600)  # conforme seus cálculos
    secador_esperado = (171.3 + 2400 + 86400) / (0.8 * 3600)  # conforme seus cálculos
    
    print(f"Chiller calculado: {resultado_chiller['E_eletrica_total_kWh']:.2f} kWh")
    print(f"Chiller esperado:  {chiller_esperado:.2f} kWh")
    print(f"Diferença chiller: {abs(resultado_chiller['E_eletrica_total_kWh'] - chiller_esperado):.2f} kWh")
    
    print(f"Secador calculado: {resultado_secador['E_eletrica_total_kWh']:.2f} kWh")
    print(f"Secador esperado:  {secador_esperado:.2f} kWh")
    print(f"Diferença secador: {abs(resultado_secador['E_eletrica_total_kWh'] - secador_esperado):.2f} kWh")
    
    return {
        'chiller': resultado_chiller,
        'secador': resultado_secador,
        'equipamentos': equipamentos_atualizados,
        'energia_total': energia_total,
        'consumo_especifico': consumo_especifico
    }

if __name__ == "__main__":
    resultados = main()