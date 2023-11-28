import time
import datetime
from datetime import datetime, timedelta
import socket
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager

import os
import re
import requests

import pandas as pd

caminho_projeto = os.path.dirname(os.path.abspath(__file__))
caminho_arquivos = os.path.join(caminho_projeto, 'arquivos')


class Ageo:

    def __init__(self, empresa, portal,senha,usuario):
        if empresa == 'vibra':
            self.c_login = usuario
            self.c_senha = senha

        if portal == 'norte':
            self.url = 'https://portal.unisolution.com.br/CorporateConnect/#/login/86'

        elif portal == 'leste':
            self.url = 'https://portal.unisolution.com.br/CorporateConnect/#/login/535'

        elif portal == 'sul':
            self.url = 'https://portal.unisolution.com.br/CorporateConnect/#/login/228'

        self.qtd_relatorios = 1

        # Obtenha a data atual como um objeto datetime
        data_atual = datetime.now()

        # Formate a data_atual como uma string
        self.data_atual = data_atual.strftime("%d/%m/%Y")

        # Subtrair 1 dia da data_atual para obter previsaoChegada
        previsaoChegada = data_atual - timedelta(days=1)

        # Adicionar 4 dias à data_atual para obter data_ate
        data_ate = data_atual + timedelta(days=4)

        # Agora você pode formatar as datas de acordo com a sua necessidade
        self.previsao_chegada = previsaoChegada.strftime("%d/%m/%Y")
        self.data_ate = data_ate.strftime("%d/%m/%Y")

        # Configurações do navegador
        self.options = webdriver.ChromeOptions()
        #self.options.add_argument("--headless")
        self.options.add_argument('--start-maximized')
        # options.add_argument('--start-fullscreen')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_experimental_option("prefs", {"profile.default_content_setting_values.cookies": 1})
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])

        prefs = {'profile.default_content_setting_values': {'notifications': 0, 'geolocation': 1},
                 "credentials_enable_service": False,
                 "profile.password_manager_enabled": False,
                 "download.default_directory": caminho_arquivos
                 }
        self.options.add_experimental_option('prefs', prefs)

        # Inicia o webdriver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.pid = self.driver.service.process.pid
        print(self.pid)
        self.wait = WebDriverWait(self.driver, 10)

        self.driver.set_window_size(1920, 1080)

        self.driver.get(self.url)

    def quit(self):

        self.driver.quit()

    def login(self):

        wait = WebDriverWait(self.driver, 10)

        # Campo - Login
        wait.until(
            EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Usuário"]'))
        ).send_keys(self.c_login)

        # Campo - Senha
        wait.until(
            EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Senha"]'))
        ).send_keys(self.c_senha)

        #Botão - Login Operador
        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="Login"]'))
        ).click()

        # Validação - Login
        try:
            WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@aria-label="Bem vindo"]'))
            )
            print('logado')
        except:
            WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@aria-label="Erro ao efetuar login"]'))
            )
            raise ValueError('Credenciais de acesso inválida')

    def deletar_arquivos(self):
        for arquivo in os.listdir(caminho_arquivos):
            caminho_arquivo = os.path.join(caminho_arquivos, arquivo)
            os.remove(caminho_arquivo)

    def aguardar_arquivo(self):
        start_time = time.time()

        while True:
            # Verifique se o tempo decorrido atingiu o limite de 60 segundos
            if time.time() - start_time >= 60:
                raise ValueError("Limite de tempo atingido. Não há arquivos XLSX suficientes.")

            # Lista todos os arquivos na pasta
            arquivos_na_pasta = os.listdir(caminho_arquivos)

            # Filtra apenas os arquivos XLSX
            arquivos_xlsx = [arquivo for arquivo in arquivos_na_pasta if arquivo.endswith('.xlsx')]

            # Verifica se há pelo menos 3 arquivos XLSX na pasta
            if len(arquivos_xlsx) >= self.qtd_relatorios:
                print("Todos os arquivos XLSX estão prontos!")
                self.qtd_relatorios += 1
                return True
            else:
                print("Aguardando mais arquivos XLSX...")
                time.sleep(5)  # Aguarde 5 segundos antes de verificar novamente

    def rel_deposito(self):
        wait = WebDriverWait(self.driver, 30)

        # Aba - Storage Solution
        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//span[normalize-space()="Storage Solution"]'))
        ).click()

        # Aba - Saldo
        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//span[normalize-space()="Saldos"]'))
        ).click()

        # Aba - Deposito por Cliente
        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//span[normalize-space()="Depositos por cliente"]'))
        ).click()

        # preencha a data no campo data
        wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="id_92_5_1"]/div/input'))
        ).send_keys(self.data_atual)

        # Botão - Consultar
        wait.until(
            EC.element_to_be_clickable((By.XPATH,'/html/body/app-root/div/div/app-pages/div/div/div/app-consulta/div[1]/div/div/div/form/div[4]/div/button'))
        ).click()

        # Botão -  Exportar Excel
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/app-root/div/div/app-pages/div/div/div/app-consulta/div[2]/div[3]/button'))
        ).click()
        try:
            if self.aguardar_arquivo():
                return True
        except:
            return False

    def rel_agendamento(self):

        wait = WebDriverWait(self.driver, 30)
        # Aba - Consultar Agendamento
        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="link491"]'))
        ).click()

        # Campo - Previsão Chegada
        wait.until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/app-root/div/div/app-pages/div/div/div/app-consulta/div[1]/div/div/div/form/div[1]/app-filtro-periodo-de/div/div/app-data/div/input'))
        ).send_keys(self.previsao_chegada)

        # Campo - até
        wait.until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/app-root/div/div/app-pages/div/div/div/app-consulta/div[1]/div/div/div/form/div[1]/app-filtro-periodo-ate/div/div/app-data/div/input'))
        ).send_keys(self.data_ate)

        # Botão - Consultar
        wait.until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/div/div/app-pages/div/div/div/app-consulta/div[1]/div/div/div/form/div[4]/div/button'))
        ).click()

        print('Valida se tem dados.')

        # Validação - Valida se tem dados para baixar a planilha
        try:
            WebDriverWait(self.driver, 1).until(
                EC.visibility_of_element_located((By.XPATH, '/html[1]/body[1]/div[1]/div[1]/div[1]/div[2]'))
            )
            print('Sem dados para Baixar')
            return False
        except:
            print('Tem dados para Baixar')
            WebDriverWait(self.driver, 120).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/app-root/div/div/app-pages/div/div/div/app-consulta/div[2]/div[3]/button'))
            )

            # Botão -  Exportar Excel
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/app-root/div/div/app-pages/div/div/div/app-consulta/div[2]/div[3]/button'))
            ).click()

            try:
                if self.aguardar_arquivo():
                    return True
            except:
                return False

    def renomear_arquivos(self, nome_relatorio):
        padrao_regex = f"{nome_relatorio}_export_\\d+\\.xlsx"

        # Compila o padrão regex
        regex = re.compile(padrao_regex)

        # Renomeia os arquivos que correspondem ao padrão
        for arquivo in os.listdir(caminho_arquivos):
            print(arquivo)
            if regex.match(arquivo):
                novo_nome = re.sub(r"_export_\d+", "", arquivo)
                os.rename(os.path.join(caminho_arquivos, arquivo), os.path.join(caminho_arquivos, novo_nome))

def status_em_atualizacao():
    try:
        requests.post('http://192.168.1.252:1338/util-api/saldo-ageo/att/')
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Erro na solicitação: {e}")

def status_atualizado():
    try:
        requests.post('http://192.168.1.252:1338/util-api/saldo-ageo/fin/')
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Erro na solicitação: {e}")


def remove_nao_numericos(texto):
    return re.sub(r'[^0-9]', '', str(texto))

def ler_excel_agend():

    caminho_excel = os.path.join(caminho_arquivos, 'Consulta Agendamento.xlsx')

    df = pd.read_excel(caminho_excel)

    df['Litros'] = df['Litros'].apply(remove_nao_numericos).astype(float)

    df = df[df["Situação"] == "Pendente"]

    return df

def ler_excel_dep():

    caminho_excel = os.path.join(caminho_arquivos, 'Depositos por cliente.xlsx')

    df = pd.read_excel(caminho_excel)
    print(df.columns)

    df = df.iloc[:-1]

    df['Liber Lt/CC'] = df['Liber Lt/CC'].apply(remove_nao_numericos).astype(float)
    df['Sem Liber Lt/CC'] = df['Sem Liber Lt/CC'].apply(remove_nao_numericos).astype(float)

    # df = df.groupby(['Cliente', 'Produto'])[[Liber Lt/CC', 'Sem Liber Lt/CC']].sum().reset_index()

    grouped_df = df.groupby(['Cliente', 'Produto'])[['Liber Lt/CC', 'Sem Liber Lt/CC']].sum().reset_index()

    print(grouped_df)

    return df

def atualizar_dep_cliente(terminal, destino, produto, saldo,saldo_provi):
    status_em_atualizacao()
    try:
        url = "http://192.168.1.252:1338/util-api/saldo-ageo/"

        terminal = terminal.upper()

        # Parâmetros da URL-
        params = {
            'regiao': terminal,
            'destino': destino,
            'produto': produto
        }

        # Dados a serem enviados no corpo da solicitação
        data = {
            'saldo': saldo,
            'saldo_provisionado': saldo_provi
        }
        print(f'Atualizando base de saldo - Cliente: {destino} - Produto: {produto} - Saldo Disp. {saldo} Saldo Provi. {saldo_provi}')
        response = requests.post(url, params=params, data=data)

        if response.status_code == 200:
            print(f'Base de saldo - Cliente: {destino} - Atualizada com sucesso')
            return True
        else:
            raise ValueError("Erro na solicitação POST. Código de status:", response.status_code)
    except ValueError as e:
        print(e)
    finally:
        status_atualizado()

def atualizar_agendamento(terminal, destino, produto,saldo ):
    status_em_atualizacao()
    try:
        url = "http://192.168.1.252:1338/util-api/saldo-ageo/sub/"

        terminal = terminal.upper()

        # Parâmetros da URL
        params = {
            'regiao': terminal,
            'destino': destino,
            'produto': produto
        }

        # Dados a serem enviados no corpo da solicitação
        data = {
            'saldo': saldo
        }
        print(f'Atualizando base de saldo - Cliente: {destino} - Produto: {produto} - Saldo a sub.: {saldo}')
        response = requests.post(url, params=params, json=data)

        if response.status_code == 200:
            print(f'Base de saldo - Cliente: {destino} - Atualizada com sucesso')
            return True
        else:
            raise ValueError("Erro na solicitação POST. Código de status:", response.status_code)
    except ValueError as e:
        print(e)
    finally:
        status_atualizado()

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

USER, PASSWORD = ler_arquivo_txt()

def enviar_log_para_api( status, erro):
    # Obter a data e a hora atuais
    data_hora_atual = datetime.now()
    # Formatar a data e a hora no formato desejado
    data_hora_formatada = data_hora_atual.strftime("%Y-%m-%d %H:%M:%S")


    url = "http://192.168.1.252:1338/util-api/log-automacao/"

    nome_da_maquina = socket.gethostname()

    dados = {
        "nome_da_maquina": nome_da_maquina,
        "nome_da_automacao": 'relatório controle saldo AGEO',
        "status": status,
        "erro": erro,
        "vel_download":'0',
        "vel_upload":'0',
        "cpu":'0',
        "memoria":'0',
        "consumo_energetico":'0',
        "hora_homem_minuto": '4',
        "data_do_evento": data_hora_formatada
    }

    response = requests.post(url, json=dados)
    return response.status_code, response.text

def main():
    linha1, linha2 = ler_arquivo_txt()

    portais = ['norte', 'sul', 'leste']
    # portais = ['sul']
    for portal in portais:
        print(portal)
        print(f'Inicio: {datetime.now()}')
        ageo = Ageo(empresa='vibra', portal=portal, senha=PASSWORD, usuario=USER)  # Use a variável portal, não portais
        ageo.login()
        ageo.deletar_arquivos()
        rel_deposito = ageo.rel_deposito()
        rel_agendamento = ageo.rel_agendamento()
        ageo.quit()
        if rel_deposito:
            ageo.renomear_arquivos(nome_relatorio="Depositos por cliente")
            dados_terminal = ler_excel_dep()

            for index, row in dados_terminal.iterrows():
                cliente = row['Cliente']
                produto = row['Produto']
                qtd_disp = row['Liber Lt/CC']
                qtd_disp_provisionado = row['Sem Liber Lt/CC']
                atualizar_dep_cliente(terminal=portal, destino=cliente, produto=produto, saldo=qtd_disp,saldo_provi=qtd_disp_provisionado)

        if rel_agendamento:
            ageo.renomear_arquivos(nome_relatorio="Consulta Agendamento")
            dados_terminal = ler_excel_agend()

            for index, row in dados_terminal.iterrows():
                cliente = row['Cliente']
                produto = row['Produto']
                qtd_disp = row['Litros']
                atualizar_agendamento(terminal=portal, destino=cliente, produto=produto, saldo=qtd_disp)

        resposta = enviar_log_para_api(status='Sucesso', erro='0')
        print(resposta)



        # ler_excel_agend()
        print(f'Fim: {datetime.now()}')




if __name__ == '__main__':

    main()
