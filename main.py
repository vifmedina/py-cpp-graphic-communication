import serial # Biblioteca usada para a comunicação via portas seriais
import time # Biblioteca para o uso de delays
import matplotlib.pyplot as plt # Biblioteca para a criação de gráficos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Módulo para integrar bibliotecas (matplotlib e tkinter)
import pandas as pd # Biblioteca usada para a manipulação de dados
import os # Biblioteca para interagir com o sistema operacional
import json # Biblioteca par ler dados em formato json
import tkinter as tk # Biblioteca para a criação de interfaces (botão)

# Configuração da comunicação serial com o arduino (9600)
arduino = serial.Serial('COM9', 9600)
arduino.flush()
time.sleep(2)

# Inicialização do gráfico fora da função enviar_sinal
fig, ax = plt.subplots()  # Criação da figura (fig) e do conjunto de eixos (ax) para a nova janela de gráfico
x_data = []  # Lista para armazenar os valores do eixo x (leituras)
y_data = []  # Lista para armazenar os valores do eixo y (força)

line, = ax.plot([], [], 'r-', label='Valor do Arduino')  # Cria uma linha no gráfico dentro do eixo ax, vermelha e contínua (r-) e define a legenda
ax.set_xlabel('Leituras')  # Define o rótulo do eixo x
ax.set_ylabel('Força')  # Define o rótulo do eixo y
ax.legend()  # exibe a legenda do gráfico

max_x_data = 1000 # Define o valor máximo para x
max_y_data = 1024 # Define o valor máximo para y

# Função para enviar o sinal
def enviar_sinal():
    arduino.write(b'1')

    # Função para salvar o valor de num_forca em um arquivo json
    def salvar_num_forca(num_forca):
        with open('num_forca.json', 'w') as f:
            json.dump({'num_forca': num_forca}, f)

    # Função para carregar o valor de num_forca de um arquivo json
    def carregar_num_forca():
        try:
            with open('num_forca.json', 'r') as f:
                data = json.load(f)
                return data['num_forca']
        except (FileNotFoundError, KeyError):
            return 0

    # Nomeia o arquivo excel
    num_forca = carregar_num_forca()
    excel_file = f'Leitura-De-Força-{num_forca}.xlsx'

    # Função para realizar o salvamento dos dados no excel
    def salvar_no_excel(x_data, y_data, arquivo):
        df = pd.DataFrame({
            'Leitura': x_data,
            'Força': y_data
        })

        if os.path.exists(arquivo):
            with pd.ExcelWriter(arquivo, engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, index=False, header=True)
        else:
            with pd.ExcelWriter(arquivo, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, header=True)

        print("Dados salvos no Excel!")

    # Set de quantas leituras são necessárias para realizar o salvamento da planilha
    intervalo_salvamento = 244
    contador_leituras = 0

    i = 0
    stop_loop = True

    arduino.reset_input_buffer()  # Limpa o buffer da entrada serial
    time.sleep(1)

    # Loop principal
    while stop_loop:
        if arduino.in_waiting >= 2:
            byte1 = arduino.read(1)
            byte2 = arduino.read(1)

            valor = (ord(byte1) << 8) | ord(byte2)

            # Ignora os primeiros dados lidos (caso sejam inválidos)
            if valor < 0 or valor > 1023:
                print(f"Ignorando valor inicial: {valor}")
                continue

            print(f'O valor que está vindo do Arduino é: {valor}')
            
            x_data.append(i)
            y_data.append(valor)
            i += 1

            if len(x_data) > max_x_data:
                x_data.pop(0)
                y_data.pop(0)

            line.set_xdata(x_data)
            line.set_ydata(y_data)

            ax.set_xlim(min(x_data), max(x_data))
            ax.set_ylim(min(y_data) - 10, max(y_data) + 10)

            canvas.draw()

            contador_leituras += 1
            print(f"Contador de leituras: {contador_leituras}")
            
            if contador_leituras >= intervalo_salvamento:
                print("Salvando dados no Excel...")
                salvar_no_excel(x_data, y_data, excel_file)
                contador_leituras = 0
                x_data.clear()
                y_data.clear()
                num_forca += 1
                salvar_num_forca(num_forca)
                stop_loop = False
        else:
            print("Aguardando dados...")
            time.sleep(0.1)
        
        root.update()  # Atualiza a interface

# Função para verificar o sinal do Arduino (quando o botão é pressionado)
def verificar_arduino():
    if arduino.in_waiting > 0:
        comando = arduino.read()
        if comando == b'1':
            enviar_sinal()  # Dispara a função de iniciar medição

# Configura a interface gráfica com um botão
root = tk.Tk()
root.title("Botão para Arduino")

# Frame para conter o gráfico e o botão
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Adiciona o botão
botao = tk.Button(root, text="Iniciar Medição", command=enviar_sinal)
botao.pack(pady=20)

# Adiciona o gráfico ao frame
canvas = FigureCanvasTkAgg(fig, master=frame)  # Cria o canvas do gráfico no frame
canvas.draw()  # Desenha o gráfico
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Exibe o canvas do gráfico no frame

# Loop principal de atualização da interface gráfica
while True:
    verificar_arduino()  # Verifica se o Arduino enviou o sinal para iniciar a medição
    root.update()  # Atualiza a interface do Tkinter
    time.sleep(0.1)  # Atraso para não sobrecarregar o processador
