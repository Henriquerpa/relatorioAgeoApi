import os

def ler_arquivo_txt():
    nome_arquivo = "registro.txt"
    try:
        with open(nome_arquivo, 'r') as arquivo:
            linha1 = arquivo.readline().strip()
            linha2 = arquivo.readline().strip()
        return linha1, linha2
    except FileNotFoundError:
        return None  # Arquivo não encontrado
    except Exception as e:
        return None  # Outro erro


linha1,linha2 = ler_arquivo_txt()


