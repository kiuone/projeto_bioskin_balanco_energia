"""
formatacao_brasileira.py - Funções para formatar números no padrão brasileiro
"""

import locale
import re

def configurar_locale_brasileiro():
    """
    Configura o locale para português brasileiro
    """
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        return True
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
            return True
        except:
            print("⚠️ Não foi possível configurar locale brasileiro. Usando formatação manual.")
            return False

def formatar_numero_brasileiro(numero, decimais=1):
    """
    Formata número no padrão brasileiro: vírgula para decimais, ponto para milhares
    
    Args:
        numero: número a ser formatado
        decimais: quantidade de casas decimais
    
    Returns:
        string formatada no padrão brasileiro
    """
    if isinstance(numero, str):
        return numero
    
    # Formatar com decimais
    if decimais == 0:
        texto = f"{numero:,.0f}"
    else:
        texto = f"{numero:,.{decimais}f}"
    
    # Converter para padrão brasileiro
    # Trocar ponto e vírgula
    texto = texto.replace(',', 'TEMP')  # Temporário
    texto = texto.replace('.', ',')     # Ponto vira vírgula (decimal)
    texto = texto.replace('TEMP', '.')  # Vírgula vira ponto (milhares)
    
    return texto

def formatar_energia_brasileiro(energia_kWh, decimais=1):
    """Formata energia em kWh no padrão brasileiro"""
    return f"{formatar_numero_brasileiro(energia_kWh, decimais)} kWh"

def formatar_potencia_brasileiro(potencia_kW, decimais=2):
    """Formata potência em kW no padrão brasileiro"""
    return f"{formatar_numero_brasileiro(potencia_kW, decimais)} kW"

def formatar_massa_brasileiro(massa_kg, decimais=1):
    """Formata massa em kg no padrão brasileiro"""
    return f"{formatar_numero_brasileiro(massa_kg, decimais)} kg"

def formatar_temperatura_brasileiro(temp_C, decimais=0):
    """Formata temperatura em °C no padrão brasileiro"""
    return f"{formatar_numero_brasileiro(temp_C, decimais)}°C"

def formatar_percentual_brasileiro(percentual, decimais=1):
    """Formata percentual no padrão brasileiro"""
    return f"{formatar_numero_brasileiro(percentual, decimais)}%"

def converter_relatorio_brasileiro(texto_original):
    """
    Converte um relatório inteiro para notação brasileira
    usando regex para encontrar números
    """
    # Padrão para encontrar números com decimais
    padrao = r'\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\b'
    
    def substituir_numero(match):
        numero_str = match.group(1)
        try:
            # Converter para float
            numero = float(numero_str.replace(',', ''))
            # Reformatar para brasileiro
            return formatar_numero_brasileiro(numero, 1)
        except:
            return numero_str
    
    return re.sub(padrao, substituir_numero, texto_original)

# Exemplo de uso
if __name__ == "__main__":
    # Configurar locale se possível
    configurar_locale_brasileiro()
    
    # Testes
    print("=== TESTES DE FORMATAÇÃO BRASILEIRA ===")
    print(f"Energia: {formatar_energia_brasileiro(4369.3)}")
    print(f"Potência: {formatar_potencia_brasileiro(0.27)}")
    print(f"Massa: {formatar_massa_brasileiro(95.6)}")
    print(f"Temperatura: {formatar_temperatura_brasileiro(28)}")
    print(f"Percentual: {formatar_percentual_brasileiro(79.2)}")
    
    # Teste de texto completo
    texto_exemplo = "Energia Total: 4369.3 kWh, Potência: 0.27 kW, Massa: 95.6 kg"
    print(f"\nTexto original: {texto_exemplo}")
    print(f"Texto brasileiro: {converter_relatorio_brasileiro(texto_exemplo)}")