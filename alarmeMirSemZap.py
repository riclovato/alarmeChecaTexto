import threading
import time
import pygame
from PIL import ImageGrab
import pytesseract
import tkinter as tk
import sys
import traceback


# Define the coordinates for the top-left and bottom-right corners
top_left_x = 1600
top_left_y = 100
bottom_right_x = 1870
bottom_right_y = 200

# Variável global para controlar o estado do programa
paused = False

# Variável global para controlar se o programa deve parar
stop_program = False

# Specify the target text you want to check for
target_text = "Wooma Temple"

# Variável global para armazenar o status do programa
program_status = "Rodando"  # Inicialmente, o programa está rodando

# Variável global para controlar a contagem regressiva
countdown = 0

# Variável global para armazenar a janela tkinter
root = None
def log_exception(ex):
    with open("error_log.txt", "a") as log_file:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"Timestamp: {timestamp}\n")
        traceback.print_exc(file=log_file)
        log_file.write("\n\n")


def toggle_pause():
    global paused, countdown, program_status
    if paused:
        paused = False
        program_status = "Rodando"
        status_label.config(text=f"Status: {program_status}")
        start_main_logic_thread()  # Inicia a lógica principal do programa quando retoma
    else:
        paused = True
        program_status = f"Pausando em {countdown} segundos"
        status_label.config(text=f"Status: {program_status}")
        start_countdown()

def start_countdown():
    global countdown
    countdown = 5  # Defina o tempo de contagem regressiva em segundos
    update_countdown()

def update_countdown():
    global countdown, paused, program_status
    if countdown > 0 and paused:
        countdown -= 1
        status_label.config(text=f"Status: Pausando em {countdown} segundos")
        root.after(1000, update_countdown)  # Atualiza a contagem a cada 1 segundo
    elif countdown == 0 and paused:
        program_status = "Pausado"
        status_label.config(text=f"Status: {program_status}")

def stop():
    global stop_program
    stop_program = True
    stop_main_logic_thread()  # Pare a lógica principal do programa
    sys.exit()

def main_logic():
    pygame.init()
    alarme = pygame.mixer.Sound("C:/temp/Python/projetoAlarme/alarme/alarmSound.mp3")
    alarm_count = 0
    while not stop_program:
        try:
            if not paused:
                time.sleep(2)
                # Capture a screenshot of the specified region
                screenshot = ImageGrab.grab(bbox=(top_left_x, top_left_y, bottom_right_x, bottom_right_y))
                screenshot.save("screenshot.png")  # Salvar a captura de tela para depuração

                # Perform OCR to extract text from the screenshot
                extracted_text = pytesseract.image_to_string(screenshot)
                print(extracted_text)

                # Check if the target text is present in the extracted text
                if target_text.lower() not in extracted_text.lower():
                    alarm_count += 1
                    time.sleep(1)
                    if alarm_count == 3:
                        alarme.play()
                        time.sleep(20)  # Wait for 18 seconds
                        alarme.stop()
                else:
                    alarm_count = 0
                print(alarm_count)
        except Exception as e:
            print(f"An error occurred: {e}")
            log_exception(e)  # Registra a exceção no arquivo de log
            alarme.play()
            time.sleep(2)  # Wait for 2 seconds if an error occurs
            alarme.stop()

    pygame.quit()

# Função para mostrar a interface gráfica
def show_gui():
    global status_label, root
    root = tk.Tk()
    root.title("Controle do Programa")

    status_label = tk.Label(root, text=f"Status: {program_status}")
    status_label.pack()

    pause_button = tk.Button(root, text="Pausar/Continuar", command=toggle_pause)
    pause_button.pack()

    stop_button = tk.Button(root, text="Parar", command=stop)
    stop_button.pack()

    root.mainloop()

def start_main_logic_thread():
    global run_main_logic
    run_main_logic = True
    main_logic_thread = threading.Thread(target=main_logic)
    main_logic_thread.start()

def stop_main_logic_thread():
    global run_main_logic
    run_main_logic = False

if __name__ == "__main__":
    gui_thread = threading.Thread(target=show_gui)
    gui_thread.start()

    try:
        start_main_logic_thread()  # Inicie a lógica principal do programa
        gui_thread.join()  # Espere pela thread da interface gráfica
    except KeyboardInterrupt:
        pass
    finally:
        stop_program = True
        pygame.quit()
