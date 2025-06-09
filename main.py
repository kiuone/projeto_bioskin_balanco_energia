"""
main.py - Balanço Energético Completo dos Soforolipídeos
Execução principal dos cálculos de energia elétrica e térmica + Visualizações
VERSÃO COM FORMATAÇÃO BRASILEIRA
"""

from src import constants as C
from src import calculations as calc
from src import visualization as viz
# from src import formatacao_brasileira
from formatacao_brasileira import *
from copy import deepcopy

def main():
    print("="*60)
    print("BALANÇO ENERGÉTICO - PRODUÇÃO DE SOFOROLIPÍDEOS")
    print("="*60)
    
    # ================================================================
    # 1. BALANÇO TÉRMICO DO CHILLER (COMPONENTES SEPARADOS)
    # ================================================================
    print("\n1. CÁLCULO DO CHILLER (FT-101) - COMPONENTES SEPARADOS")
    print("-" * 60)
    
    # Calcular balanço térmico do chiller com componentes separados
    resultado_chiller = calc.balanco_chiller_completo(
        m_sf_inicial=C.m_sf_inicial,                        # 95.6 kg SF antes cristalização
        m_biomassa_inicial=C.m_biomassa_inicial,            # 25.52 kg biomassa do decantador
        m_HCl_inicial=C.m_HCl_inicial,                      # 37.75 kg HCl total adicionado
        m_biomassa_residual=C.m_biomassa_residual,          # 1.0 kg biomassa residual
        m_HCl_residual=C.m_HCl_residual,                    # 2.0 kg HCl residual
        m_sf_cristalizar=C.m_sf_cristalizar,                # 90.6 kg SF após cristalização
        m_etanol_lavagem=C.m_etanol_lavagem,                # 75.42 kg etanol para lavagem
        Cp_soforolipideos=C.Cp_soforolipideos,              # 1.6 kJ/kg·K
        Cp_biomassa=C.Cp_biomassa,                          # 3.5 kJ/kg·K
        Cp_HCl_solucao=C.Cp_HCl_solucao,                    # 3.8 kJ/kg·K
        Cp_etanol_70=C.Cp_etanol_70,                        # 1.86 kJ/kg·K
        T_inicial=C.T_entrada_chiller,                      # 28°C
        T_final=C.T_cristalizacao,                          # 4°C
        T_ambiente=C.T_ambiente,                            # 25°C (temperatura etanol)
        L_cristalizacao_SL=C.L_cristalizacao_SL,            # 28.9 kJ/kg
        perdas_ambiente_kW=C.Q_perdas_V102,                 # 0.5 kW
        t_resfriamento_28_4=C.t_resfriamento_28_4,          # 5h
        t_manutencao_cristalizacao=C.t_manutencao_cristalizacao,  # 6h
        t_manutencao_lavagem=C.t_manutencao_lavagem,        # 2h
        COP=C.COP_chiller                                   # 3.0
    )
    
    # Mostrar resultados do chiller detalhadamente - FORMATAÇÃO BRASILEIRA
    print(f"PARTE 1 (5h) - Resfriamento 28°C→4°C + Cristalização:")
    print(f"  Q SF sensível ({formatar_massa_brasileiro(95.6)}): {formatar_numero_brasileiro(resultado_chiller['Q_sf_sensivel_kJ'], 1)} kJ")
    print(f"  Q SF latente ({formatar_massa_brasileiro(95.6)}): {formatar_numero_brasileiro(resultado_chiller['Q_sf_latente_kJ'], 1)} kJ (liberado)")
    print(f"  Q biomassa ({formatar_massa_brasileiro(25.52)}): {formatar_numero_brasileiro(resultado_chiller['Q_biomassa_inicial_kJ'], 1)} kJ")
    print(f"  Q HCl ({formatar_massa_brasileiro(37.75)}): {formatar_numero_brasileiro(resultado_chiller['Q_HCl_inicial_kJ'], 1)} kJ")
    print(f"  Q perdas ambiente: {formatar_numero_brasileiro(resultado_chiller['Q_perdas_total_kJ']/3, 1)} kJ")
    print(f"  SUBTOTAL PARTE 1: {formatar_numero_brasileiro(resultado_chiller['Q_part1_kJ'], 1)} kJ")
    
    print(f"PARTE 2 (6h) - Manutenção {formatar_massa_brasileiro(resultado_chiller['m_parte2_kg'])}:")
    print(f"  Q perdas ambiente: {formatar_numero_brasileiro(resultado_chiller['Q_perdas_total_kJ']/3, 1)} kJ")
    print(f"  SUBTOTAL PARTE 2: {formatar_numero_brasileiro(resultado_chiller['Q_part2_kJ'], 1)} kJ")
    
    print(f"PARTE 3 (2h) - Lavagem {formatar_massa_brasileiro(resultado_chiller['m_parte3_kg'])}:")
    print(f"  Q etanol sensível ({formatar_massa_brasileiro(75.42)}): {formatar_numero_brasileiro(resultado_chiller['Q_etanol_sensivel_kJ'], 1)} kJ")
    print(f"  Q perdas ambiente: {formatar_numero_brasileiro(resultado_chiller['Q_perdas_total_kJ']/3, 1)} kJ")
    print(f"  SUBTOTAL PARTE 3: {formatar_numero_brasileiro(resultado_chiller['Q_part3_kJ'], 1)} kJ")
    
    print(f"Q TOTAL removido: {formatar_numero_brasileiro(resultado_chiller['Q_total_remover_kJ'], 1)} kJ")
    print(f"Energia elétrica TOTAL: {formatar_energia_brasileiro(resultado_chiller['E_eletrica_total_kWh'], 2)}")
    
    # Calcular potência média do chiller
    tempo_total_chiller = C.t_resfriamento_28_4 + C.t_manutencao_cristalizacao + C.t_manutencao_lavagem  # 13h
    potencia_media_chiller = resultado_chiller['E_eletrica_total_kWh'] / tempo_total_chiller
    print(f"Potência média: {formatar_potencia_brasileiro(potencia_media_chiller)}")
    print(f"Tempo total operação: {tempo_total_chiller} h")
    
    # ================================================================
    # 2. BALANÇO TÉRMICO DO SECADOR (INCLUINDO ETANOL)
    # ================================================================
    print("\n2. CÁLCULO DO SECADOR (TDR-101) - INCLUINDO ETANOL")
    print("-" * 60)
    
    # Calcular balanço térmico do secador incluindo etanol
    resultado_secador = calc.balanco_secador_completo(
        m_cristais_umidos=C.m_cristais_umidos,              # 81.8 kg cristais
        m_agua_evaporar=C.m_agua_evaporar,                  # 1.0 kg água
        m_etanol_evaporar=C.m_etanol_evaporar,              # 1.0 kg etanol
        Cp_soforolipideos=C.Cp_soforolipideos,              # 1.6 kJ/kg·K
        Cp_agua=C.Cp_agua,                                  # 4.18 kJ/kg·K
        Cp_etanol_70=C.Cp_etanol_70,                        # 1.86 kJ/kg·K
        T_inicial=C.T_entrada_secador,                      # 4°C
        T_final=C.T_secagem,                                # 45°C
        L_vap_agua_45C=C.L_vap_agua_45C,                    # 2400 kJ/kg
        L_etanol_70=C.L_etanol_70,                          # 850 kJ/kg
        perdas_ambiente_kW=C.Q_perdas_TDR101,               # 2.0 kW
        tempo_h=C.t_secagem,                                # 12h
        eficiencia=C.eficiencia_secador                     # 0.8
    )
    
    # Mostrar resultados do secador detalhadamente - FORMATAÇÃO BRASILEIRA
    print(f"AQUECIMENTO (4°C→45°C):")
    print(f"  Q cristais sensível ({formatar_massa_brasileiro(81.8)}): {formatar_numero_brasileiro(resultado_secador['Q_cristais_sensivel_kJ'], 1)} kJ")
    print(f"  Q água sensível ({formatar_massa_brasileiro(1.0)}): {formatar_numero_brasileiro(resultado_secador['Q_agua_sensivel_kJ'], 1)} kJ")
    print(f"  Q etanol sensível ({formatar_massa_brasileiro(1.0)}): {formatar_numero_brasileiro(resultado_secador['Q_etanol_sensivel_kJ'], 1)} kJ")
    
    print(f"EVAPORAÇÃO (45°C):")
    print(f"  Q água latente ({formatar_massa_brasileiro(1.0)}): {formatar_numero_brasileiro(resultado_secador['Q_agua_latente_kJ'], 1)} kJ")
    print(f"  Q etanol latente ({formatar_massa_brasileiro(1.0)}): {formatar_numero_brasileiro(resultado_secador['Q_etanol_latente_kJ'], 1)} kJ")
    
    print(f"Q ÚTIL total: {formatar_numero_brasileiro(resultado_secador['Q_total_util_kJ'], 1)} kJ")
    print(f"Q perdas ambiente (12h): {formatar_numero_brasileiro(resultado_secador['Q_perdas_kJ'], 1)} kJ")
    print(f"Q TOTAL fornecido: {formatar_numero_brasileiro(resultado_secador['Q_total_fornecer_kJ'], 1)} kJ")
    print(f"Energia elétrica TOTAL: {formatar_energia_brasileiro(resultado_secador['E_eletrica_total_kWh'], 2)}")
    
    # Calcular potência média do secador
    potencia_media_secador = resultado_secador['E_eletrica_total_kWh'] / C.t_secagem
    print(f"Potência média: {formatar_potencia_brasileiro(potencia_media_secador)}")
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
    print(f"FT-101 (Chiller): {formatar_potencia_brasileiro(potencia_media_chiller)}")
    
    # Atualizar secador
    equipamentos_atualizados['TDR-101']['P_nom'] = potencia_media_secador
    print(f"TDR-101 (Secador): {formatar_potencia_brasileiro(potencia_media_secador)}")
    
    # ================================================================
    # 4. CALCULAR ENERGIA TOTAL DE TODOS OS EQUIPAMENTOS
    # ================================================================
    print("\n4. ENERGIA ELÉTRICA POR EQUIPAMENTO")
    print("-" * 40)
    
    # Calcular energia de cada equipamento
    energias_equipamentos = calc.calcular_energia_total_equipamentos(equipamentos_atualizados)
    
    # Mostrar resultados individuais - FORMATAÇÃO BRASILEIRA
    total_processo = 0
    for codigo, energia in energias_equipamentos.items():
        if codigo != 'TOTAL':
            dados = equipamentos_atualizados[codigo]
            print(f"{codigo:12} | {formatar_potencia_brasileiro(dados['P_nom'], 2):>10} × {dados['tempo']:3.0f} h = {formatar_energia_brasileiro(energia, 2):>12}")
            total_processo += energia
    
    print("-" * 65)
    print(f"{'TOTAL PROCESSO':12} | {' ':16} = {formatar_energia_brasileiro(total_processo, 2):>12}")
    
    # ================================================================
    # 5. RESUMO ENERGÉTICO FINAL
    # ================================================================
    print("\n5. RESUMO ENERGÉTICO TOTAL")
    print("=" * 40)
    
    # Energias por categoria
    energia_processo = total_processo
    energia_utilidades = C.E_utilidades_fixas_total
    energia_total = energia_processo + energia_utilidades
    
    print(f"Equipamentos de Processo: {formatar_energia_brasileiro(energia_processo, 1):>12} ({formatar_percentual_brasileiro(energia_processo/energia_total*100, 1)})")
    print(f"Utilidades Fixas:         {formatar_energia_brasileiro(energia_utilidades, 1):>12} ({formatar_percentual_brasileiro(energia_utilidades/energia_total*100, 1)})")
    print("-" * 55)
    print(f"TOTAL POR LOTE:           {formatar_energia_brasileiro(energia_total, 1):>12}")
    
    # Consumo específico
    massa_produto_final = C.m_cristais_secos  # 80.8 kg
    consumo_especifico = energia_total / massa_produto_final
    print(f"\nConsumo específico:       {formatar_numero_brasileiro(consumo_especifico, 1)} kWh/kg produto")
    
    # ================================================================
    # 6. VERIFICAÇÕES DE CONSISTÊNCIA (VALORES CORRETOS)
    # ================================================================
    print("\n6. VERIFICAÇÕES")
    print("-" * 40)
    
    # Valores esperados com componentes separados
    # Chiller: cada componente calculado separadamente
    Q_sf_sensivel_esperado = 95.6 * 1.6 * 24  # 3,671 kJ
    Q_sf_latente_esperado = 95.6 * 28.9        # 2,763 kJ (valor absoluto)
    Q_biomassa_esperado = 25.52 * 3.5 * 24     # 2,143 kJ
    Q_HCl_esperado = 37.75 * 3.8 * 24          # 3,444 kJ
    Q_etanol_esperado = 75.42 * 1.86 * 21      # 2,944 kJ
    Q_perdas_chiller_esperado = 0.5 * 13 * 3600  # 23,400 kJ
    Q_total_chiller_esperado = (Q_sf_sensivel_esperado + Q_sf_latente_esperado + 
                               Q_biomassa_esperado + Q_HCl_esperado + 
                               Q_etanol_esperado + Q_perdas_chiller_esperado)
    chiller_esperado = Q_total_chiller_esperado / (3.0 * 3600)
    
    # Secador: incluindo etanol
    Q_cristais_esperado = 81.8 * 1.6 * 41      # 5,366 kJ
    Q_agua_esperado = 1.0 * 4.18 * 41 + 1.0 * 2400  # 2,571 kJ
    Q_etanol_sec_esperado = 1.0 * 1.86 * 41 + 1.0 * 850  # 926 kJ
    Q_perdas_sec_esperado = 2.0 * 12 * 3600    # 86,400 kJ
    Q_total_sec_esperado = (Q_cristais_esperado + Q_agua_esperado + 
                           Q_etanol_sec_esperado + Q_perdas_sec_esperado)
    secador_esperado = Q_total_sec_esperado / (0.8 * 3600)
    
    print(f"Chiller calculado: {formatar_energia_brasileiro(resultado_chiller['E_eletrica_total_kWh'], 2)}")
    print(f"Chiller esperado:  {formatar_energia_brasileiro(chiller_esperado, 2)}")
    print(f"Diferença chiller: {formatar_energia_brasileiro(abs(resultado_chiller['E_eletrica_total_kWh'] - chiller_esperado), 2)}")
    
    print(f"Secador calculado: {formatar_energia_brasileiro(resultado_secador['E_eletrica_total_kWh'], 2)}")
    print(f"Secador esperado:  {formatar_energia_brasileiro(secador_esperado, 2)}")
    print(f"Diferença secador: {formatar_energia_brasileiro(abs(resultado_secador['E_eletrica_total_kWh'] - secador_esperado), 2)}")
    
    # Verificar se valores estão na faixa esperada ATUALIZADA
    if 3.0 <= resultado_chiller['E_eletrica_total_kWh'] <= 4.0:
        print("✅ Chiller: Energia na faixa esperada (3-4 kWh)")
    else:
        print("⚠️  Chiller: Energia fora da faixa esperada")
        
    if 30.0 <= resultado_secador['E_eletrica_total_kWh'] <= 35.0:
        print("✅ Secador: Energia na faixa esperada (30-35 kWh)")
    else:
        print("⚠️  Secador: Energia fora da faixa esperada")
        
    # Verificar componentes principais do chiller - FORMATAÇÃO BRASILEIRA
    print(f"\nDetalhamento Chiller:")
    print(f"  SF sensível: {formatar_numero_brasileiro(resultado_chiller['Q_sf_sensivel_kJ'], 0)} kJ (esperado: {formatar_numero_brasileiro(Q_sf_sensivel_esperado, 0)})")
    print(f"  SF latente: {formatar_numero_brasileiro(abs(resultado_chiller['Q_sf_latente_kJ']), 0)} kJ (esperado: {formatar_numero_brasileiro(Q_sf_latente_esperado, 0)})")
    print(f"  Biomassa: {formatar_numero_brasileiro(resultado_chiller['Q_biomassa_inicial_kJ'], 0)} kJ (esperado: {formatar_numero_brasileiro(Q_biomassa_esperado, 0)})")
    print(f"  HCl: {formatar_numero_brasileiro(resultado_chiller['Q_HCl_inicial_kJ'], 0)} kJ (esperado: {formatar_numero_brasileiro(Q_HCl_esperado, 0)})")
    print(f"  Etanol: {formatar_numero_brasileiro(resultado_chiller['Q_etanol_sensivel_kJ'], 0)} kJ (esperado: {formatar_numero_brasileiro(Q_etanol_esperado, 0)})")
    
    print(f"\nDetalhamento Secador:")
    print(f"  Cristais: {formatar_numero_brasileiro(resultado_secador['Q_cristais_sensivel_kJ'], 0)} kJ (esperado: {formatar_numero_brasileiro(Q_cristais_esperado, 0)})")
    print(f"  Água: {formatar_numero_brasileiro(resultado_secador['Q_agua_sensivel_kJ'] + resultado_secador['Q_agua_latente_kJ'], 0)} kJ (esperado: {formatar_numero_brasileiro(Q_agua_esperado, 0)})")
    print(f"  Etanol: {formatar_numero_brasileiro(resultado_secador['Q_etanol_sensivel_kJ'] + resultado_secador['Q_etanol_latente_kJ'], 0)} kJ (esperado: {formatar_numero_brasileiro(Q_etanol_sec_esperado, 0)})")
    
    # ================================================================
    # 7. GERAR VISUALIZAÇÕES COMPLETAS
    # ================================================================
    print("\n" + "="*60)
    print("GERANDO VISUALIZAÇÕES ENERGÉTICAS")
    print("="*60)
    
    try:
        # Gerar todas as visualizações
        viz.gerar_visualizacoes_completas(
            resultado_chiller=resultado_chiller,
            resultado_secador=resultado_secador, 
            equipamentos_atualizados=equipamentos_atualizados,
            energia_total=energia_total,
            consumo_especifico=consumo_especifico,
            utilidades_fixas_total=energia_utilidades
        )
        
        print("\n✅ SUCESSO: Todas as visualizações foram geradas!")
        print("📁 Arquivos criados:")
        print("   🌐 dashboard_energetico.html (dashboard interativo)")
        print("   🖼️  dashboard_energetico.png (imagem estática)")
        print("   🔄 fluxo_energetico_sankey.html (diagrama de fluxo interativo)")
        print("   🖼️  fluxo_energetico_sankey.png (imagem estática)")
        print("   📊 analise_termodinamica.png (análise comparativa)")
        
    except Exception as e:
        print(f"\n❌ ERRO ao gerar visualizações: {e}")
        print("🔧 Verifique se todas as dependências estão instaladas:")
        print("   pip install plotly matplotlib seaborn pandas")
        print("   pip install kaleido  # para salvar imagens")
    
    # ================================================================
    # 8. RETURN COMPLETO DOS RESULTADOS
    # ================================================================
    return {
        'chiller': resultado_chiller,
        'secador': resultado_secador,
        'equipamentos': equipamentos_atualizados,
        'energia_total': energia_total,
        'energia_processo': energia_processo,
        'energia_utilidades': energia_utilidades,
        'consumo_especifico': consumo_especifico,
        'massa_produto': massa_produto_final,
        'verificacoes': {
            'chiller_ok': 3.0 <= resultado_chiller['E_eletrica_total_kWh'] <= 4.0,
            'secador_ok': 30.0 <= resultado_secador['E_eletrica_total_kWh'] <= 35.0
        }
    }

if __name__ == "__main__":
    resultados = main()
    print(f"\n🎯 EXECUÇÃO FINALIZADA COM SUCESSO!")
    print(f"📈 Energia Total: {formatar_energia_brasileiro(resultados['energia_total'], 1)}/lote")
    print(f"⚡ Consumo Específico: {formatar_numero_brasileiro(resultados['consumo_especifico'], 1)} kWh/kg")
    print(f"✅ Verificações: Chiller OK = {resultados['verificacoes']['chiller_ok']}, Secador OK = {resultados['verificacoes']['secador_ok']}")