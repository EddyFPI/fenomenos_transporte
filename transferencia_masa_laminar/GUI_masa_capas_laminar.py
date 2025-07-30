from scipy.optimize import fsolve
from scipy.special import erfc
from scipy.linalg import solve_banded
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import customtkinter as ctk
import tkinter as tk
import webbrowser
import pandas as pd
from tkinter import filedialog, messagebox
import math
from PIL import Image
import os
from matplotlib.animation import FuncAnimation

#-----------------------CONFIGURACIÓN PRINCIPAL--------------------------------------
# Configuración inicial de la aplicación
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Creación de la ventana principal
principal = ctk.CTk()
principal.title("SIMULADOR DE TRANSFERENCIA DE MASA")
screen_width = principal.winfo_screenwidth()
screen_height = principal.winfo_screenheight()
principal.geometry(f'{screen_width-10}x{screen_height-85}+0+0')

#--------------------------------ENLACE DE TIC EN DESCRIPCIÓN----------------------------------
#Función para que el usuario pueda acceder al escrito donde se explica lo teórico
def descargar_archivo():
    webbrowser.open("https://epnecuador-my.sharepoint.com/:w:/g/personal/gabriel_quilismal_epn_edu_ec/EUI2f9JKzp5IiKItcUl7PDsBXGa7hB71rnjtgr12lkAqEA?e=XE9lxF")

# Crear el menu
menu = ctk.CTkTabview(master=principal)
menu.pack(padx=10, pady=10, fill="both", expand=True)

# Agregar pestañas
tabs = ["Descripción", "Caso 1", "Caso 2", "Caso 3", "Caso 4"]
for tab in tabs:
    menu.add(tab)

for nombres in tabs:
    frame = menu.tab(nombres)
    content_frame = ctk.CTkFrame(frame)
    content_frame.pack(padx=10, pady=10, fill="both", expand=True)
    
    # Añadir título según la pestaña
    titles = {
        "Descripción": "SIMULADOR DE TRANSFERENCIA DE MASA",
        "Caso 1": "DIFUSIÓN A TRAVÉS DE UNA PELÍCULA DE GAS ESTANCADA",
        "Caso 2": "DIFUSIÓN CON REACCIÓN HETEROGÉNEA",
        "Caso 3": "DIFUSIÓN CON REACCIÓN HOMOGÉNEA",
        "Caso 4": "DIFUSIÓN A UNA PELÍCULA LÍQUIDA DESCENDENTE\n(ABSORCIÓN DE GAS)"
    }
    
    title_label = ctk.CTkLabel(
        content_frame, 
        text=titles[nombres], 
        font=('Times New Roman', 34), 
        anchor='n'
    )
    title_label.pack(fill='x', pady=(20, 5))

    # Contenido específico para cada pestaña
    if nombres == "Descripción":
        desc_text = ctk.CTkLabel(
            content_frame,
            text="El presente simulador resuelve los siguientes casos de Transferencia de Masa:\n\n"
                 "\tCaso 1: Difusión a través de una película de gas estancada.\n\n"
                 "\tCaso 2: Difusión con reacción heterogénea (instantánea y no instantánea).\n\n"
                 "\tCaso 3: Difusión con reacción homogénea.\n\n"
                 "\tCaso 4: Difusión a una película líquida descendente (absorción de gas).",
            font=('Times New Roman', 30), justify="left", anchor="w")
        desc_text.pack(fill='x', pady=(50, 20))
        
        desc_text2 = ctk.CTkLabel(
            content_frame,
            text="Cada caso es desarrollado en estado transitorio y tiene sus propias suposiciones. "
                 "Las ecuaciones gobernantes de cada caso y las demostraciones pertinentes se encuentran en el siguiente archivo descargable.",
            font=('Times New Roman', 30),
            justify="left",
            anchor="w",
            wraplength=principal.winfo_screenwidth() - 150
        )
        desc_text2.pack(fill='x', pady=(20, 20))
        
        link = ctk.CTkLabel(
            content_frame,
            text=" 📄 Descargar documento",
            text_color="blue",
            font=('Times New Roman', 25, 'underline'),
            cursor="hand2"
        )
        link.pack(anchor="w", padx=30)
        link.bind("<Button-1>", lambda e: descargar_archivo())
        
        autor = ctk.CTkLabel(
            content_frame, 
            text="Gabriel Z. Quilismal M.", 
            font=('Times New Roman', 16), 
            anchor='se'
        )
        autor.pack(fill='x', side='bottom')

#-----------------------FUNCIÓN PARA CREAR ETIQUETAS-----------------------------------
# Función para crear campos de entrada con etiquetas
def crear_entry(frame, row, label_text, default_value):
    ctk.CTkLabel(frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
    entry = ctk.CTkEntry(frame)
    entry.grid(row=row, column=1, padx=5, pady=5)
    entry.insert(0, default_value)
    return entry

def format_time(total_seconds):
    if total_seconds is None:
        return "N/A" # Maneja el caso si el tiempo no está disponible

    total_seconds = float(total_seconds) # Asegura que sea un flotante para los cálculos

    # Constantes de conversión
    SECONDS_IN_MINUTE = 60
    SECONDS_IN_HOUR = 3600
    SECONDS_IN_DAY = 86400 # 24 * 3600

    if total_seconds >= SECONDS_IN_DAY:
        days = int(total_seconds // SECONDS_IN_DAY)
        remaining_seconds_after_days = total_seconds % SECONDS_IN_DAY
        
        hours = int(remaining_seconds_after_days // SECONDS_IN_HOUR)
        remaining_seconds_after_hours = remaining_seconds_after_days % SECONDS_IN_HOUR
        
        minutes = int(remaining_seconds_after_hours // SECONDS_IN_MINUTE)
        seconds = remaining_seconds_after_hours % SECONDS_IN_MINUTE
        
        return f"{days} d {hours} h {minutes} m {seconds:.2f} s"
    elif total_seconds >= SECONDS_IN_HOUR:
        hours = int(total_seconds // SECONDS_IN_HOUR)
        remaining_seconds_after_hours = total_seconds % SECONDS_IN_HOUR
        
        minutes = int(remaining_seconds_after_hours // SECONDS_IN_MINUTE)
        seconds = remaining_seconds_after_hours % SECONDS_IN_MINUTE
        
        return f"{hours} h {minutes} m {seconds:.2f} s"
    elif total_seconds >= SECONDS_IN_MINUTE:
        minutes = int(total_seconds // SECONDS_IN_MINUTE)
        seconds = total_seconds % SECONDS_IN_MINUTE
        return f"{minutes} m {seconds:.2f} s"
    else:
        return f"{total_seconds:.2f} s"

#_______________________________________________________________________________________________________________________________________

#----------------------------FUNCIÓN CASO 4-------------------DIFUSIÓN A UNA PELÍCULA LÍQUIDA DESCENDENTE (ABSORCIÓN DE GAS)------------
#_______________________________________________________________________________________________________________________________________

# Configuración específica para Caso 4
frame_c4 = menu.tab("Caso 4")
content_c4 = ctk.CTkFrame(frame_c4)
content_c4.pack(padx=10, pady=5, fill="both", expand=True)

# Frame para las suposiciones
inicio_c4 = ctk.CTkFrame(content_c4)
inicio_c4.pack(padx=10, pady=5, fill="both", expand=True)

#Esquema
esquema_frame_c4 = ctk.CTkFrame(inicio_c4, width=int(principal.winfo_screenwidth()*0.3))
esquema_frame_c4.pack(side = 'right', expand = False, padx = 10, pady = (5,5))

# Obtiene el directorio del script actual
script_dir_c4 = os.path.dirname(os.path.abspath(__file__))
imagen_path_c4 = os.path.join(script_dir_c4, "caso_4.png")

try:
    imagen_pil_c4 = Image.open(imagen_path_c4)

    # Crea una versión CTkImage para modo claro y oscuro (puedes usar la misma imagen PIL)
    esquema_ctk_image_c4 = ctk.CTkImage(light_image=imagen_pil_c4, dark_image=imagen_pil_c4, size = (503,541)) # Ajusta el tamaño

    esquema_label_c4 = ctk.CTkLabel(esquema_frame_c4, image=esquema_ctk_image_c4, text="")
    esquema_label_c4.pack(padx=10, pady=5)

except FileNotFoundError:
    print(f"Error: No se encontró la imagen en la ruta: {imagen_path_c4}")
except Exception as e:
    print(f"Error al cargar la imagen: {e}")

#Suposiciones 
suposiciones_frame_c4 = ctk.CTkFrame(inicio_c4)
suposiciones_frame_c4.pack(fill='both', expand=True, padx=5, pady=5)

# Frame de suposiciones caso 1 
f_caso_4 = ctk.CTkFrame(suposiciones_frame_c4)
f_caso_4.pack(padx=(10,10), pady=10)

sup_caso_4 = ctk.CTkLabel(f_caso_4, 
                        text="Suposiciones para la Difusión a una película líquida descendente (absorción de gas)",
                        font=('Times New Roman', 22),
                        justify="center")
sup_caso_4.pack(pady=(10,10))

desp_caso_4 = ctk.CTkLabel(f_caso_4, 
                            text="Tenemos al absorción de un gas A en un apelícula laminar descendete del líquido B con las siguientes consideraciones:\n\n"
                                "- El gas A es ligeramente soluble en el líquido B lo que no cambia su viscosidad.\n\n"
                                "- Se supone que la difusión en muy lenta en el líquido por lo que A penetra casi nada en B.\n\n"
                                "- Se asume que el flujo molar en z es principalmente por convección y en x por difusión.\n\n"
                                "- Se asume que inicialmente en z=0 solo hay B y que A no puede difundirse más alla del espesor de la pared.\n\n"
                                "- Se asume que x->∞ con lo que x_A en z=δ es 0.",
                            font=('Times New Roman', 18),justify="left")
desp_caso_4.pack(padx=10, pady=10, fill="both", expand=True)

# --- Frame para los controles de la escala de los ejes ---
escala_frame_4 = ctk.CTkFrame(inicio_c4)
escala_frame_4.pack(fill='both', expand=False, padx=20, pady=(10,5))
escala_frame_4.columnconfigure(0, weight=1)
escala_frame_4.columnconfigure(1, weight=1)
escala_frame_4.rowconfigure(0, weight=2)
escala_frame_4.rowconfigure(1, weight=1)

# --- Controles para la Escala del Eje Y ---
escala_y_label_4 = ctk.CTkLabel(escala_frame_4, text="Escala Eje Y:")
escala_y_label_4.grid(row = 0, column = 1, padx=5, pady=(5, 0))

escala_y_opciones_4 = ["Lineal", "Logarítmica"]
escala_y_seleccionada_4 = ctk.StringVar(value="Lineal")
escala_y_menu_4 = ctk.CTkComboBox(escala_frame_4, values=escala_y_opciones_4, variable=escala_y_seleccionada_4)
escala_y_menu_4.grid(row = 1, column = 1, padx=5, pady=(0, 5))

# --- Controles para la Escala del Eje X ---
escala_x_label_4 = ctk.CTkLabel(escala_frame_4, text="Escala Eje X:")
escala_x_label_4.grid(row = 0, column = 0, padx=5, pady=(5, 0))

escala_x_opciones_4 = ["Lineal", "Logarítmica"]
escala_x_seleccionada_4 = ctk.StringVar(value="Lineal")
escala_x_menu_4 = ctk.CTkComboBox(escala_frame_4, values=escala_x_opciones_4, variable=escala_x_seleccionada_4)
escala_x_menu_4.grid(row = 1, column = 0, padx=5, pady=(0, 5))

# Frame de simulación (oculto inicialmente)
simulacion_frame_c4 = ctk.CTkFrame(content_c4)
simulacion_frame_c4.pack_forget()

# Configuración inicial
solver_frame_c4 = ctk.CTkFrame(content_c4)
solver_frame_c4.pack_forget()

def mostrar_solver_c4():
    global entry_D_AB_s4, entry_x_A0_s4, resultados_frame_s4, graf_frame_s4, toolbar_frame_s4, entry_L_s4, entry_vmax_s4, entry_W_s4, entry_c_s4, boton_exportar_s4
    # Ocultar frame de inicio y configurar solver
    inicio_c4.pack_forget()
    solver_frame_c4.pack(fill="both", expand=True, padx=5, pady=10)
    
    # Limpiar frame existente
    for widget in solver_frame_c4.winfo_children():
        widget.destroy()
    
    # Frame de parámetros (30% del ancho)
    izq_frame_s4 = ctk.CTkFrame(solver_frame_c4, width=int(principal.winfo_screenwidth()*0.3))
    izq_frame_s4.pack(side='left', fill='both', padx=2, pady=5)

    # Frame de la gráfica (70% del ancho)
    right_container_s4 = ctk.CTkFrame(solver_frame_c4)
    right_container_s4.pack(side='right', fill='both', expand=True, padx=2, pady=5)

    # ----------------------------
    # Frame del gráfico 
    # ----------------------------
    graf_frame_s4 = ctk.CTkFrame(right_container_s4)
    graf_frame_s4.pack(fill='both', expand=True, padx=2, pady=5)

    # Frame para la barra de herramientas
    toolbar_frame_s4 = ctk.CTkFrame(right_container_s4, height=40)
    toolbar_frame_s4.pack(fill='x', padx=5, pady=(0,5))
      
    # ----------------------------
    # Frame de parámetros (arriba)
    # ----------------------------
    param_frame_s4 = ctk.CTkScrollableFrame(izq_frame_s4)
    param_frame_s4.pack(fill='both', expand=True, padx=2, pady=5)

    resultados_frame_s4 = ctk.CTkFrame(izq_frame_s4)
    resultados_frame_s4.pack(fill='both', padx=5, pady=5, expand=False)  # Cambiado de grid a pack

    # Campos de entrada
    # Campos de entrada para el caso 1
    entry_D_AB_s4 = crear_entry(param_frame_s4, 0, "Coeficiente de difusión (D_AB) [m²/s]:", "2e-9")
    entry_x_A0_s4 = crear_entry(param_frame_s4, 1, "Fracción molar inicial (x_A0):", "0.001")
    entry_c_s4 = crear_entry(param_frame_s4, 2, "Concentración del sistema [mol/L]:", "55.56")
    entry_L_s4 = crear_entry(param_frame_s4, 3, "Longitud en z [m]:", "2.5e-2")
    entry_vmax_s4 = crear_entry(param_frame_s4, 5, "Velocidad máxima [m/s]:", "3e-3")
    entry_W_s4 = crear_entry(param_frame_s4, 4, "Profundidad [m]:", "1.5e-2")

    #SUPOSICIONES ESTACIONARIO
    sup_estacionario_s4 = ctk.CTkFrame(param_frame_s4)
    sup_estacionario_s4.grid(row = 6, columnspan = 2, pady = (10,10))

    delta_S4 = ctk.CTkLabel(sup_estacionario_s4, text = 'Se asume que δ (espesor de la pared) tiende a ∞, por tanto,\n la concentración final c_A será 0.', font=('Times New Roman', 16),
                        justify="center")
    delta_S4.pack( pady=(5,5))
    
    # Botones de control
    button_frame_s4 = ctk.CTkFrame(izq_frame_s4)
    button_frame_s4.pack(fill='x', padx=5, pady=(5, 10), expand=False)  # Cambiado de grid a pack
    
    # Configurar grid para los botones
    button_frame_s4.columnconfigure(0, weight=1)
    button_frame_s4.columnconfigure(1, weight=1)
    button_frame_s4.columnconfigure(2, weight=1)
    button_frame_s4.rowconfigure(0, weight=1)
    button_frame_s4.rowconfigure(1, weight=1)

    boton_simular_s4 = ctk.CTkButton(
        button_frame_s4, 
        text="Simular", 
        command=solver_4, 
        height=40, 
        font=('Arial', 14)
    )
    boton_simular_s4.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

    boton_borrar_s4 = ctk.CTkButton(
        button_frame_s4, 
        text="Borrar", 
        command=limpiar_s4, 
        fg_color="#d9534f", 
        hover_color="#c9302c", 
        height=40, 
        font=('Arial', 14)
    )
    boton_borrar_s4.grid(row=0, column=1, pady=5, padx=5, sticky="nsew")

    boton_volver_s4 = ctk.CTkButton(
        button_frame_s4,
        text="Volver",
        command=volver_inicio_c4,
        fg_color="#6c757d",
        hover_color="#5a6268",
        height=40,
        font=('Arial', 14)
    )
    boton_volver_s4.grid(row=0, column=2, pady=5, padx=5, sticky="nsew")

    boton_exportar_s4 = ctk.CTkButton(
        button_frame_s4,
        text="Exportar Datos",
        command=exportar_s4,
        fg_color="#27ae60",  # Cambiado a verde para mejor identificación
        hover_color="#219653",
        height=40,
        font=('Arial', 14)
    )
    boton_exportar_s4.grid_forget()

def solver_4():
    # Declarar variables globales al inicio de la función
    global x_plot_points, z_plot_points, x_A_matrix_2d 
    
    # Activar el botón de exportar (asumiendo que boton_exportar_s4 es un widget global)
    boton_exportar_s4.grid(row=1, column=1, pady=5, padx=5, sticky="nsew") 

    try:
        D_AB = float(entry_D_AB_s4.get())  # Coeficiente de difusión [m²/s]
        x_A0_surface = float(entry_x_A0_s4.get()) # Fracción molar de A en x=0 (x_A,0)
        c_total = float(entry_c_s4.get())*1000 # Concentración total del sistema (c_total)
        vmax = float(entry_vmax_s4.get())  # Velocidad máxima del flujo [m/s]
        W = float(entry_W_s4.get())      # Ancho de la película [m]
        L = float(entry_L_s4.get())      # Longitud de la película [m]

        cA0_molar = x_A0_surface * c_total

        if D_AB <= 0 or x_A0_surface <= 0 or c_total <= 0 or vmax <= 0 or L <= 0 or W <= 0:
            raise ValueError("Todos los parámetros deben ser positivos y no nulos.")

        # Limpiar frames antes de generar nuevos resultados y gráficos
        for widget in graf_frame_s4.winfo_children():
            widget.destroy()
        for widget in resultados_frame_s4.winfo_children():
            widget.destroy()

        num_points_for_plots = 500 
        
        # Parámetros para el dominio espacial
        diffusion_depth_scale = np.sqrt(D_AB * L / vmax)
        x_max_domain = 5 * diffusion_depth_scale # Dominio de x hasta donde la concentración es despreciable

        # --- Definir los puntos para los ejes y calcular la matriz 2D de concentración x_A(x, z) ---
        x_plot_points = np.linspace(0, x_max_domain, num_points_for_plots)
        z_plot_points = np.linspace(1e-12, L, num_points_for_plots) # Asegurar inicio en un valor pequeño para evitar log(0) o división por cero

        x_A_matrix_2d = np.zeros((num_points_for_plots, num_points_for_plots))

        # Iterar sobre cada punto (x, z) para calcular x_A
        for i, current_x in enumerate(x_plot_points):
            for j, current_z in enumerate(z_plot_points):
                if current_x == 0:
                    # Condición de borde en la interfase x=0
                    x_A_matrix_2d[i, j] = x_A0_surface
                else:
                    # Calcular el denominador para erfc
                    raiz_denominador = np.sqrt(4 * (D_AB / vmax) * current_z)
                    
                    # Evitar división por cero si current_z es muy pequeño y raiz_denominador se hace 0
                    min_val_for_denominator = 1e-15 
                    if raiz_denominador < min_val_for_denominator:
                        raiz_denominador = min_val_for_denominator
                    
                    argumento_erfc = current_x / raiz_denominador
                    x_A_matrix_2d[i, j] = x_A0_surface * erfc(argumento_erfc)

        # --- Cálculo de los Resultados Numéricos (N_Ax, W_A, t_exp) ---
        # Usamos z_plot_points para consistencia
        N_Ax_at_x0_array = cA0_molar * np.sqrt(D_AB * vmax / (np.pi * z_plot_points)) #
        N_Ax_at_x0_initial = N_Ax_at_x0_array[0] 
        
        W_A_total = W * L * cA0_molar * np.sqrt(4 * D_AB * vmax / (np.pi * L)) #
        
        t_exp = L / vmax

        # --- Mostrar resultados en el frame de respuestas ---
        resultado_texto = (
            f"Resultados del cálculo:\n"
            f"1. Densidad de flujo molar en la interfase (N_Ax|x=0): {N_Ax_at_x0_initial:.3e} mol/(m²·s)\n"
            f"2. Flujo molar total (W_A): {W_A_total:.3e} mol/s\n"
            f"3. Tiempo de exposición: {t_exp:.3f} s\n"
        )

        respuestas_label = ctk.CTkLabel(
            resultados_frame_s4,
            text=resultado_texto,
            font=('Consolas', 12),
            justify="left"
        )
        respuestas_label.pack(pady=10)

        # --- GRÁFICOS COMBINADOS EN SUBPLOTS ---
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))
        
        # --- Gráfico 1: Perfiles de fracción molar x_A(x) vs x para diferentes z ---
        num_z_curves = 10 
        z_values_for_x_profiles = np.linspace(1e-12, L, num_z_curves) 

        for z_val in z_values_for_x_profiles:
            raiz_denominador_single_z = np.sqrt(4 * (D_AB / vmax) * z_val)
            min_val_for_denominator = 1e-15
            if raiz_denominador_single_z < min_val_for_denominator:
                raiz_denominador_single_z = min_val_for_denominator
            
            argumento_erfc_single_z = x_plot_points / raiz_denominador_single_z
            x_A_profile = x_A0_surface * erfc(argumento_erfc_single_z)
            
            ax1.plot(x_plot_points, x_A_profile, label=f'z = {z_val:.2f} m') 
        
        if escala_y_seleccionada_4.get() == "Logarítmica":
            ax1.set_yscale('log')
        else:
            ax1.set_yscale('linear')
        
        if escala_x_seleccionada_4.get() == "Logarítmica":
            ax1.set_xscale('log')
        else:
            ax1.set_xscale('linear')
            
        ax1.set_xlabel('Posición x [m]', fontsize=12)
        ax1.set_ylabel('Fracción molar $x_A$', fontsize=12)
        ax1.set_title('Perfiles de $x_A$ vs x (diferentes z)', fontsize=14)
        ax1.grid(True, linestyle='--', alpha=0.6)
        ax1.set_xlim(0, x_max_domain)
        ax1.set_ylim(0, x_A0_surface * 1.05)
        ax1.legend(loc='best', fontsize=10)

        # --- Gráfico 2: Perfiles de fracción molar x_A(z) vs z para diferentes x ---
        num_x_curves = 10 
        x_values_for_z_profiles = np.linspace(0, x_max_domain, num_x_curves) 

        for x_val in x_values_for_z_profiles:
            if x_val == 0:
                x_A_profile_z = np.full_like(z_plot_points, x_A0_surface) 
            else:
                raiz_denominador_single_x = np.sqrt(4 * (D_AB / vmax) * z_plot_points)
                raiz_denominador_single_x = np.where(raiz_denominador_single_x < 1e-15, 1e-15, raiz_denominador_single_x)
                argumento_erfc_single_x = x_val / raiz_denominador_single_x
                x_A_profile_z = x_A0_surface * erfc(argumento_erfc_single_x)
            
            ax2.plot(z_plot_points, x_A_profile_z, label=f'x = {x_val:.2e} m') 
        
        if escala_y_seleccionada_4.get() == "Logarítmica":
            ax2.set_yscale('log')
        else:
            ax2.set_yscale('linear')
        
        if escala_x_seleccionada_4.get() == "Logarítmica": 
            ax2.set_xscale('log')
        else:
            ax2.set_xscale('linear')
            
        ax2.set_xlabel('Posición z [m]', fontsize=12)
        ax2.set_ylabel('Fracción molar $x_A$', fontsize=12)
        ax2.set_title('Perfiles de $x_A$ vs z (diferentes x)', fontsize=14)
        ax2.grid(True, linestyle='--', alpha=0.6)
        ax2.set_xlim(0, L * 1.05)
        ax2.set_ylim(0, x_A0_surface * 1.05)
        ax2.legend(loc='best', fontsize=10)
        
        plt.tight_layout()

        # Crear canvas único para ambos subplots
        canvas = FigureCanvasTkAgg(fig, master=graf_frame_s4)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Toolbar único que funcionará para ambas gráficas
        try:
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame_s4)
            toolbar.update()
            toolbar.pack(side='bottom', fill='x')
        except:
            pass  # Si toolbar_frame_s4 no existe, continuar sin toolbar

    except ValueError as ve:
        messagebox.showerror("Error de Entrada", str(ve))
    except Exception as e:
        messagebox.showerror("Error en simulación", f"Ocurrió un error inesperado: {str(e)}")

def exportar_s4():
    filepath = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Archivos Excel", "*.xlsx"), ("CSV", "*.csv"), ("Todos los archivos", "*.*")],
        title="Guardar datos de fracción molar del Caso 4",
        initialfile="simulación_estado_estacionario_caso_4.xlsx"
    )
    if not filepath:
        return # El usuario canceló la operación

    try:
        df_export = pd.DataFrame(x_A_matrix_2d.T, index=z_plot_points, columns=x_plot_points)
        
        # Opcional: Renombrar el índice para mayor claridad en el archivo
        df_export.index.name = 'Posición z [m]'
        df_export.columns.name = 'Posición x [m]'

        if filepath.endswith('.csv'):
            df_export.to_csv(filepath, index=True) # index=True para incluir la columna 'z'
            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")
        else: # Asume .xlsx
            df_export.to_excel(filepath, index=True, sheet_name='Concentraciones') # index=True para incluir la columna 'z'
            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")

    except Exception as e:
        messagebox.showerror("Error de Exportación", f"No se pudo exportar los datos:\n{str(e)}")

def mostrar_sim_c4():
    global entry_D_AB_c4, entry_tsim_c4, entry_dt_c4, entry_delta_c4, entry_tolerancia_c4, entry_Nx_c4, entry_Nz_c4, entry_L_c4, entry_x_A0_c4, entry_vmax_c4, right_container_c4
    global graf_frame_c4, main_frame_c4, izq_frame_c4, respuestas_frame_c4, param_frame_c4, boton_exportar_c4, tool_c4, boton_reanudar_c4, boton_pausa_c4, entry_x_fijo, entry_z_fijo

    # Ocultar frames de suposiciones y la barra de opciones
    suposiciones_frame_c4.pack_forget()
    inicio_c4.pack_forget()
    botones_inicio_c4.pack_forget()
    
    # Mostrar frame de simulación
    simulacion_frame_c4.pack(fill='both', expand=True, padx=5, pady=0)
    
    # Configurar título dinámico
    for widget in simulacion_frame_c4.winfo_children():
        widget.destroy()
      
    # Main frame para la interfaz de simulación
    main_frame_c4 = ctk.CTkFrame(simulacion_frame_c4)
    main_frame_c4.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Frame de parámetros (30% del ancho)
    izq_frame_c4 = ctk.CTkFrame(main_frame_c4, width=int(principal.winfo_screenwidth()*0.25), height=int(screen_height))
    izq_frame_c4.pack(side='left', fill='y', padx=2, pady=5)
    
    # Frame de la gráfica (70% del ancho)
    right_container_c4 = ctk.CTkFrame(main_frame_c4)
    right_container_c4.pack(side='right', fill='both', expand=True, padx=0, pady=5)

    botones_anim_c4 = ctk.CTkFrame(right_container_c4)  
    botones_anim_c4.pack(fill='both', expand=False, padx=5, pady=(0,0))
    botones_anim_c4.columnconfigure(0, weight=1)
    botones_anim_c4.columnconfigure(1, weight=1)
    
    # Contenedor para gráfica
    graf_frame_c4 = ctk.CTkFrame(right_container_c4)
    graf_frame_c4.pack(fill='both', expand=True, padx=0, pady=5)

    tool_c4 = ctk.CTkFrame(right_container_c4)
    tool_c4.pack(side = 'bottom', fill='x')

    # Controles en izq_frame_c2
    param_frame_c4 = ctk.CTkScrollableFrame(izq_frame_c4)
    param_frame_c4.pack(padx=2, pady=5, fill='both', expand=True)
    
    # Frame para respuestas
    respuestas_frame_c4 = ctk.CTkFrame(izq_frame_c4)
    respuestas_frame_c4.pack(fill='x', padx=2, pady=(5,5))
    
    # Campos de entrada para el caso 1
    entry_D_AB_c4 = crear_entry(param_frame_c4, 0, "Coeficiente de difusión (D_AB) [m²/s]:", "2e-9")
    entry_x_A0_c4 = crear_entry(param_frame_c4, 1, "Fracción molar inicial (x_A0):", "0.001")
    entry_L_c4 = crear_entry(param_frame_c4, 2, "Longitud en z [m]:", "2.5e-2")
    entry_delta_c4 = crear_entry(param_frame_c4, 3, "Espesor de película (δ [m]):", "2.5e-3")
    entry_vmax_c4 = crear_entry(param_frame_c4, 4, "Velocidad máxima [m/s]:", "3e-3")
    entry_Nx_c4 = crear_entry(param_frame_c4, 5, "Número de puntos en x (Nx):", "20")
    entry_Nz_c4 = crear_entry(param_frame_c4, 6, "Número de puntos en z (Nz):", "20")
    entry_tsim_c4 = crear_entry(param_frame_c4, 7, "Tiempo de simulación [s]:", "15")
    entry_dt_c4 = crear_entry(param_frame_c4, 8, "Δt de simulación [s]:", "5e-3")
    entry_tolerancia_c4 = crear_entry(param_frame_c4, 9, "Tolerancia:", "3e-6")
    entry_x_fijo = crear_entry(param_frame_c4, 10, 'Punto (Nz - COLUMNA) que desea fijar:', '2')
    entry_z_fijo = crear_entry(param_frame_c4, 11, 'Punto (Nx - FILA) que desea fijar:', '20')
    
    # Botones de control
    button_frame_c4 = ctk.CTkFrame(izq_frame_c4)
    button_frame_c4.pack(fill='both', expand=True, padx=5, pady=5)
    button_frame_c4.columnconfigure(0, weight=1)
    button_frame_c4.columnconfigure(1, weight=1)
    button_frame_c4.columnconfigure(2, weight=1)
    button_frame_c4.rowconfigure(0, weight=1)
    button_frame_c4.rowconfigure(1, weight=1)

    boton_simular_c4 = ctk.CTkButton(
        button_frame_c4, 
        text="Simular", 
        command=caso_4, 
        height=40, 
        font=('Arial', 14)
    )
    boton_simular_c4.grid(row=0, column=0, pady=2, padx=5)

    boton_borrar_c4 = ctk.CTkButton(
        button_frame_c4, 
        text="Borrar", 
        command=limpiar_c4, 
        fg_color="#d9534f", 
        hover_color="#c9302c", 
        height=40, 
        font=('Arial', 14)
    )
    boton_borrar_c4.grid(row=0, column=1, pady=2, padx=5)

    boton_volver_c4 = ctk.CTkButton(
        button_frame_c4,
        text="Volver",
        command=volver_inicio_c4,
        fg_color="#6c757d",
        hover_color="#5a6268",
        height=40,
        font=('Arial', 14)
    )
    boton_volver_c4.grid(row=0, column=2, pady=2, padx=5)

    boton_exportar_c4 = ctk.CTkButton(
        button_frame_c4,
        text="Exportar Datos",
        command=exportar_c4,
        fg_color="#27ae60",  
        hover_color="#219653",
        height=40,
        font=('Arial', 14)
    )
    boton_exportar_c4.grid_forget()

    boton_pausa_c4 = ctk.CTkButton(
        botones_anim_c4,
        text="⏸️",
        command=lambda: (ani.event_source.stop() if ani else None, anix.event_source.stop() if anix else None),
        fg_color="#000000", 
        hover_color="#000000", 
        height=20, 
        font=('Arial', 20)
    )
    boton_pausa_c4.grid_forget() # O .pack_forget() o similar, dependiendo de cómo los manejes

    boton_reanudar_c4 = ctk.CTkButton(
        botones_anim_c4,
        text="▶️",
        command=lambda: (ani.event_source.start() if ani else None, anix.event_source.start() if anix else None),
        fg_color="#000000",
        hover_color="#000000",
        height=20,
        font=('Arial', 20))
    boton_reanudar_c4.grid_forget()

def volver_inicio_c4():
    # Ocultar frame de simulación
    solver_frame_c4.pack_forget()
    simulacion_frame_c4.pack_forget()
    inicio_c4.pack(padx=10, pady=5, fill="both", expand=True)
    suposiciones_frame_c4.pack(fill='both', expand=True, padx=5, pady=5)
    botones_inicio_c4.pack(fill='both', expand=True, padx=20, pady=20)

def limpiar_c4():
    plt.close('all')

    for widget in graf_frame_c4.winfo_children():
        widget.destroy()
    
    for widget in respuestas_frame_c4.winfo_children():
        widget.destroy()
    
    for widget in tool_c4.winfo_children():
        widget.destroy()
    
    # Limpiar y reiniciar entries
    boton_exportar_c4.grid_forget()
    boton_pausa_c4.grid_forget()
    boton_reanudar_c4.grid_forget()
    entry_D_AB_c4.delete(0, 'end')
    entry_x_A0_c4.delete(0, 'end')
    entry_L_c4.delete(0, 'end')
    entry_Nx_c4.delete(0, 'end')
    entry_Nz_c4.delete(0, 'end')
    entry_tsim_c4.delete(0, 'end')
    entry_dt_c4.delete(0, 'end')
    entry_tolerancia_c4.delete(0, 'end')
    entry_vmax_c4.delete(0, 'end')
    entry_delta_c4.delete(0, 'end')
    
    # Restaurar valores predeterminados
    entry_D_AB_c4.insert(0, "2e-9")
    entry_x_A0_c4.insert(0, "0.001")
    entry_L_c4.insert(0, "2.5e-2")
    entry_Nx_c4.insert(0, "20")
    entry_Nz_c4.insert(0, "20")
    entry_vmax_c4.insert(0, "3e-3")
    entry_delta_c4.insert(0, "2.5e-3")
    entry_tsim_c4.insert(0, "15")
    entry_dt_c4.insert(0, "5e-3")
    entry_tolerancia_c4.insert(0, "3e-6")

def limpiar_s4():
    for widget in graf_frame_s4.winfo_children():
        widget.destroy()
    for widget in toolbar_frame_s4.winfo_children():
        widget.destroy()
    for widget in resultados_frame_s4.winfo_children():
        widget.destroy()
    
    boton_exportar_s4.grid_forget()
    entry_D_AB_s4.delete(0, 'end')
    entry_x_A0_s4.delete(0, 'end')
    entry_L_s4.delete(0, 'end')
    entry_W_s4.delete(0, 'end')
    entry_vmax_s4.delete(0, 'end')
    entry_c_s4.delete(0,'end')
    entry_D_AB_s4.insert(0, "2e-9")
    entry_x_A0_s4.insert(0, "0.001")
    entry_L_s4.insert(0, "2.5e-2")
    entry_W_s4.insert(0, "1.5e-2")
    entry_vmax_s4.insert(0, "3e-3")
    entry_c_s4.insert(0, "55.56")

def exportar_c4():
    try:
        tolerancia = float(entry_tolerancia_c4.get())
    except ValueError:
        messagebox.showerror("Error de Entrada", "La tolerancia debe ser un valor numérico válido.")
        return

    filepath = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Archivos Excel", "*.xlsx"), ("CSV", "*.csv"), ("Todos los archivos", "*.*")],
        title="Guardar datos de simulación del Caso 4",
        initialfile="simulacion_transitorio_caso_4.xlsx" # Nombre de archivo más general
    )
    if not filepath:
        return

    # Calcular diferencias para la hoja de convergencia (una sola vez)
    diffs = []
    convergence_status = []
    for perfil_2d in transitorios: # Diferencia calculada con la matriz 2D completa
        diff = np.mean(np.abs(perfil_2d - x_steady))
        diffs.append(diff)
        if tolerancia is not None:
            convergence_status.append("CONVERGE" if diff <= tolerancia else "NO CONVERGE")
        else:
            convergence_status.append("N/A")

    try:
        if filepath.endswith('.csv'):
            # --- Exportación CSV ---
            # CSV para perfiles x_A(z) en el x_fijo (el que se anima)
            filepath_z_fixed_x_csv = filepath.replace('.csv', '_perfil_z_x_fijo.csv')
            df_csv_z_fixed_x = pd.DataFrame({'z [m]': z, 'Estado Estacionario': x_steady[idx_x_fijo, :]})
            for t_csv, current_x_A_matrix in zip(tiempos, transitorios):
                column_name_csv = f't={t_csv:.2f}s'
                if tiempo_convergencia is not None and abs(t_csv - tiempo_convergencia) < 1e-9:
                    column_name_csv += ' (Convergencia)'
                df_csv_z_fixed_x[column_name_csv] = current_x_A_matrix[idx_x_fijo, :] # Perfil en el x_fijo
            df_csv_z_fixed_x.to_csv(filepath_z_fixed_x_csv, index=False)

            # CSV para perfiles x_A(x) en el z_fijo (el que se anima)
            filepath_x_fixed_z_csv = filepath.replace('.csv', '_perfil_x_z_fijo.csv')
            df_csv_x_fixed_z = pd.DataFrame({'x [m]': x, 'Estado Estacionario': x_steady[:, idx_z_fijo]})
            for t_csv, current_x_A_matrix in zip(tiempos, transitorios):
                column_name_csv = f't={t_csv:.2f}s'
                if tiempo_convergencia is not None and abs(t_csv - tiempo_convergencia) < 1e-9:
                    column_name_csv += ' (Convergencia)'
                df_csv_x_fixed_z[column_name_csv] = current_x_A_matrix[:, idx_z_fijo] # Perfil en el z_fijo
            df_csv_x_fixed_z.to_csv(filepath_x_fixed_z_csv, index=False)
            
            # CSV de convergencia
            convergence_filepath = filepath.replace('.csv', '_convergencia.csv')
            df_convergence = pd.DataFrame({
                'Tiempo [s]': tiempos,
                'Diferencia promedio (Matriz 2D)': diffs,
                'Tolerancia': [tolerancia] * len(tiempos) if tolerancia is not None else ["N/A"] * len(tiempos),
                'Estado': convergence_status
            })
            df_convergence.to_csv(convergence_filepath, index=False)

            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath_z_fixed_x_csv}\n{filepath_x_fixed_z_csv}\ny\n{convergence_filepath}")

        else: # Exportación a Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # --- Hoja: Estado Estacionario (Matriz 2D Completa) ---
                # Crear un DataFrame con 'x' como índice y 'z' como columnas
                df_steady_2d = pd.DataFrame(x_steady, index=x, columns=z)
                df_steady_2d.index.name = 'Posición x [m]/Posición z [m]'
                df_steady_2d.to_excel(writer, sheet_name='Estado Estacionario', index=True)

                # --- Hoja(s) de Transitorios xA(z) en x_fijo ---
                if transitorios:
                    df_trans_z_current_sheet = pd.DataFrame({'z [m]': z})
                    excel_sheet_z_counter = 1
                    for i, (t_excel, current_x_A_matrix) in enumerate(zip(tiempos, transitorios)):
                        column_header_excel = f't={t_excel:.2f}s'
                        if tiempo_convergencia is not None and abs(t_excel - tiempo_convergencia) < 1e-9:
                            column_header_excel += ' (Convergencia)'
                        df_trans_z_current_sheet[column_header_excel] = current_x_A_matrix[idx_x_fijo, :] # Perfil en el x_fijo

                        if (i + 1) % 50 == 0 or (i == len(transitorios) - 1 and len(df_trans_z_current_sheet.columns) > 1):
                            sheet_name = f'Transitorios_xA(z)_Nx{idx_x_fijo}_{excel_sheet_z_counter}'
                            df_trans_z_current_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
                            df_trans_z_current_sheet = pd.DataFrame({'z [m]': z}) # Reiniciar para la siguiente hoja
                            excel_sheet_z_counter += 1

                    if len(df_trans_z_current_sheet.columns) > 1:
                        sheet_name = f'Transitorios_xA(z)_Nx{idx_x_fijo}_{excel_sheet_z_counter}'
                        df_trans_z_current_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

                # --- Hoja(s) de Transitorios xA(x) en z_fijo ---
                if transitorios:
                    df_trans_x_current_sheet = pd.DataFrame({'x [m]': x})
                    excel_sheet_x_counter = 1
                    for i, (t_excel, current_x_A_matrix) in enumerate(zip(tiempos, transitorios)):
                        column_header_excel = f't={t_excel:.2f}s'
                        if tiempo_convergencia is not None and abs(t_excel - tiempo_convergencia) < 1e-9:
                            column_header_excel += ' (Convergencia)'
                        df_trans_x_current_sheet[column_header_excel] = current_x_A_matrix[:, idx_z_fijo] # Perfil en el z_fijo

                        if (i + 1) % 50 == 0 or (i == len(transitorios) - 1 and len(df_trans_x_current_sheet.columns) > 1):
                            sheet_name = f'Transitorios_xA(x)_Nz{idx_z_fijo}_{excel_sheet_x_counter}'
                            df_trans_x_current_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
                            df_trans_x_current_sheet = pd.DataFrame({'x [m]': x}) # Reiniciar para la siguiente hoja
                            excel_sheet_x_counter += 1

                    if len(df_trans_x_current_sheet.columns) > 1:
                        sheet_name = f'Transitorios_xA(x)_Nz{idx_z_fijo}_{excel_sheet_x_counter}'
                        df_trans_x_current_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

                # --- Hoja: Información de Convergencia ---
                df_convergence = pd.DataFrame({
                    'Tiempo [s]': tiempos,
                    'Diferencia promedio (Matriz 2D)': diffs,
                    'Tolerancia': [tolerancia] * len(tiempos) if tolerancia is not None else ["N/A"] * len(tiempos),
                    'Estado': convergence_status
                })

                # Añadir una fila de resumen final
                if tiempo_convergencia is not None:
                    resumen = pd.DataFrame({
                        'Tiempo [s]': ["RESUMEN"],
                        'Diferencia promedio (Matriz 2D)': ["---"],
                        'Tolerancia': [tolerancia if tolerancia is not None else "N/A"],
                        'Estado': [f"Convergencia alcanzada en t={tiempo_convergencia:.2f}s"]
                    })
                else:
                    resumen = pd.DataFrame({
                        'Tiempo [s]': ["RESUMEN"],
                        'Diferencia promedio (Matriz 2D)': ["---"],
                        'Tolerancia': [tolerancia if tolerancia is not None else "N/A"],
                        'Estado': ["No se alcanzó convergencia"]
                    })
                
                df_convergence = pd.concat([df_convergence, resumen], ignore_index=True)
                df_convergence.to_excel(writer, sheet_name='Convergencia', index=False)

            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar los datos:\n{str(e)}")

def caso_4():
    global transitorios, tiempos, x_steady, z, tiempo_convergencia, ani, anix, x, idx_x_fijo, idx_z_fijo, Nx, Nz
    
    # Limpiar widgets anteriores en los frames para evitar duplicados
    for widget in respuestas_frame_c4.winfo_children():
        widget.destroy()
    for widget in graf_frame_c4.winfo_children():
        widget.destroy()

    boton_exportar_c4.grid(row=1, column=1, pady=5, padx=5) 
    boton_pausa_c4.grid(row=0, column=0, padx=5, pady=0)
    boton_reanudar_c4.grid(row=0, column=1, padx=5, pady=0)

    try:
        # --- 1. PARÁMETROS DE ENTRADA ---
        D_AB = float(entry_D_AB_c4.get())     # Coeficiente de difusión [m²/s]
        v_max = float(entry_vmax_c4.get())   # Velocidad constante [m/s]
        delta = float(entry_delta_c4.get())   # Espesor de la película [m]
        x_A0 = float(entry_x_A0_c4.get())    # Concentración en interfase [mol/m³]
        L = float(entry_L_c4.get())           # Longitud en z [m]
        Nx = int(entry_Nx_c4.get())         
        Nz = int(entry_Nz_c4.get())           
        tsim = float(entry_tsim_c4.get())
        dt_us = float(entry_dt_c4.get())
        tolerancia = float(entry_tolerancia_c4.get())
        x_fijo = int(entry_x_fijo.get())
        z_fijo = int(entry_z_fijo.get())

        # Validaciones de entrada
        if Nx < 2 or Nz < 2:
            raise ValueError("Nx y Nz deben ser ≥ 2")
        if tsim <= 0 or tolerancia <= 0:
            raise ValueError("El tiempo de simulación y la tolerancia deben ser > 0")
        if Nx > 100 or Nz > 100:
            messagebox.showwarning("Advertencia", "Nx o Nz muy grandes puede afectar el rendimiento")
        if v_max <= 0:
            raise ValueError("La velocidad máxima (v_max) debe ser mayor que 0")
        if delta <= 0:
            raise ValueError("El espesor de la película (delta) debe ser mayor que 0")
        if D_AB <= 0:
            raise ValueError("El coeficiente de difusión (D_AB) debe ser mayor que 0")
        if x_fijo < 1 or x_fijo > Nx:
            raise ValueError(f"x_fijo debe estar entre 1 y {Nx}")
        if z_fijo < 1 or z_fijo > Nz:
            raise ValueError(f"z_fijo debe estar entre 1 y {Nz}")

        # --- 2. DISCRETIZACIÓN ESPACIAL ---
        dx = delta / (Nx - 1)
        dz = L / (Nz - 1)
        x = np.linspace(0, delta, Nx)
        z = np.linspace(0, L, Nz)

        def sol_estado_estacionario(x_A_steady_flat):
 
            num_x_internal = Nx - 2
            num_z_incognitas = Nz - 1 
           
            x_A_internal = x_A_steady_flat.reshape((num_x_internal, num_z_incognitas))
            x_A_full = np.zeros((Nx, Nz))

            # CONDICIONES DE FRONTERA MODIFICADAS:
            # CL1: z=0, x_A = 0 (entrada limpia)
            x_A_full[:, 0] = 0
            x_A_full[0, 0] = x_A0  # Excepción en (0,0)

            # CL2: x=0, x_A = x_A0 (pared con concentración constante)
            x_A_full[0, :] = x_A0

            # Llenar puntos internos
            x_A_full[1:Nx-1, 1:Nz] = x_A_internal

            # CL3 MODIFICADA: x=δ, x_A = 0 (concentración cero en el infinito)
            # Esto simula que x→∞ y la concentración tiende a 0
            x_A_full[Nx-1, :] = 0

            F = np.zeros((num_x_internal, num_z_incognitas))

            # Resolver ecuación con velocidad constante
            for i_int in range(num_x_internal):
                i_full = i_int + 1  
                # Velocidad constante (ya no depende de x)
                v_convect = v_max

                for j_int in range(num_z_incognitas):
                    j_full = j_int + 1  

                    # Término de difusión en x
                    diff_term = D_AB * (x_A_full[i_full+1, j_full] - 2*x_A_full[i_full, j_full] + x_A_full[i_full-1, j_full]) / dx**2
                    
                    # Término de convección en z (velocidad constante)
                    conv_term = v_convect * (x_A_full[i_full, j_full] - x_A_full[i_full, j_full-1]) / dz

                    # Ecuación de estado estacionario: convección = difusión
                    F[i_int, j_int] = conv_term - diff_term

            return F.flatten()
        
        # Estimación inicial modificada para velocidad constante
        x_initial_guess_steady = np.zeros((Nx - 2, Nz-1))
        for i_int in range(Nx - 2):
            i_full = i_int + 1
            for j_int in range(Nz-1):
                j_full = j_int + 1 
                # Decaimiento exponencial desde la pared hacia el infinito
                # Con velocidad constante, el perfil será más lineal en x
                factor_x = x_A0 * np.exp(-x[i_full] / delta)  # Decaimiento exponencial en x
                factor_z = (1 - np.exp(-z[j_full] / L))       # Crecimiento en z
                x_initial_guess_steady[i_int, j_int] = factor_x * factor_z

        # Resolver el sistema no lineal
        x_A_steady_solucion = fsolve(sol_estado_estacionario, x_initial_guess_steady.flatten(), xtol=1e-10)
        
        # Reconstruir la solución completa
        x_steady = np.zeros((Nx, Nz))
        x_steady[1:Nx-1, 1:Nz] = x_A_steady_solucion.reshape((Nx - 2, Nz - 1))

        # Aplicar las condiciones de frontera MODIFICADAS
        x_steady[:, 0] = 0                # CL1: z=0, x_A = 0 
        x_steady[0, :] = x_A0             # CL2: x=0, x_A = x_A0
        x_steady[Nx-1, :] = 0             # CL3 MODIFICADA: x=δ, x_A = 0 (simula x→∞)
        
        # --- 4. ESTADO TRANSITORIO CON CRANK-NICOLSON + UPWIND ---
        
        # Criterio de estabilidad (velocidad constante)
        dt_conv = dz / v_max if v_max > 0 else np.inf
        dt_diff = 0.5 * dx**2 / D_AB if D_AB > 0 else np.inf
        dt_max = min(dt_conv, dt_diff)
        dt_sim = 0.9 * dt_max

        if dt_us <= dt_sim:
            dt = dt_us
        else:
            messagebox.showinfo("Advertencia", 
                f"Para estabilidad tu Δt = {dt_us:.1e} s es mayor que el Δt_max = {dt_sim:.1e} s. Se usará Δt = {dt_sim:.1e} s.")
            dt = dt_sim

        iteraciones = math.ceil(tsim / dt)

        # Inicialización con condiciones de frontera modificadas
        x_A = np.zeros((Nx, Nz))
        x_A[:, 0] = 0               # CL1: z=0, x_A = 0
        x_A[0, :] = x_A0            # CL2: x=0, x_A = x_A0
        x_A[Nx-1, :] = 0            # CL3 MODIFICADA: x=δ, x_A = 0

        transitorios = []
        tiempos = []
        tiempo_convergencia = None
        perfil_convergido = None 
        diff_promedio = np.inf 

        # Parámetros para Crank-Nicolson
        alpha = D_AB * dt / (2 * dx**2)  # Parámetro de difusión para CN
        beta = dt / (2 * dz)             # Parámetro de convección

        for n in range(iteraciones):
            x_old = x_A.copy()
            x_new = x_A.copy()
            
            # Resolver para cada fila z (j) usando Crank-Nicolson en x y upwind en z
            for j in range(1, Nz):
                # Construir sistema tridiagonal para cada fila j
                
                # Matrices del sistema tridiagonal
                a = np.zeros(Nx-2)  # diagonal inferior
                b = np.zeros(Nx-2)  # diagonal principal
                c = np.zeros(Nx-2)  # diagonal superior
                d = np.zeros(Nx-2)  # término independiente
                
                for i in range(1, Nx-1):
                    i_sys = i - 1  # índice en el sistema (0 a Nx-3)
                    
                    # Velocidad constante (ya no depende de x)
                    v_i = v_max
                    
                    # Término convectivo (upwind explícito)
                    conv_term = v_i * (x_old[i, j] - x_old[i, j-1]) / dz
                    
                    # Coeficientes del sistema tridiagonal para Crank-Nicolson
                    if i > 1:  # no es el primer punto interno
                        a[i_sys] = -alpha
                    
                    b[i_sys] = 1 + 2*alpha  # diagonal principal
                    
                    if i < Nx-2:  # no es el último punto interno
                        c[i_sys] = -alpha
                    
                    # Término independiente (lado derecho)
                    diff_explicit = alpha * (x_old[i+1, j] - 2*x_old[i, j] + x_old[i-1, j])
                    d[i_sys] = x_old[i, j] + diff_explicit - dt * conv_term
                
                # Aplicar condiciones de frontera en el sistema
                d[0] += alpha * x_A0  # Contribución del borde izquierdo (x=0)
                
                # CONDICIÓN DE FRONTERA DERECHA MODIFICADA
                # En lugar de ∂x_A/∂x = 0, ahora x_A = 0 en x=δ
                if len(d) > 0:
                    d[-1] += alpha * 0  # Contribución del borde derecho (x_A = 0)
                
                # Resolver sistema tridiagonal
                if len(d) > 0 and np.all(np.abs(b) > 1e-12):
                    x_solution = solve_tridiagonal(a, b, c, d)
                    x_new[1:Nx-1, j] = x_solution
            
            x_A = x_new
            
            # Aplicar condiciones de frontera MODIFICADAS
            x_A[:, 0] = 0                # CL1: z=0, x_A = 0
            x_A[0, :] = x_A0             # CL2: x=0, x_A = x_A0
            x_A[Nx-1, :] = 0             # CL3 MODIFICADA: x=δ, x_A = 0 (simula x→∞)
            
            # Almacenar resultados para animación
            if n % max(1, iteraciones // 50) == 0 or n == 0:
                transitorios.append(x_A.copy()) 
                tiempos.append(n * dt)

            # Verificar convergencia
            if x_steady is not None:
                diff_promedio = np.mean(np.abs(x_A - x_steady)) 
                if diff_promedio <= tolerancia and tiempo_convergencia is None:
                    tiempo_convergencia = n * dt
                    perfil_convergido = x_A.copy()
                    if n % max(1, iteraciones // 50) != 0 and n != 0:
                        transitorios.append(x_A.copy())
                        tiempos.append(n * dt)
                    
        perfil_final = perfil_convergido if perfil_convergido is not None else x_A.copy()
        idx_x_fijo = x_fijo - 1
        x_fijo_valor = x[idx_x_fijo]
        idx_z_fijo = z_fijo - 1
        z_fijo_valor = z[idx_z_fijo] 
       
        # Mostrar resultados
        if tiempo_convergencia is not None:
            resultado_texto = (
                f"Iteraciones realizadas: {iteraciones}\n"
                f"Modelo: Velocidad constante v(x) = {v_max} m/s, x→∞ (x_A→0)\n"
                f"Convergencia alcanzada en la iteración {tiempo_convergencia/dt:.0f}\n"
                f"Tiempo de convergencia: {tiempo_convergencia:.3f} s\n"
                f"Diferencia entre estado estacionario y transitorio: {diff_promedio:.3e}\n"
                f"Tiempo simulado total: {tsim:.3f} s\n"
                f"Paso temporal (Δt): {dt:.3e} s\n"
                f"----------------------------------------------------\n"
                f"\t\tConcentraciones Finales:\n"
                f"  Fracción de A en z = {z_fijo_valor:.3f} [m]: {x_steady[idx_x_fijo, Nz-1]:.5f}\n"
                f"  Fracción de A en x = {x_fijo_valor:.3f} [m]: {x_steady[idx_x_fijo, idx_z_fijo]:.5f}\n"
            )
        else:
            if diff_promedio == np.inf and x_steady is not None:
                diff_promedio = np.mean(np.abs(x_A - x_steady))
            resultado_texto = (
                f"Iteraciones realizadas: {iteraciones}\n"
                f"Modelo: Velocidad constante v(x) = {v_max} m/s, x→∞ (x_A→0)\n"
                f"El sistema NO CONVERGIÓ con {iteraciones} iteraciones\n"
                f"a una tolerancia de {tolerancia}\n"
                f"Diferencia entre estado estacionario y transitorio: {diff_promedio:.2e}\n"
                f"Tiempo simulado total: {iteraciones*dt:.2f} s\n"
                f"Paso temporal (Δt): {dt:.1e} s\n"
                f"----------------------------------------------------\n"
                f"\t\tConcentraciones Finales:\n"
                f"  Fracción de A en z = {z_fijo_valor:.3f} [m]: {x_steady[idx_x_fijo, Nz-1]:.5f}\n"
                f"  Fracción de A en x = {x_fijo_valor:.3f} [m]: {x_steady[idx_x_fijo, idx_z_fijo]:.5f}\n"
            )

        # Crear label para mostrar resultados
        respuestas_label = ctk.CTkLabel(
            master=respuestas_frame_c4,
            text=resultado_texto,
            font=('Consolas', 12),
            justify="left"
        )
        respuestas_label.pack(pady=10)

        # Crear gráficas
        crear_graficas_animacion(x, z, transitorios, tiempos, x_steady, perfil_final, 
                                 idx_x_fijo, idx_z_fijo, x_fijo_valor, z_fijo_valor, 
                                 tiempo_convergencia, delta, L, x_A0)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error en simulación:\n{str(e)}")

def solve_tridiagonal(a, b, c, d):
    """
    Resuelve un sistema tridiagonal Ax = d usando el algoritmo de Thomas
    a: diagonal inferior
    b: diagonal principal
    c: diagonal superior
    d: vector del lado derecho
    """
    n = len(d)
    if n == 0:
        return np.array([])
    
    # Forward elimination
    for i in range(1, n):
        if abs(b[i-1]) < 1e-14:
            raise ValueError("División por cero en solve_tridiagonal")
        w = a[i-1] / b[i-1]
        b[i] = b[i] - w * c[i-1] if i-1 < len(c) else b[i]
        d[i] = d[i] - w * d[i-1]
    
    # Back substitution
    x = np.zeros(n)
    if abs(b[n-1]) < 1e-14:
        raise ValueError("División por cero en solve_tridiagonal")
    x[n-1] = d[n-1] / b[n-1]
    
    for i in range(n-2, -1, -1):
        if abs(b[i]) < 1e-14:
            raise ValueError("División por cero en solve_tridiagonal")
        x[i] = (d[i] - c[i] * x[i+1]) / b[i] if i < len(c) else d[i] / b[i]
    
    return x

def crear_graficas_animacion(x, z, transitorios, tiempos, x_steady, perfil_final, 
                           idx_x_fijo, idx_z_fijo, x_fijo_valor, z_fijo_valor, 
                           tiempo_convergencia, delta, L, x_A0):
    """Función separada para crear las gráficas y animaciones"""
    
    # Verificar que tenemos datos válidos
    if not transitorios or len(transitorios) == 0:
        messagebox.showerror("Error", "No hay datos de transitorios para graficar")
        return
    
    try:
        # Crear figura con dos subgráficas lado a lado
        fig, (ax_z, ax_x) = plt.subplots(1, 2, figsize=(13, 6))

        # Configurar escalas (asumiendo que estas variables existen globalmente)
        try:
            escala_y = escala_y_seleccionada_4.get()
            escala_x = escala_x_seleccionada_4.get()
        except:
            escala_y = "Lineal"
            escala_x = "Lineal"

        # --- GRÁFICA 1: ANIMACIÓN (x_A vs Z en un X fijo) ---
        if escala_y == "Logarítmica":
            ax_z.set_yscale('log')
        else:
            ax_z.set_yscale('linear')

        if escala_x == "Logarítmica":
            ax_z.set_xscale('log')
        else:
            ax_z.set_xscale('linear')

        # Líneas para animación en Z
        lines_z = []
        for _ in range(len(transitorios)):
            line_z, = ax_z.plot([], [], '--', alpha=0.6)
            lines_z.append(line_z)

        # Perfil de estado estacionario en Z
        steady_profile_at_x_fijo = x_steady[idx_x_fijo, :]
        steady_line_z, = ax_z.plot(z, steady_profile_at_x_fijo, 'r-', linewidth=2.5, label='Estado estacionario')

        # Perfil convergido en Z
        perfil_convergido_at_x_fijo = perfil_final[idx_x_fijo, :]
        if tiempo_convergencia is not None:
            label_convergencia_z = f'Converge a t = {tiempo_convergencia:.2f} s'
        else:
            label_convergencia_z = 'Final (no converge)'
        convergido_line_z, = ax_z.plot(z, perfil_convergido_at_x_fijo, 'b:', linewidth=4, label=label_convergencia_z)

        # Texto para mostrar tiempo en Z
        time_text_z = ax_z.text(0.02, 0.95, '', transform=ax_z.transAxes, fontsize=10, verticalalignment='top')

        # Configurar ejes Z
        ax_z.set_xlabel('Posición z [m]', fontsize=12)
        ax_z.set_ylabel('Fracción molar $x_A$', fontsize=12)
        ax_z.set_title(f'$x_A$(z) en x = {x_fijo_valor:.3f} m', fontsize=12)
        ax_z.legend(loc='upper right', fontsize=9, framealpha=0.95)
        ax_z.grid(True, linestyle='--', alpha=0.6)
        ax_z.set_xlim(0, L * 1.05)

        # Configurar límites Y para gráfica Z
        all_data_at_x_fijo = [trans[idx_x_fijo, :] for trans in transitorios] + [steady_profile_at_x_fijo]
        min_y_data_z = np.min([np.min(d[d > 0]) if np.any(d > 0) else 1e-9 for d in all_data_at_x_fijo])
        max_y_data_z = np.max([np.max(d) for d in all_data_at_x_fijo])

        if escala_y == "Logarítmica":
            ax_z.set_ylim(max(1e-9, min_y_data_z * 0.9), max_y_data_z * 1.1)
        else:
            ax_z.set_ylim(0, max(x_A0 * 1.1, max_y_data_z * 1.1))

        # --- GRÁFICA 2: ANIMACIÓN (x_A vs X en un Z fijo) ---
        if escala_y == "Logarítmica":
            ax_x.set_yscale('log')
        else:
            ax_x.set_yscale('linear')

        if escala_x == "Logarítmica":
            ax_x.set_xscale('log')
        else:
            ax_x.set_xscale('linear')

        # Líneas para animación en X
        lines_x = []
        for _ in range(len(transitorios)):
            line_x, = ax_x.plot([], [], '--', alpha=0.6)
            lines_x.append(line_x)

        # Perfil de estado estacionario en X
        steady_profile_at_z_fijo = x_steady[:, idx_z_fijo]
        steady_line_x, = ax_x.plot(x, steady_profile_at_z_fijo, 'r-', linewidth=2.5, label='Estado estacionario')

        # Perfil convergido en X
        perfil_convergido_at_z_fijo = perfil_final[:, idx_z_fijo]
        if tiempo_convergencia is not None:
            label_convergencia_x = f'Converge a t = {tiempo_convergencia:.2f} s'
        else:
            label_convergencia_x = 'Final (no converge)'
        convergido_line_x, = ax_x.plot(x, perfil_convergido_at_z_fijo, 'b:', linewidth=4, label=label_convergencia_x)

        # Texto para mostrar tiempo en X
        time_text_x = ax_x.text(0.02, 0.95, '', transform=ax_x.transAxes, fontsize=10, verticalalignment='top')

        # Configurar ejes X
        ax_x.set_xlabel('Posición x [m]', fontsize=12)
        ax_x.set_ylabel('Fracción molar $x_A$', fontsize=12)
        ax_x.set_title(f'$x_A$(x) en z = {z_fijo_valor:.3f} m', fontsize=12)
        ax_x.legend(loc='upper right', fontsize=9, framealpha=0.95)
        ax_x.grid(True, linestyle='--', alpha=0.6)
        ax_x.set_xlim(0, delta * 1.05)

        # Configurar límites Y para gráfica X
        all_data_at_z_fijo = [trans[:, idx_z_fijo] for trans in transitorios] + [steady_profile_at_z_fijo]
        min_y_data_x = np.min([np.min(d[d > 0]) if np.any(d > 0) else 1e-9 for d in all_data_at_z_fijo])
        max_y_data_x = np.max([np.max(d) for d in all_data_at_z_fijo])

        if escala_y == "Logarítmica":
            ax_x.set_ylim(max(1e-9, min_y_data_x * 0.9), max_y_data_x * 1.1)
        else:
            ax_x.set_ylim(0, max(x_A0 * 1.1, max_y_data_x * 1.1))

        # Función de animación para ambas gráficas
        def animate_both(i):
            if i < len(transitorios):
                # Actualizar gráfica Z
                lines_z[i].set_data(z, transitorios[i][idx_x_fijo, :])
                time_text_z.set_text(f'Tiempo t = {tiempos[i]:.2f} s')
                
                # Actualizar gráfica X
                lines_x[i].set_data(x, transitorios[i][:, idx_z_fijo])
                time_text_x.set_text(f'Tiempo t = {tiempos[i]:.2f} s')
                
            return (*lines_z[:i+1], *lines_x[:i+1], time_text_z, time_text_x)

        # Crear animación
        global ani
        ani = FuncAnimation(fig, animate_both, frames=len(transitorios), interval=200, blit=True, repeat=True)

        # Ajustar layout
        plt.tight_layout()

        # Integrar en la interfaz
        canvas = FigureCanvasTkAgg(fig, master=graf_frame_c4)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Toolbar
        try:
            toolbar = NavigationToolbar2Tk(canvas, tool_c4)
            toolbar.update()
            toolbar.pack(side='left')
        except:
            pass  # Si tool_c4 no existe, continuar sin toolbar

        # Botón para abrir gráfica 3D
        def abrir_grafica_3d():
            crear_ventana_3d(transitorios, tiempos, x, z, x_steady, delta, L, x_A0)
            
        boton_3d = ctk.CTkButton(
            master=respuestas_frame_c4,
            text="Abrir Visualización 3D",
            command=abrir_grafica_3d,
            font=('Arial', 12, 'bold'),
            fg_color="#2E8B57",
            hover_color="#228B22"
        )
        boton_3d.pack(pady=10)
        
    except Exception as e:
        messagebox.showerror("Error en gráficas", f"Error al crear las gráficas:\n{str(e)}")

def crear_ventana_3d(transitorios, tiempos, x, z, x_steady, delta, L, x_A0):
    
    try:
        # Crear ventana independiente
        ventana_3d = tk.Toplevel()
        ventana_3d.title("Visualización 3D - Difusión a una película de líquido descendente")
        ventana_3d.geometry("1000x800")
        ventana_3d.configure(bg='#2E2E2E')
        
        # Frame para controles
        controles_frame = tk.Frame(ventana_3d, bg='#2E2E2E')
        controles_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Variables para controles
        pausado = tk.BooleanVar(value=False)
        mostrar_steady = tk.BooleanVar(value=True)
        
        # Botones de control
        def toggle_pausa():
            pausado.set(not pausado.get())
            btn_pausa.config(text="Reanudar" if pausado.get() else "Pausar")
        
        btn_pausa = tk.Button(controles_frame, text="Pausar", command=toggle_pausa, 
                             font=('Arial', 10), bg='#4CAF50', fg='white')
        btn_pausa.pack(side=tk.LEFT, padx=5)
        
        
        # Checkbox para mostrar estado estacionario
        check_steady = tk.Checkbutton(controles_frame, text="Mostrar Estado Estacionario", 
                                     variable=mostrar_steady, bg='#2E2E2E', fg='white', 
                                     font=('Arial', 10), selectcolor='#2E2E2E')
        check_steady.pack(side=tk.LEFT, padx=10)
        
        # Crear figura 3D
        fig = plt.figure(figsize=(12, 9))
        fig.patch.set_facecolor('#2E2E2E')
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor('#1E1E1E')
        
        # Crear mallas para la superficie
        X, Z = np.meshgrid(x, z, indexing='ij')
        
        # Variable para el índice actual de la animación
        frame_actual = [0]
        
        def animate_3d(frame):
            if pausado.get():
                return
                
            # Limpiar y reconfigurar
            ax.clear()
            ax.set_facecolor('#1E1E1E')
            
            # Superficie transitoria
            surf_new = ax.plot_surface(X, Z, transitorios[frame_actual[0]], 
                                      cmap='plasma', alpha=0.8, linewidth=0, antialiased=True)
            
            # Superficie de estado estacionario (si está habilitada)
            if mostrar_steady.get():
                ax.plot_surface(X, Z, x_steady, cmap='coolwarm', 
                               alpha=0.3, linewidth=0, antialiased=True)
            
            # Configuración de ejes
            ax.set_xlabel('Posición x [m]', fontsize=12, color='white')
            ax.set_ylabel('Posición z [m]', fontsize=12, color='white')
            ax.set_zlabel('Fracción molar x_A', fontsize=12, color='white')
            ax.set_title('Difusión a una película de líquido descendente 3D', fontsize=14, color='white', pad=20)
            ax.set_xlim(0, delta)
            ax.set_ylim(0, L)
            ax.set_zlim(0, x_A0 * 1.1)
            
            # Personalizar apariencia
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.zaxis.label.set_color('white')
            ax.tick_params(colors='white')
            
            # Texto de tiempo
            ax.text2D(0.02, 0.95, f'Tiempo: {tiempos[frame_actual[0]]:.2f} s', 
                     transform=ax.transAxes, fontsize=12, color='white', weight='bold',
                     bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
            
            # Incrementar frame
            frame_actual[0] = (frame_actual[0] + 1) % len(transitorios)
        
        # Crear animación
        ani_3d = FuncAnimation(fig, animate_3d, frames=len(transitorios), 
                              interval=200, blit=False, repeat=True)
        
        # Integrar en la ventana
        canvas_3d = FigureCanvasTkAgg(fig, master=ventana_3d)
        canvas_3d.draw()
        canvas_3d.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
       
    except Exception as e:
        messagebox.showerror("Error 3D", f"Error en simulación:\n{str(e)}")
                             
# Frame para botones de opciones
botones_inicio_c4 = ctk.CTkFrame(inicio_c4)
botones_inicio_c4.pack(fill='both', expand=True, padx=20, pady=20)
botones_inicio_c4.columnconfigure(0, weight=3)
botones_inicio_c4.columnconfigure(1, weight=3)
botones_inicio_c4.rowconfigure(0, weight=3)

#Botones para usuario
boton_simulador_c4 = ctk.CTkButton(botones_inicio_c4, text="Simulador Gráfico Transitorio", command=mostrar_sim_c4, height=80, font=('Arial', 20))
boton_simulador_c4.grid(row = 0, column = 0, pady=15, padx = 5)

boton_solver_c4 = ctk.CTkButton(botones_inicio_c4, text="Solver Estado Estacionario", command=mostrar_solver_c4, height=80, font=('Arial', 20))
boton_solver_c4.grid(row = 0, column = 1, pady=15, padx = 5)

#_______________________________________________________________________________________________________________________________________

#----------------------------FUNCIÓN CASO 3-------------------DIFUSIÓN REACCIÓN HOMOGÉNEA-------------------------------------------
#_______________________________________________________________________________________________________________________________________

# Configuración específica para Caso 3
frame_c3 = menu.tab("Caso 3")
content_c3 = ctk.CTkFrame(frame_c3)
content_c3.pack(padx=10, pady=5, fill="both", expand=True)

# Frame para las suposiciones
inicio_c3 = ctk.CTkFrame(content_c3)
inicio_c3.pack(padx=10, pady=5, fill="both", expand=True)

#Esquema
esquema_frame_c3 = ctk.CTkFrame(inicio_c3, width=int(principal.winfo_screenwidth()*0.3))
esquema_frame_c3.pack(side = 'right', expand = False, padx = 15, pady = (5,5))

# Obtiene el directorio del script actual
script_dir_c3 = os.path.dirname(os.path.abspath(__file__))
imagen_path_c3 = os.path.join(script_dir_c3, "caso_3.png")

try:
    imagen_pil_c3 = Image.open(imagen_path_c3)

    # Crea una versión CTkImage para modo claro y oscuro (puedes usar la misma imagen PIL)
    esquema_ctk_image_c3 = ctk.CTkImage(light_image=imagen_pil_c3, dark_image=imagen_pil_c3, size = (581,602)) # Ajusta el tamaño

    esquema_label_c3 = ctk.CTkLabel(esquema_frame_c3, image=esquema_ctk_image_c3, text="")
    esquema_label_c3.pack(padx=10, pady=10)

except FileNotFoundError:
    print(f"Error: No se encontró la imagen en la ruta: {imagen_path_c3}")
except Exception as e:
    print(f"Error al cargar la imagen: {e}")

#Suposiciones 
suposiciones_frame_c3 = ctk.CTkFrame(inicio_c3)
suposiciones_frame_c3.pack(fill='both', expand=True, padx=5, pady=5)
# Frame de suposiciones caso 1 
f_caso_3 = ctk.CTkFrame(suposiciones_frame_c3)
f_caso_3.pack(padx=(10,10), pady=20)

sup_caso_3 = ctk.CTkLabel(f_caso_3, 
                        text="Suposiciones para la Difusión con reacción química homogénea",
                        font=('Times New Roman', 22),
                        justify="center")
sup_caso_3.pack(pady=(10,10))

desp_caso_3 = ctk.CTkLabel(f_caso_3, 
                            text="Tenemos una reacción de tipo A + B → AB  con las siguientes consideraciones:\n\n"
                                "- La reacción es ISOTÉRMICA en la fase líquida.\n\n"
                                "- La reacción es irreversible de primer orden.\n\n"
                                "- Se supone una solución binaria de A y B.\n\n"
                                "- Se ignora la cantidad AB que se produce (suposición pseudobinaria).\n\n",
                            font=('Times New Roman', 20),
                            justify="left")
desp_caso_3.pack(padx=10, pady=10, fill="both", expand=True)

# --- Frame para los controles de la escala de los ejes ---
escala_frame_3 = ctk.CTkFrame(inicio_c3)
escala_frame_3.pack(fill='both', expand=False, padx=20, pady=(10,5))
escala_frame_3.columnconfigure(0, weight=1)
escala_frame_3.columnconfigure(1, weight=1)
escala_frame_3.rowconfigure(0, weight=2)
escala_frame_3.rowconfigure(1, weight=1)

# --- Controles para la Escala del Eje Y ---
escala_y_label_3 = ctk.CTkLabel(escala_frame_3, text="Escala Eje Y:")
escala_y_label_3.grid(row = 0, column = 1, padx=5, pady=(5, 0))

escala_y_opciones_3 = ["Lineal", "Logarítmica"]
escala_y_seleccionada_3 = ctk.StringVar(value="Lineal")
escala_y_menu_3 = ctk.CTkComboBox(escala_frame_3, values=escala_y_opciones_3, variable=escala_y_seleccionada_3)
escala_y_menu_3.grid(row = 1, column = 1, padx=5, pady=(0, 5))

# --- Controles para la Escala del Eje X ---
escala_x_label_3 = ctk.CTkLabel(escala_frame_3, text="Escala Eje X:")
escala_x_label_3.grid(row = 0, column = 0, padx=5, pady=(5, 0))

escala_x_opciones_3 = ["Lineal", "Logarítmica"]
escala_x_seleccionada_3 = ctk.StringVar(value="Lineal")
escala_x_menu_3 = ctk.CTkComboBox(escala_frame_3, values=escala_x_opciones_3, variable=escala_x_seleccionada_3)
escala_x_menu_3.grid(row = 1, column = 0, padx=5, pady=(0, 5))

# Frame de simulación (oculto inicialmente)
simulacion_frame_c3 = ctk.CTkFrame(content_c3)
simulacion_frame_c3.pack_forget()

# Configuración inicial
solver_frame_c3 = ctk.CTkFrame(content_c3)
solver_frame_c3.pack_forget()

def mostrar_solver_c3():
    global entry_D_AB_s3, entry_x_A0_s3, resultados_frame_s3, graf_frame_s3, toolbar_frame_s3, entry_L_s3, entry_At_s3, entry_k_s3, boton_exportar_s3, entry_c3
    # Ocultar frame de inicio y configurar solver
    inicio_c3.pack_forget()
    solver_frame_c3.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Limpiar frame existente
    for widget in solver_frame_c3.winfo_children():
        widget.destroy()
    
    # Frame de parámetros (30% del ancho)
    izq_frame_s3 = ctk.CTkFrame(solver_frame_c3, width=int(principal.winfo_screenwidth()*0.3))
    izq_frame_s3.pack(side='left', fill='both', padx=5, pady=5)

    # Frame de la gráfica (70% del ancho)
    right_container_s3 = ctk.CTkScrollableFrame(solver_frame_c3)
    right_container_s3.pack(side='right', fill='both', expand=True, padx=5, pady=5)

    # ----------------------------
    # Frame del gráfico 
    # ----------------------------
    graf_frame_s3 = ctk.CTkFrame(right_container_s3)
    graf_frame_s3.pack(fill='both', expand=True, padx=5, pady=5)

    # Frame para la barra de herramientas
    toolbar_frame_s3 = ctk.CTkFrame(right_container_s3, height=40)
    toolbar_frame_s3.pack(fill='x', padx=5, pady=(0,5))
      
    # ----------------------------
    # Frame de parámetros (arriba)
    # ----------------------------
    param_frame_s3 = ctk.CTkFrame(izq_frame_s3)
    param_frame_s3.pack(fill='both', expand=True, padx=5, pady=5)

    resultados_frame_s3 = ctk.CTkFrame(izq_frame_s3)
    resultados_frame_s3.pack(fill='both', padx=5, pady=5, expand=False)  
    
    # Campos de entrada
    entry_D_AB_s3 = crear_entry(param_frame_s3, 0, "Coeficiente de difusión (D_AB) [m²/s]:", "1.91e-9")
    entry_x_A0_s3 = crear_entry(param_frame_s3, 1, "Fracción molar Inicial:", "0.02")
    entry_c3 = crear_entry(param_frame_s3, 2, "Concentración del sistema [mol/m³]:", "34")
    entry_k_s3 = crear_entry(param_frame_s3, 3, "Constante de reacción [1/s]:", "0.005")
    entry_L_s3 = crear_entry(param_frame_s3, 4, "Longitud L [m]:", "0.015")
    entry_At_s3 = crear_entry(param_frame_s3, 5, "Área Transversal [m²]:", "0.049")

    # Botones de control
    button_frame_s3 = ctk.CTkFrame(izq_frame_s3)
    button_frame_s3.pack(fill='x', padx=5, pady=(5, 10), expand=False)  # Cambiado de grid a pack
    
    # Configurar grid para los botones
    button_frame_s3.columnconfigure(0, weight=1)
    button_frame_s3.columnconfigure(1, weight=1)
    button_frame_s3.columnconfigure(2, weight=1)
    button_frame_s3.rowconfigure(0, weight=1)
    button_frame_s3.rowconfigure(1, weight=1)

    boton_simular_s3 = ctk.CTkButton(
        button_frame_s3, 
        text="Simular", 
        command=solver_3, 
        height=40, 
        font=('Arial', 14)
    )
    boton_simular_s3.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

    boton_borrar_s3 = ctk.CTkButton(
        button_frame_s3, 
        text="Borrar", 
        command=limpiar_s3, 
        fg_color="#d9534f", 
        hover_color="#c9302c", 
        height=40, 
        font=('Arial', 14)
    )
    boton_borrar_s3.grid(row=0, column=1, pady=5, padx=5, sticky="nsew")

    boton_volver_s3 = ctk.CTkButton(
        button_frame_s3,
        text="Volver",
        command=volver_inicio_c3,
        fg_color="#6c757d",
        hover_color="#5a6268",
        height=40,
        font=('Arial', 14)
    )
    boton_volver_s3.grid(row=0, column=2, pady=5, padx=5, sticky="nsew")

    boton_exportar_s3 = ctk.CTkButton(
        button_frame_s3,
        text="Exportar Datos",
        command=exportar_s3,
        fg_color="#27ae60",  # Cambiado a verde para mejor identificación
        hover_color="#219653",
        height=40,
        font=('Arial', 14)
    )
    boton_exportar_s3.grid_forget()

def solver_3():
    global x_A_profile, x_B_profile,z_points
    boton_exportar_s3.grid(row=1, column=1, pady=5, padx=5, sticky="nsew")
    try:
        # Obtención de parámetros introducidos por el usuario
        D_AB = float(entry_D_AB_s3.get())  # Coeficiente de difusión [m²/s]
        x_A0 = float(entry_x_A0_s3.get())  # Concentración de A en z=L 
        c = float (entry_c3.get())         #Concentración del sistema (mol/m^3)
        k = float(entry_k_s3.get())        # Constante de velocidad de reacción [1/s]
        L = float(entry_L_s3.get())        # Longitud del reactor [m]
        A_transversal = float(entry_At_s3.get())  # Área transversal [m²]

        if D_AB <= 0 or x_A0 <= 0 or k <= 0 or L <= 0 or A_transversal <= 0:
            raise ValueError("Todos los parámetros deben ser positivos")

        # Limpiar frames anteriores
        for widget in graf_frame_s3.winfo_children():
            widget.destroy()
        for widget in resultados_frame_s3.winfo_children():
            widget.destroy()

        # Cálculo del módulo de Thiele (φ)
        phi = L * np.sqrt(k / D_AB)

        # 1. Perfil de concentración (Ec. 18.4-10)
        z_points = np.linspace(0, L, 1000)
        x_A_relative = np.cosh(phi * (1 - z_points/L)) / np.cosh(phi)  
        x_A_profile = x_A0 * x_A_relative  
        x_B_profile = 1 - x_A_profile

        # 2. Concentración media (Ec. 18.4-11)
        x_A_media = x_A0 * np.tanh(phi) / phi

        # 3. Densidad de flujo molar en z=0 (Ec. 18.4-12)
        N_A_z0 = c * (x_A0 * D_AB / L) * phi * np.tanh(phi)
        
        # 4. Flujo másico total (W_A = N_A * A_transversal)
        W_A = N_A_z0 * A_transversal  # [mol/s]

        # Mostrar resultados en el frame de respuestas
        resultado_texto = (
            f"Resultados del cálculo:\n"
            f"1. Fracción molar media de A: {x_A_media:.3e}\n"
            f"2. Fracción molar final de A: {x_A_profile[-1]:.3e}\n"
            f"3. Densidad de flujo molar en z=0 (N_A|z=0): {N_A_z0:.3e} mol/(m²·s)\n"
            f"4. Velocidad de absorción (W_A): {W_A:.3e} mol/s\n\n")

        respuestas_label = ctk.CTkLabel(
            resultados_frame_s3,
            text=resultado_texto,
            font=('Consolas', 12),
            justify="left"
        )
        respuestas_label.pack(pady=10)

        #GRÁFICAS

        fig, ax1 = plt.subplots(figsize=(10, 7))
        escala_y_s3 = escala_y_seleccionada_3.get()
        if escala_y_s3 == "Logarítmica":
            ax1.set_yscale('log')
        else:
            ax1.set_yscale('linear')
        escala_x_s3 = escala_x_seleccionada_3.get()
        if escala_x_s3 == "Logarítmica":
            ax1.set_xscale('log')
        else:
            ax1.set_xscale('linear')
        ax1.plot(z_points, x_A_profile, 'b-', linewidth=2, label='$x_A$')
        ax1.plot(z_points, x_B_profile, 'r-', linewidth=2, label='$x_B$')
        ax1.set_xlabel('Posición z [m]', fontsize=12)
        ax1.set_ylabel('Fracción molar', fontsize=12)
        ax1.set_title('Perfiles de concentración (Estado Estacionario)', fontsize=14)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, linestyle='--', alpha=0.6)
        ax1.set_xlim(0, L * 1.05)
        ax1.set_ylim(0, 1)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=graf_frame_s3)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, graf_frame_s3)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    except Exception as e:
        messagebox.showerror("Error", f"Error en simulación:\n{str(e)}")
       
def mostrar_sim_c3():
    global entry_D_AB_c3, entry_tsim_c3, entry_L_c3, entry_tolerancia_c3, entry_N_c3, entry_x_A0_c3, entry_k_c3, entry_dt_c3
    global graf_frame_c3, main_frame_c3, izq_frame_c3, respuestas_frame_c3, param_frame_c3, boton_exportar_c3, boton_pausa_c3, boton_reanudar_c3

    # Ocultar frames de suposiciones y la barra de opciones
    suposiciones_frame_c3.pack_forget()
    inicio_c3.pack_forget()
    botones_inicio_c3.pack_forget()
    
    # Mostrar frame de simulación
    simulacion_frame_c3.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Configurar título dinámico
    for widget in simulacion_frame_c3.winfo_children():
        widget.destroy()
      
    # Main frame para la interfaz de simulación
    main_frame_c3 = ctk.CTkFrame(simulacion_frame_c3)
    main_frame_c3.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Frame de parámetros (30% del ancho)
    izq_frame_c3 = ctk.CTkFrame(main_frame_c3, width=int(principal.winfo_screenwidth()*0.3))
    izq_frame_c3.pack(side='left', fill='y', padx=5, pady=5)
    
    # Frame de la gráfica (70% del ancho)
    right_container_c3 = ctk.CTkFrame(main_frame_c3)
    right_container_c3.pack(side='right', fill='both', expand=True, padx=5, pady=5)

    botones_anim_c3 = ctk.CTkFrame(right_container_c3)  
    botones_anim_c3.pack(fill='both', expand=False, padx=5, pady=(0,0))
    botones_anim_c3.columnconfigure(0, weight=1)
    botones_anim_c3.columnconfigure(1, weight=1)
    
    # Contenedor para gráfica
    graf_frame_c3 = ctk.CTkFrame(right_container_c3)
    graf_frame_c3.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Controles en izq_frame_c2
    param_frame_c3 = ctk.CTkFrame(izq_frame_c3)
    param_frame_c3.pack(padx=10, pady=5, fill='both', expand=True)
    
    # Frame para respuestas
    respuestas_frame_c3 = ctk.CTkFrame(izq_frame_c3)
    respuestas_frame_c3.pack(fill='x', padx=10, pady=(5,5))
    
    # Campos de entrada para el caso 1
    entry_D_AB_c3 = crear_entry(param_frame_c3, 0, "Coeficiente de difusión (D_AB) [m²/s]:", "1.91e-9")
    entry_x_A0_c3 = crear_entry(param_frame_c3, 1, "Fracción molar:", "0.02")
    entry_L_c3 = crear_entry(param_frame_c3, 2, "Longitud (L [m]):", "0.015")
    entry_k_c3 = crear_entry(param_frame_c3, 3, "Constante de reacción [1/s]:", "0.005")
    entry_N_c3 = crear_entry(param_frame_c3, 4, "Número de puntos (N):", "100")
    entry_tsim_c3 = crear_entry(param_frame_c3, 5, "Tiempo de simulación [s]:", "1000")
    entry_dt_c3 = crear_entry(param_frame_c3, 6, "Δt de simulación [s]:", "0.05")
    entry_tolerancia_c3 = crear_entry(param_frame_c3, 7, "Tolerancia:", "1e-5")
    
    # Botones de control
    button_frame_c3 = ctk.CTkFrame(izq_frame_c3)
    button_frame_c3.pack(fill='both', expand=False, padx=5, pady=5)
    button_frame_c3.columnconfigure(0, weight=1)
    button_frame_c3.columnconfigure(1, weight=1)
    button_frame_c3.columnconfigure(2, weight=1)
    button_frame_c3.rowconfigure(0, weight=1)
    button_frame_c3.rowconfigure(1, weight=1)

    boton_simular_c3 = ctk.CTkButton(
        button_frame_c3, 
        text="Simular", 
        command=caso_3, 
        height=40, 
        font=('Arial', 14)
    )
    boton_simular_c3.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

    boton_borrar_c3 = ctk.CTkButton(
        button_frame_c3, 
        text="Borrar", 
        command=limpiar_c3, 
        fg_color="#d9534f", 
        hover_color="#c9302c", 
        height=40, 
        font=('Arial', 14)
    )
    boton_borrar_c3.grid(row=0, column=1, pady=5, padx=5, sticky="nsew")

    boton_volver_c3 = ctk.CTkButton(
        button_frame_c3,
        text="Volver",
        command=volver_inicio_c3,
        fg_color="#6c757d",
        hover_color="#5a6268",
        height=40,
        font=('Arial', 14)
    )
    boton_volver_c3.grid(row=0, column=2, pady=5, padx=5, sticky="nsew")

    boton_exportar_c3 = ctk.CTkButton(
        button_frame_c3,
        text="Exportar Datos",
        command=exportar_c3,
        fg_color="#27ae60",  # Cambiado a verde para mejor identificación
        hover_color="#219653",
        height=40,
        font=('Arial', 14)
    )
    boton_exportar_c3.grid_forget()

    boton_pausa_c3 = ctk.CTkButton(botones_anim_c3, text="⏸️", command=lambda: ani.event_source.stop(), fg_color="#000000", 
    hover_color="#000000", 
    height=20, 
    font=('Arial', 20))
    boton_pausa_c3.grid_forget()

    boton_reanudar_c3 = ctk.CTkButton(botones_anim_c3, text="▶️", command=lambda: ani.event_source.start(), fg_color="#000000",  
        hover_color="#000000",
        height=20,
        font=('Arial', 20)  
    )
    boton_reanudar_c3.grid_forget()

def exportar_c3():
    try:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx"), ("CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar datos de simulación",
            initialfile="simulacion_transitorio_caso_3.xlsx"
        )
        if not filepath:
            return

        # Obtener la tolerancia desde la interfaz
        try:
            tolerancia = float(entry_tolerancia_c3.get())
        except:
            tolerancia = None  # Si no se puede obtener, se manejará más adelante

        if filepath.endswith('.csv'):
            # CSV para casos muy grandes (una sola hoja)
            df_csv = pd.DataFrame({'z [m]': z, 'Estado Estacionario': x_steady})
            for t_csv, perfil_csv in zip(tiempos, transitorios):
                column_name_csv = f't={t_csv:.2f}s'
                # Añadir distintivo si es el tiempo de convergencia
                if tiempo_convergencia is not None and abs(t_csv - tiempo_convergencia) < 1e-9:  # Comparación de flotantes
                    column_name_csv += ' (Convergencia)'
                df_csv[column_name_csv] = perfil_csv
            df_csv.to_csv(filepath, index=False)
            
            # Para CSV no podemos incluir múltiples hojas, así que añadimos
            # un archivo adicional para los datos de convergencia
            if filepath:
                convergence_filepath = filepath.replace('.csv', '_convergencia.csv')
                # Calcular diferencias para cada perfil transitorio
                diffs = []
                convergence_status = []
                for perfil in transitorios:
                    diff = np.mean(np.abs(perfil - x_steady))
                    diffs.append(diff)
                    if tolerancia is not None:
                        convergence_status.append("CONVERGE" if diff <= tolerancia else "NO CONVERGE")
                    else:
                        convergence_status.append("N/A")
                
                df_convergence = pd.DataFrame({
                    'Tiempo [s]': tiempos,
                    'Diferencia promedio': diffs,
                    'Tolerancia': [tolerancia] * len(tiempos) if tolerancia is not None else ["N/A"] * len(tiempos),
                    'Estado': convergence_status
                })
                df_convergence.to_csv(convergence_filepath, index=False)
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}\ny\n{convergence_filepath}")
        else:
            # Excel con organización por hojas optimizada
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja de estado estacionario
                pd.DataFrame({
                    'Posición z [m]': z,
                    'Fracción molar x_A': x_steady
                }).to_excel(writer, sheet_name='Estacionario', index=False)
                
                # Hoja(s) consolidada(s) de transitorios con numeración optimizada
                df_trans_excel_current_sheet = pd.DataFrame({'z [m]': z})
                excel_sheet_counter = 1  # Contador para los nombres de hoja: Transitorios_1, Transitorios_2, ...

                for i, (t_excel, perfil_excel) in enumerate(zip(tiempos, transitorios)):
                    column_header_excel = f't={t_excel:.2f}s'
                    # Añadir distintivo si es el tiempo de convergencia
                    if tiempo_convergencia is not None and abs(t_excel - tiempo_convergencia) < 1e-9:  # Comparación de flotantes
                        column_header_excel += ' (Convergencia)'
                    
                    df_trans_excel_current_sheet[column_header_excel] = perfil_excel

                    # (i + 1) es el número total de perfiles transitorios procesados hasta ahora.
                    # Si hemos procesado un múltiplo de 50 perfiles, guardamos la hoja actual y preparamos una nueva.
                    if (i + 1) % 50 == 0:
                        df_trans_excel_current_sheet.to_excel(writer, sheet_name=f'Transitorios_{excel_sheet_counter}', index=False)
                        # Resetear el DataFrame para la siguiente hoja, comenzando con la columna 'z [m]'
                        df_trans_excel_current_sheet = pd.DataFrame({'z [m]': z})
                        excel_sheet_counter += 1  # Incrementar para la siguiente hoja
                
                # Después del bucle, si quedan datos en df_trans_excel_current_sheet
                # (es decir, tiene más columnas que solo 'z [m]'),
                # esto significa que el número total de transitorios no fue un múltiplo exacto de 50.
                if len(df_trans_excel_current_sheet.columns) > 1:
                    df_trans_excel_current_sheet.to_excel(writer, sheet_name=f'Transitorios_{excel_sheet_counter}', index=False)
                
                # NUEVA HOJA: Información de convergencia
                # Calcular diferencias para cada perfil transitorio
                diffs = []
                convergence_status = []
                for perfil in transitorios:
                    diff = np.mean(np.abs(perfil - x_steady))
                    diffs.append(diff)
                    if tolerancia is not None:
                        convergence_status.append("CONVERGE" if diff <= tolerancia else "NO CONVERGE")
                    else:
                        convergence_status.append("N/A")
                
                df_convergence = pd.DataFrame({
                    'Tiempo [s]': tiempos,
                    'Diferencia promedio': diffs,
                    'Tolerancia': [tolerancia] * len(tiempos) if tolerancia is not None else ["N/A"] * len(tiempos),
                    'Estado': convergence_status
                })
                
                # Añadir una fila de resumen final
                if tiempo_convergencia is not None:
                    resumen = pd.DataFrame({
                        'Tiempo [s]': ["RESUMEN"],
                        'Diferencia promedio': ["---"],
                        'Tolerancia': [tolerancia if tolerancia is not None else "N/A"],
                        'Estado': [f"Convergencia alcanzada en t={tiempo_convergencia:.2f}s"]
                    })
                else:
                    resumen = pd.DataFrame({
                        'Tiempo [s]': ["RESUMEN"],
                        'Diferencia promedio': ["---"],
                        'Tolerancia': [tolerancia if tolerancia is not None else "N/A"],
                        'Estado': ["No se alcanzó convergencia"]
                    })
                
                # Concatenar el DataFrame original con la fila de resumen
                df_convergence = pd.concat([df_convergence, resumen], ignore_index=True)
                
                # Exportar a la hoja de Excel
                df_convergence.to_excel(writer, sheet_name='Convergencia', index=False)

            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")

    except Exception as e:
        if isinstance(e, NameError):
             messagebox.showerror("Error de Variable", 
                f"No se pudo exportar: una variable necesaria (como 'z', 'tiempos', etc.) no fue definida.\n"
                f"Asegúrate de que la simulación ('caso_1') se haya ejecutado primero y haya definido las variables globales.\nDetalle: {str(e)}")
        else:
            messagebox.showerror("Error", 
                f"No se pudo exportar los datos:\n{str(e)}\n")

def exportar_s3():
    try:
        # Preguntar al usuario dónde guardar y el tipo de archivo
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile="estado_estacionario_caso_3",
            filetypes=[("Archivos Excel", "*.xlsx"), ("CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar datos de estado estacionario"
        )

        if filepath:
            df = pd.DataFrame({'z [m]': z_points, 'Fracción molar de A (xA)': x_A_profile, 'Fracción molar de B (xB)': x_B_profile})

            if filepath.endswith('.csv'):
                df.to_csv(filepath, index=False)
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")
            elif filepath.endswith('.xlsx'):
                df.to_excel(filepath, index=False, sheet_name='Concentraciones')
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")
            else:
                messagebox.showerror("Error", "Formato de archivo no válido. Por favor, elija .csv o .xlsx.")

    except Exception as e:
        messagebox.showerror("Error al Exportar", f"Ocurrió un error al exportar los datos:\n{str(e)}")

def volver_inicio_c3():
    # Ocultar frame de simulación
    solver_frame_c3.pack_forget()
    simulacion_frame_c3.pack_forget()
    inicio_c3.pack(padx=10, pady=5, fill="both", expand=True)
    suposiciones_frame_c3.pack(fill='both', expand=True, padx=5, pady=5)
    botones_inicio_c3.pack(fill='both', expand=True, padx=20, pady=20)

def limpiar_c3():
    for widget in graf_frame_c3.winfo_children():
        widget.destroy()
    for widget in respuestas_frame_c3.winfo_children():
        widget.destroy()

    boton_exportar_c3.grid_forget()
    boton_pausa_c3.grid_forget()
    boton_reanudar_c3.grid_forget()
    entry_D_AB_c3.delete(0, 'end')
    entry_x_A0_c3.delete(0, 'end')
    entry_L_c3.delete(0, 'end')
    entry_N_c3.delete(0, 'end')
    entry_k_c3.delete(0, 'end')
    entry_tsim_c3.delete(0, 'end')
    entry_dt_c3.delete(0, 'end')
    entry_tolerancia_c3.delete(0, 'end')
    entry_D_AB_c3.insert(0, "1.91e-9")
    entry_x_A0_c3.insert(0, "0.02")
    entry_L_c3.insert(0, "0.015")
    entry_k_c3.insert(0, "0.005")
    entry_N_c3.insert(0, "100")
    entry_tsim_c3.insert(0, "1000")
    entry_dt_c3.insert(0, "0.05")
    entry_tolerancia_c3.insert(0, "1e-5")

def limpiar_s3():
    for widget in graf_frame_s3.winfo_children():
        widget.destroy()
    for widget in toolbar_frame_s3.winfo_children():
        widget.destroy()
    for widget in resultados_frame_s3.winfo_children():
        widget.destroy()

    boton_exportar_s3.grid_forget()
    boton_exportar_s3.grid_forget()
    entry_D_AB_s3.delete(0, 'end')
    entry_x_A0_s3.delete(0, 'end')
    entry_L_s3.delete(0, 'end')
    entry_At_s3.delete(0, 'end')
    entry_c3.delete(0, 'end')
    entry_D_AB_s3.insert(0, "1.91e-9")
    entry_x_A0_s3.insert(0, "0.02")
    entry_c3.insert(0, "34")
    entry_L_s3.insert(0, "0.015")
    entry_At_s3.insert(0, "0.049")

def caso_3():
    global transitorios, tiempos, x_steady, z, tiempo_convergencia, ani
    boton_exportar_c3.grid(row=1, column=1, pady=5, padx=5, sticky="nsew")
    boton_pausa_c3.grid(row = 0, column = 0, padx=5, pady=0)
    boton_reanudar_c3.grid(row = 0, column = 1, padx=5, pady=0)
    try:
        # Obtención de parámetros introducidos por el usuario
        D_AB = float(entry_D_AB_c3.get())
        k = float(entry_k_c3.get())  
        x_A0 = float(entry_x_A0_c3.get()) 
        L = float(entry_L_c3.get())
        N = int(entry_N_c3.get())
        tsim = int(entry_tsim_c3.get())
        dt_us = float(entry_dt_c3.get())
        tolerancia = float(entry_tolerancia_c3.get())

        if N <= 2 or tsim <= 0 or tolerancia <= 0:
            raise ValueError("N debe ser >2, el tiempo de simulación y la tolerancia deben ser positivas")

        # Limpiar frames anteriores
        for widget in graf_frame_c3.winfo_children():
            widget.destroy()
        for widget in respuestas_frame_c3.winfo_children():
            widget.destroy()

        # 2. Discretización
        iteraciones = math.ceil(tsim/dt_us)
        dz = L / (N - 1)
        z = np.linspace(0, L, N)

        #SOLUCIÓN ANALÍTICA ESTADO ESTACIONARIO
        phi = L * np.sqrt(k / D_AB)

        # 1. Perfil de concentración (Ec. 18.4-10)
        z_points_ana = z
        x_A_relative = np.cosh(phi * (1 - z_points_ana/L)) / np.cosh(phi)  
        x_A_profile_est_ana = x_A0 * x_A_relative  

        # --SOLUCIÓN NUMÉRICA DE ESTADO ESTACIONARIO --
        def solve_ec_diff(c):
            # c ya es de tamaño N-2 (solo puntos interiores)
            # Creamos c_total con las condiciones de frontera incluidas
            x_total = np.zeros(N)
            x_total[0] = x_A0  # CL1: x(0) = x_A0
            x_total[1:-1] = c  # Puntos interiores
            x_total[-1] = c[-1]  # Último punto interior duplicado para la condición Neumann
            
            # Calculamos la ecuación diferencial en los puntos interiores
            F = np.zeros(N-2)  # Solo para puntos interiores
            for i in range(1, N-1):
                F[i-1] = D_AB*(x_total[i+1] - 2*x_total[i] + x_total[i-1])/dz**2 - k*x_total[i]
            
            return F

        # Estimación inicial lineal entre x_A0 y 0
        x_initial_guess = np.linspace(x_A0, 0, N)[1:-1]  # Solo puntos interiores
        x_steady_interior = fsolve(solve_ec_diff, x_initial_guess)

        # Construimos el perfil completo con las condiciones de frontera
        x_steady = np.zeros(N)
        x_steady[0] = x_A0
        x_steady[1:-1] = x_steady_interior
        x_steady[-1] = x_steady[-2]  # Condición Neumann en z=L

        # --SOLUCIÓN DE ESTADO TRANSITORIO--
        dt = dt_us
        alpha = D_AB * dt / (2 * dz**2)  # Coeficiente para difusión
        beta = k * dt / 2                 # Coeficiente para reacción

        x_A = np.zeros(N)
        x_A[0] = x_A0  # CL1
        x_A[-1] = x_A[-2]  # CL2: derivada cero en L
        
        transitorios = []
        tiempos = []
        tiempo_convergencia = None
        perfil_convergido = None

        for n in range(iteraciones):
            x_old = x_A.copy()
            # Construir sistema tridiagonal
            main_diag = np.ones(N-2) * (1 + 2*alpha + beta)  # Diagonal principal
            lower_diag = np.ones(N-3) * (-alpha)             # Diagonal inferior
            upper_diag = np.ones(N-3) * (-alpha)             # Diagonal superior
            rhs = np.zeros(N-2)                              # Vector del lado derecho

            # Llenar el vector rhs (términos explícitos)
            for i in range(1, N-1):
                diffusion_explicit = alpha * (x_old[i+1] - 2*x_old[i] + x_old[i-1])
                reaction_explicit = beta * x_old[i]
                rhs[i-1] = x_old[i] + diffusion_explicit - reaction_explicit

            # Aplicar condiciones de frontera al rhs
            rhs[0] += alpha * x_A0           # Dirichlet en z=0 (x_A = x_A0)
            rhs[-1] += alpha * x_old[-2]     # Neumann en z=L (dx_A/dz = 0)

            # Resolver sistema tridiagonal
            ab = np.vstack([
                np.r_[0, upper_diag],    # Diagonal superior
                main_diag,               # Diagonal principal
                np.r_[lower_diag, 0]     # Diagonal inferior
            ])
            x_interior = solve_banded((1, 1), ab, rhs)  # Solver eficiente

            # Actualizar solución
            x_A[1:-1] = x_interior
            x_A[-1] = x_A[-2]  # Asegurar condición Neumann
            
            # Guardar perfiles transitorios en intervalos regulares
            if n % max(1, iteraciones // 50) == 0 or n == 0:
                transitorios.append(x_A.copy())
                tiempos.append(n * dt)
                      
            # Verificación de convergencia comparando con la solución estacionaria
            if x_steady is not None:
                # Calcular diferencia absoluta promedio entre estados
                diff_num = np.abs(x_A - x_steady)
                diff_promedio_num = np.mean(diff_num)
                
                # Verificar si se alcanzó la convergencia basado en la tolerancia
                if diff_promedio_num <= tolerancia and tiempo_convergencia is None:
                    tiempo_convergencia = n * dt
                    perfil_convergido = x_A.copy()
                    
                    # Guardar el perfil convergido si no estaba en los guardados periódicamente
                    if n % max(1, iteraciones // 50) != 0 and n != 0:
                        transitorios.append(x_A.copy())
                        tiempos.append(n * dt)
                    
        # Resultado final y mensaje
        perfil_final = perfil_convergido if perfil_convergido is not None else x_A.copy()

        
        #--RESULTADOS--
        if tiempo_convergencia is not None:
            resultado_texto = (
                f"Iteraciones realizadas: {iteraciones}\n"
                f"Convergencia alcanzada en la iteración {tiempo_convergencia/dt:.0f}\n"
                f"Tiempo de convergencia: {tiempo_convergencia:.3f} s\n"
                f"Diferencia entre estado estacionario y transitorio: {diff_promedio_num:.3e}\n"
                f"Tiempo simulado total: {iteraciones*dt:.3f} s\n"
                f"Paso temporal (Δt): {dt:.3e} s)\n"
                f"Constante de reacción k: {k:.3e} s⁻¹"
            )
        else:
            resultado_texto = (
                f"Iteraciones realizadas: {iteraciones}\n"
                f"El sistema NO CONVERGE con {iteraciones} iteraciones\na una tolerancia de {tolerancia}\n"
                f"Diferencia entre estado estacionario y transitorio: {diff_promedio_num:.3e}\n"
                f"Tiempo simulado total: {iteraciones*dt:.3f} s\n"
                f"Paso temporal (Δt): {dt:.3e} s)\n"
                f"Constante de reacción k: {k:.3e} s⁻¹"
            )

        respuestas_label = ctk.CTkLabel(
            respuestas_frame_c3,
            text=resultado_texto,
            font=('Consolas', 12),
            justify="left"
        )
        respuestas_label.pack(pady=10)

        #--GRÁFICAS--

        fig, ax = plt.subplots(figsize=(8, 5))
        escala_y = escala_y_seleccionada_3.get()
        escala_x = escala_x_seleccionada_3.get()

        # Aplicar la escala al eje Y
        if escala_y == "Logarítmica":
            ax.set_yscale('log')
        else:
            ax.set_yscale('linear')

        # Aplicar la escala al eje X
        if escala_x == "Logarítmica":
            ax.set_xscale('log')
        else:
            ax.set_xscale('linear')

        lines = []
        for _ in range(len(transitorios)):
            line, = ax.plot([], [], '--', alpha=0.6)
            lines.append(line)
        steady_line, = ax.plot(z, x_steady, 'r-', linewidth=2, label='Estado estacionario Numérico')
        steady_line_ana, = ax.plot(z_points_ana, x_A_profile_est_ana, 'k.-', linewidth=2, label='Estado estacionario Analítico')
        convergido = ax.plot(z, perfil_final, 'b:', linewidth = 4, label= f'Converge a t = {tiempo_convergencia:.3f}s' ) 
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10, verticalalignment='top')

        ax.set_xlabel('Posición z [m]', fontsize=12) # Etiqueta en cm
        ax.set_ylabel('Fracción molar $x_A$', fontsize=12)
        ax.set_title(f'Difusión con Reacción Homogénea', fontsize=14)
        ax.legend(loc='upper right', fontsize=10, framealpha=0.95)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlim(0, L * 1.05) 
        ax.set_ylim(-0.01, x_A0 * 1.1)

        # Ajustar los límites del eje Y considerando la escala
        all_data = transitorios + [x_steady]
        min_y_data = min(np.min(d) for d in all_data)
        max_y_data = max(np.max(d) for d in all_data)
        if escala_y == "Logarítmica":
            ax.set_ylim(max(1e-9, min_y_data), max_y_data * 1.1)
        else:
            ax.set_ylim(0, x_A0 * 1.1)

        def animate(i):
            lines[i].set_data(z , transitorios[i]) 
            time_text.set_text(f'Tiempo t = {tiempos[i]:.2f} s')
            return (*lines[:i+1], time_text)

        ani = animation.FuncAnimation(fig, animate, frames=len(transitorios), interval=200, blit=True, repeat=True)

        canvas = FigureCanvasTkAgg(fig, master=graf_frame_c3)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, graf_frame_c3)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    except Exception as e:
        messagebox.showerror("Error", f"Error en simulación:\n{str(e)}")

# Frame para botones de opciones
botones_inicio_c3 = ctk.CTkFrame(inicio_c3)
botones_inicio_c3.pack(fill='both', expand=True, padx=20, pady=20)
botones_inicio_c3.columnconfigure(0, weight=3)
botones_inicio_c3.columnconfigure(1, weight=3)
botones_inicio_c3.rowconfigure(0, weight=3)

#Botones para usuario
boton_simulador_c3 = ctk.CTkButton(botones_inicio_c3, text="Simulador Gráfico Transitorio", command=mostrar_sim_c3, height=80, font=('Arial', 20))
boton_simulador_c3.grid(row = 0, column = 0, pady=15, padx = 5)

boton_solver_c3 = ctk.CTkButton(botones_inicio_c3, text="Solver Estado Estacionario", command=mostrar_solver_c3, height=80, font=('Arial', 20))
boton_solver_c3.grid(row = 0, column = 1, pady=15, padx = 5)

#_______________________________________________________________________________________________________________________________________

#----------------------------FUNCIÓN CASO 2-------------------DIFUSIÓN REACCIÓN HETEROGÉNEA-------------------------------------------
#_______________________________________________________________________________________________________________________________________

# Configuración para el caso 2

frame_c2 = menu.tab("Caso 2")
content_c2 = ctk.CTkFrame(frame_c2)
content_c2.pack(padx=1, pady=5, fill="both", expand=True)

#Frame para el menu desplegable
opciones_frame = ctk.CTkFrame(content_c2)
opciones_frame.pack(padx=20, pady=(0,15))

# Frame para el inicio del caso 2
menu_frame_2 = ctk.CTkFrame(content_c2)
menu_frame_2.pack(padx=(50,50), pady=(10,10), fill="x")

# Menú desplegable
subcasos = ['Reacción instantánea Simulador Transitorio', 'Reacción no instantánea Simulador Transitorio', 'Reacción instantánea Simulador Estacionario', 'Reacción no instantánea Simulador Estacionario']
menu_c2 = ctk.CTkOptionMenu(opciones_frame, 
                        values=subcasos, 
                        command=lambda opcion: mostrar_sim_2(opcion) if "Transitorio" in opcion else mostrar_solver_2(opcion),
                        width=300,
                        font=('Arial', 14))
menu_c2.pack(side = 'right', pady=(0,10), padx = (50,50))
menu_c2.set('Seleccione el tipo de reacción y el tipo de Simulador')

# --- Frame para los controles de la escala de los ejes ---
escala_frame_2 = ctk.CTkFrame(opciones_frame)
escala_frame_2.pack(side = 'left', fill='both', expand=False, padx=(50,50) , pady=(10,5))
escala_frame_2.columnconfigure(0, weight=1)
escala_frame_2.columnconfigure(1, weight=1)
escala_frame_2.rowconfigure(0, weight=2)
escala_frame_2.rowconfigure(1, weight=1)

# --- Controles para la Escala del Eje Y ---
escala_y_label_2 = ctk.CTkLabel(escala_frame_2, text="Escala Eje Y:")
escala_y_label_2.grid(row = 0, column = 1, padx=5, pady=(5, 0))

escala_y_opciones_2 = ["Lineal", "Logarítmica"]
escala_y_seleccionada_2 = ctk.StringVar(value="Lineal")
escala_y_menu_2 = ctk.CTkComboBox(escala_frame_2, values=escala_y_opciones_2, variable=escala_y_seleccionada_2)
escala_y_menu_2.grid(row = 1, column = 1, padx=5, pady=(0, 5))

# --- Controles para la Escala del Eje X ---
escala_x_label_2 = ctk.CTkLabel(escala_frame_2, text="Escala Eje X:")
escala_x_label_2.grid(row = 0, column = 0, padx=5, pady=(5, 0))

escala_x_opciones_2 = ["Lineal", "Logarítmica"]
escala_x_seleccionada_2 = ctk.StringVar(value="Lineal")
escala_x_menu_2 = ctk.CTkComboBox(escala_frame_2, values=escala_x_opciones_2, variable=escala_x_seleccionada_2)
escala_x_menu_2.grid(row = 1, column = 0, padx=5, pady=(0, 5))

# Frame principal con dos subframes de suposiciones (estado inicial)
suposiciones_frame_2 = ctk.CTkFrame(menu_frame_2)
suposiciones_frame_2.pack(side = 'left', fill='both', expand=True, padx=(5,5) , pady=5)
suposiciones_frame_2.columnconfigure(0, weight=1)
suposiciones_frame_2.rowconfigure(0, weight=1)
suposiciones_frame_2.rowconfigure(1, weight=1)

# Frame de suposiciones caso 2.1 (Reacción instantánea)
f_caso_2_1 = ctk.CTkFrame(suposiciones_frame_2)
f_caso_2_1.grid(row=0, column=0, padx=(5,5), pady=(5,5))

sup_caso_2_1 = ctk.CTkLabel(f_caso_2_1, 
                        text="Suposiciones para la Difusión con Reacción Heterogénea con reacción instantánea",
                        font=('Times New Roman', 20),
                        justify="center")
sup_caso_2_1.pack(pady=(5,5))

desp_caso_2_1 = ctk.CTkLabel(f_caso_2_1, 
                            text="Tenemos una reacción de tipo 2A → B y las siguientes suposiciones:\n\n"
                                "- La reacción es instantánea.\n\n"
                                "- El producto B se difunde retirándose a través de la corriente gaseosa.\n\n"
                                "- Se conoce el espesor de la película de gas y las concentraciones x_A0 y x_B0.\n\n"
                                "- La película de gas es isotérmica, se desprecia calores de reacción.",
                            font=('Times New Roman', 18),
                            justify="left")
desp_caso_2_1.pack(padx=2, pady=5, fill="both", expand=True)

#Esquema
esquema_frame_2 = ctk.CTkFrame(menu_frame_2, width=int(principal.winfo_screenwidth()*0.5))
esquema_frame_2.pack(side = 'right', padx=(2,2), pady=(10,10))

# Obtiene el directorio del script actual
script_dir_2 = os.path.dirname(os.path.abspath(__file__))
imagen_path_2 = os.path.join(script_dir_2, "caso_2.png")

try:
    imagen_pil = Image.open(imagen_path_2)

    # Crea una versión CTkImage para modo claro y oscuro (puedes usar la misma imagen PIL)
    esquema_ctk_image = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size = (580,471)) # Ajusta el tamaño

    esquema_label = ctk.CTkLabel(esquema_frame_2, image=esquema_ctk_image, text="")
    esquema_label.pack(padx=2, pady=10)

except FileNotFoundError:
    print(f"Error: No se encontró la imagen en la ruta: {imagen_path_2}")
except Exception as e:
    print(f"Error al cargar la imagen: {e}")


# Frame de suposiciones caso 2.2 (Reacción NO instantánea)
f_caso_2_2 = ctk.CTkFrame(suposiciones_frame_2)
f_caso_2_2.grid(row=1, column=0, padx=(5,5), pady=0)

sup_caso_2_2 = ctk.CTkLabel(f_caso_2_2, 
                        text="Suposiciones para la Difusión con Reacción Heterogénea con reacción NO instantánea",
                        font=('Times New Roman', 20),
                        justify="center")
sup_caso_2_2.pack(pady=(5,5))

desp_caso_2_2 = ctk.CTkLabel(f_caso_2_2, 
                            text="Tenemos una reacción de tipo 2A→B y las siguientes suposiciones:\n\n"
                                "- La velocidad de desaparición de A es proporcional a su concentración.\n\n"
                                "\t\t\tN_Az = k·c·x_A\n\n"
                                "- k es una constante de velocidad para reacción de pseudo primer orden.\n\n"
                                "- La condición de borde cambia a x_A = N_Az/(k·c) en z=δ.",
                            font=('Times New Roman', 18),
                            justify="left")
desp_caso_2_2.pack(padx=2, pady=10, fill="both", expand=True)
# Frame de simulación (oculto inicialmente)
simulacion_frame_2 = ctk.CTkFrame(content_c2)
simulacion_frame_2.pack_forget()

# Configuración inicial
solver_frame_c2 = ctk.CTkFrame(content_c2)
solver_frame_c2.pack_forget()

def solver_2(opcion):
    global x_A_profile, x_B_profile, z_points
    boton_exportar_s2.grid(row=1, column=1, pady=5, padx=5)
    try:
        D_AB = float(entry_D_AB_s2.get())
        x_A0 = float(entry_x_A0_s2.get())
        delta = float(entry_delta_s2.get())/1000
        k = float(entry_k.get())
        c = float(entry_c2.get())

        if not (0 < x_A0 < 1):
            raise ValueError("Las fracciones molares deben estar entre 0 y 1")
        if delta <= 0:
            raise ValueError("δ debe ser mayor que 0")
        if D_AB <= 0 or k <= 0 or c <= 0:
            raise ValueError("D_AB, k y c deben ser positivos")

        for widget in graf_frame_s2.winfo_children():
            widget.destroy()
        for widget in respuestas_frame_s2.winfo_children():
            widget.destroy()

        x_A_profile = []
        x_B_profile = []
        z_points = np.linspace(0, delta, 1000)
        Da =  k * delta/D_AB

        if opcion == 'Reacción instantánea Simulador Estacionario':                  
            factor = 1 - (1/2) * x_A0
            # Aplicando la ecuación 18.3-8:
            x_A_profile = 2 * (1 - factor ** (1 - z_points / delta))
            x_B_profile = 1 - x_A_profile
            
            # Aplicando la ecuación 18.3-9:
            N_Az = (2 * c * D_AB / delta) * np.log(1 / factor)
            x_B_profile = 1 - x_A_profile
            
            # Cálculo de N_Az
            N_Az = (2*c * D_AB / delta) * np.log(1 / factor)
            
            resultado_texto = (
                f"Resultados del cálculo para Reacción Instantánea:\n\n"
                f"1. Densidad de flujo molar (N_Az): {N_Az:.3e} mol/(m²·s)\n"
                f"2. Número de Damköhler (k·δ/D_AB): {Da:.3f}\n")
            respuestas_label = ctk.CTkLabel(respuestas_frame_s2, text=resultado_texto, font=('Consolas', 12), justify="left")
            respuestas_label.pack(pady=10)

        elif opcion == 'Reacción no instantánea Simulador Estacionario':
            N_Az_inicial = 1e-6
            N_Az_calculado_array, info, ier, mesg = fsolve(
                lambda N_Az: N_Az - (2 * c * D_AB / delta) * np.log((1 - 0.5 * (N_Az / (k*c))) / (1 - 0.5 * x_A0)),
                N_Az_inicial,
                full_output=True
            )
            if ier != 1:
                raise ValueError(f"No se pudo encontrar N_Az: {mesg}")
            N_Az_calculado = N_Az_calculado_array[0]
            x_A_profile = np.zeros(len(z_points))
            for i, zi in enumerate(z_points):
                term1 = (1 - 0.5 * (N_Az_calculado / (k*c)))**(zi / delta)
                term2 = (1 - 0.5 * x_A0)**(1 - (zi / delta))
                x_A_profile[i] = 2 * (1 - term1 * term2)
            x_B_profile = 1 - x_A_profile
            resultado_texto = (f"Resultados del cálculo para Reacción No Instantánea:\n\n1. Densidad de flujo molar (N_Az): {N_Az_calculado:.3e} mol/(m²·s)\n2. Número de Damköhler (k·δ/D_AB): {Da:.3f}\n3. Fracción molar de A en z=δ (x_A_final): {x_A_profile[-1]:.5f}")
            respuestas_label = ctk.CTkLabel(respuestas_frame_s2, text=resultado_texto, font=('Consolas', 12), justify="left")
            respuestas_label.pack(pady=10)

        # GRÁFICA
        fig, ax1 = plt.subplots(figsize=(9, 6.5))
        escala_y_s2 = escala_y_seleccionada_2.get()
        if escala_y_s2 == "Logarítmica":
            ax1.set_yscale('log')
        else:
            ax1.set_yscale('linear')
        escala_x_s2 = escala_x_seleccionada_2.get()
        if escala_x_s2 == "Logarítmica":
            ax1.set_xscale('log')
        else:
            ax1.set_xscale('linear')
        ax1.plot(z_points * 100, x_A_profile, 'b-', linewidth=2, label='$x_A$')
        ax1.plot(z_points * 100, x_B_profile, 'r-', linewidth=2, label='$x_B$')
        ax1.set_xlabel('Posición δ [cm]', fontsize=12)
        ax1.set_ylabel('Fracción molar', fontsize=12)
        ax1.set_title('Perfiles de concentración (Estado Estacionario)', fontsize=14)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, linestyle='--', alpha=0.6)
        ax1.set_xlim(0, delta * 100 * 1.05)
        ax1.set_ylim(0, 1)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=graf_frame_s2)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, graf_frame_s2)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    except Exception as e:
        messagebox.showerror("Error", f"Error en simulación:\n{str(e)}")

def mostrar_solver_2(opcion):
    global entry_D_AB_s2, entry_delta_s2, entry_x_A0_s2, entry_k, entry_c2
    global graf_frame_s2, main_frame_s2, izq_frame_s2, respuestas_frame_s2, param_frame_s2, boton_exportar_s2

    if opcion == 'Reacción instantánea Simulador Estacionario' or opcion == 'Reacción no instantánea Simulador Estacionario':
       
        # Ocultar frames de suposiciones y la barra de opciones
        suposiciones_frame_2.pack_forget()
        menu_frame_2.pack_forget()
        opciones_frame.pack_forget()
        
        # Mostrar frame de simulación
        solver_frame_c2.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configurar título dinámico
        for widget in solver_frame_c2.winfo_children():
            widget.destroy()
        
        # Main frame para la interfaz de simulación
        main_frame_s2 = ctk.CTkFrame(solver_frame_c2)
        main_frame_s2.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Frame de parámetros (30% del ancho)
        izq_frame_s2 = ctk.CTkFrame(main_frame_s2, width=int(principal.winfo_screenwidth()*0.3))
        izq_frame_s2.pack(side='left', fill='y', padx=5, pady=5)
        
        # Frame de la gráfica (70% del ancho)
        right_container_s2 = ctk.CTkFrame(main_frame_s2)
        right_container_s2.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Contenedor para gráfica
        graf_frame_s2 = ctk.CTkFrame(right_container_s2)
        graf_frame_s2.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Controles en izq_frame_s2
        param_frame_s2 = ctk.CTkFrame(izq_frame_s2)
        param_frame_s2.pack(padx=10, pady=5, fill='both', expand=True)
        
        # Frame para respuestas
        respuestas_frame_s2 = ctk.CTkFrame(izq_frame_s2)
        respuestas_frame_s2.pack(fill='x', padx=10, pady=(0,5))
        
        # Campos de entrada
        entry_D_AB_s2 = crear_entry(param_frame_s2, 0, "Coeficiente de difusión (D_AB) [m²/s]:", "5.43e-6")
        entry_x_A0_s2 = crear_entry(param_frame_s2, 1, "Fracción molar (x_A0):", "0.996")
        entry_delta_s2 = crear_entry(param_frame_s2, 2, "Espesor de película (δ [mm]):", "0.1")
        entry_c2 = crear_entry(param_frame_s2, 3, "Concentración molar total (mol/m³):", "41.04")
        entry_k = crear_entry(param_frame_s2, 4, "Constante de reacción (k) [m/s]:", "0.75")
        
        # Frame para botones
        button_frame_s2 = ctk.CTkFrame(izq_frame_s2)
        button_frame_s2.pack(fill='both', expand=True, padx=5, pady=0)
        button_frame_s2.columnconfigure(0, weight=1)
        button_frame_s2.columnconfigure(1, weight=1)
        button_frame_s2.columnconfigure(2, weight=1)
        button_frame_s2.rowconfigure(0, weight=1)
        button_frame_s2.rowconfigure(1, weight=1)
        
        # Botón Simular
        boton_simular_s2 = ctk.CTkButton(button_frame_s2, 
                                        text="Simular", 
                                        command=lambda: solver_2(opcion),
                                        height=40,
                                        font=('Arial', 14))
        boton_simular_s2.grid(row=0, column=0, pady=5, padx=5)
    
        # Botón Borrar
        boton_borrar_s2 = ctk.CTkButton(button_frame_s2, 
                                    text="Borrar", 
                                    command=limpiar_s2,
                                    fg_color="#d9534f",
                                    hover_color="#c9302c",
                                    height=40,
                                    font=('Arial', 14))
        boton_borrar_s2.grid(row=0, column=1, pady=5, padx=5)
        
        # Botón Volver
        boton_volver_s2 = ctk.CTkButton(button_frame_s2,
                                    text="Volver",
                                    command=volver_inicio_c2,
                                    fg_color="#6c757d",
                                    hover_color="#5a6268",
                                    height=40,
                                    font=('Arial', 14))
        boton_volver_s2.grid(row=0, column=2, pady=5, padx=5)
        
        boton_exportar_s2 = ctk.CTkButton(
            button_frame_s2,
            text="Exportar Datos",
            command=lambda: exportar_s2(opcion),
            fg_color="#27ae60",
            hover_color="#219653",
            height=40,
            font=('Arial', 14)
        )
        boton_exportar_s2.grid_forget()

def limpiar_s2():
    for widget in graf_frame_s2.winfo_children():
        widget.destroy()
    for widget in respuestas_frame_s2.winfo_children():
        widget.destroy()
    boton_exportar_s2.grid_forget()
    entry_D_AB_s2.delete(0, 'end')
    entry_x_A0_s2.delete(0, 'end')
    entry_delta_s2.delete(0, 'end')
    entry_c2.delete(0, 'end')
    entry_k.delete(0, 'end')
    entry_D_AB_s2.insert(0, "5.43e-6")
    entry_x_A0_s2.insert(0, "0.996")
    entry_delta_s2.insert(0, "0.1")
    entry_c2.insert(0, "41.04")
    entry_k.insert(0, "0.75")

def mostrar_sim_2(opcion):
    global entry_D_AB_c2, entry_dt_c2, entry_delta_c2, entry_tolerancia_c2, entry_N_c2, entry_x_A0_c2, entry_k, entry_c_2
    global graf_frame_c2, main_frame_c2, izq_frame_c2, entry_tsim_c2, respuestas_frame_c2, param_frame_c2, boton_exportar_c2, botones_anim_c2, boton_reanudar_c2, boton_pausa_c2

    if opcion == 'Reacción instantánea Simulador Transitorio' or opcion == 'Reacción no instantánea Simulador Transitorio':

        # Ocultar frames de suposiciones y la barra de opciones
        suposiciones_frame_2.pack_forget()
        menu_frame_2.pack_forget()
        opciones_frame.pack_forget()
        
        # Mostrar frame de simulación
        simulacion_frame_2.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configurar título dinámico
        for widget in simulacion_frame_2.winfo_children():
            widget.destroy()
        
        # Main frame para la interfaz de simulación
        main_frame_c2 = ctk.CTkFrame(simulacion_frame_2)
        main_frame_c2.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Frame de parámetros (30% del ancho)
        izq_frame_c2 = ctk.CTkFrame(main_frame_c2, width=int(principal.winfo_screenwidth()*0.3))
        izq_frame_c2.pack(side='left', fill='y', padx=5, pady=5)
        
        # Frame de la gráfica (70% del ancho)
        right_container_c2 = ctk.CTkFrame(main_frame_c2)
        right_container_c2.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        botones_anim_c2 = ctk.CTkFrame(right_container_c2)  
        botones_anim_c2.pack(fill='both', expand=False, padx=5, pady=(0,0))
        botones_anim_c2.columnconfigure(0, weight=1)
        botones_anim_c2.columnconfigure(1, weight=1)

        # Contenedor para gráfica
        graf_frame_c2 = ctk.CTkFrame(right_container_c2)
        graf_frame_c2.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Controles en izq_frame_c2
        param_frame_c2 = ctk.CTkScrollableFrame(izq_frame_c2)
        param_frame_c2.pack(padx=10, pady=5, fill='both', expand=True)
        
        # Frame para respuestas
        respuestas_frame_c2 = ctk.CTkFrame(izq_frame_c2)
        respuestas_frame_c2.pack(fill='x', padx=10, pady=(0,5))
        
        # Campos de entrada
        entry_D_AB_c2 = crear_entry(param_frame_c2, 0, "Coeficiente de difusión (D_AB) [m²/s]:", "5.43e-6")
        entry_x_A0_c2 = crear_entry(param_frame_c2, 1, "Fracción molar (x_A0):", "0.996")
        entry_delta_c2 = crear_entry(param_frame_c2, 2, "Espesor de película (δ [mm]):", "0.1")
        entry_N_c2 = crear_entry(param_frame_c2, 3, "Número de puntos (N):", "100")
        entry_tsim_c2 = crear_entry(param_frame_c2, 4, "Tiempo de simulación [s]:", "0.001")
        entry_dt_c2 = crear_entry(param_frame_c2, 5, "Δt de simulación [s]:", "1e-7")
        entry_tolerancia_c2 = crear_entry(param_frame_c2, 6, "Tolerancia:", "5e-3")
        entry_k = crear_entry(param_frame_c2, 7, "Constante de reacción (k) [m/s]:", "0.75")
        entry_c_2 = crear_entry(param_frame_c2, 8, "Concentración del sistema (mol/m³):", "41.04")
        
        # Frame para botones
        button_frame_c2 = ctk.CTkFrame(izq_frame_c2)
        button_frame_c2.pack(fill='both', expand=True, padx=5, pady=0)
        button_frame_c2.columnconfigure(0, weight=1)
        button_frame_c2.columnconfigure(1, weight=1)
        button_frame_c2.columnconfigure(2, weight=1)
        button_frame_c2.rowconfigure(0, weight=1)
        button_frame_c2.rowconfigure(1, weight=1)
        
        # Botón Simular
        boton_simular_c2 = ctk.CTkButton(button_frame_c2, 
                                        text="Simular", 
                                        command=lambda: caso_2(opcion),
                                        height=40,
                                        font=('Arial', 14))
        boton_simular_c2.grid(row = 0, column = 0, pady=5, padx = 5)
    
        # Botón Borrar
        boton_borrar_c2 = ctk.CTkButton(button_frame_c2, 
                                    text="Borrar", 
                                    command=limpiar_c2,
                                    fg_color="#d9534f",
                                    hover_color="#c9302c",
                                    height=40,
                                    font=('Arial', 14))
        boton_borrar_c2.grid(row = 0, column = 1, pady=5, padx = 5)
        
        # Botón Volver
        boton_volver_c2 = ctk.CTkButton(button_frame_c2,
                                    text="Volver",
                                    command=volver_inicio_c2,
                                    fg_color="#6c757d",
                                    hover_color="#5a6268",
                                    height=40,
                                    font=('Arial', 14))
        boton_volver_c2.grid(row = 0, column = 2, pady=5, padx = 5)
        
        boton_exportar_c2 = ctk.CTkButton(
            button_frame_c2,
            text="Exportar Datos",
            command=lambda: exportar_c2(opcion),
            fg_color="#27ae60",  # Cambiado a verde para mejor identificación
            hover_color="#219653",
            height=40,
            font=('Arial', 14)
        )
        boton_exportar_c2.grid_forget()

        # En la parte de la interfaz donde creas los controles
        boton_pausa_c2 = ctk.CTkButton(botones_anim_c2, text="⏸️", command=lambda: ani.event_source.stop(), fg_color="#000000", 
            hover_color="#000000", 
            height=20, 
            font=('Arial', 20))
        boton_pausa_c2.grid_forget()

        boton_reanudar_c2 = ctk.CTkButton(botones_anim_c2, text="▶️", command=lambda: ani.event_source.start(), fg_color="#000000",  
            hover_color="#000000",
            height=20,
            font=('Arial', 20)  
        )
        boton_reanudar_c2.grid_forget()

def volver_inicio_c2():
    # Ocultar frame de simulación
    solver_frame_c2.pack_forget()
    simulacion_frame_2.pack_forget()
    opciones_frame.pack(padx=20, pady=(0,15))
    menu_frame_2.pack(padx=20, pady=(0,15), fill="x")
    suposiciones_frame_2.pack(fill='both', expand=True, padx=5, pady=5)
    menu_c2.set('Seleccione el tipo de reacción')

def exportar_c2(opcion):

    try:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx"), ("CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar datos de simulación",
            initialfile=(
                "simulacion_transitorio_caso_2_instantaneo.xlsx"
                if opcion == 'Reacción instantánea Simulador Transitorio'
                else "simulacion_transitorio_caso_2_no_instantaneo.xlsx"
            ),
        )
        if not filepath:
            return

        # Obtener la tolerancia desde la interfaz de caso_2
        try:
            tolerancia = float(entry_tolerancia_c2.get())
        except ValueError:
            tolerancia = None  # Si no se puede obtener, se manejará más adelante

        if filepath.endswith('.csv'):
            # CSV para casos muy grandes (una sola hoja)
            df_csv = pd.DataFrame({'z [m]': z, 'Estado Estacionario': x_steady})
            for t_csv, perfil_csv in zip(tiempos, transitorios):
                column_name_csv = f't={t_csv:.2f}s'
                # Añadir distintivo si es el tiempo de convergencia
                if tiempo_convergencia is not None and abs(t_csv - tiempo_convergencia) < 1e-9:  # Comparación de flotantes
                    column_name_csv += ' (Convergencia)'
                df_csv[column_name_csv] = perfil_csv
            df_csv.to_csv(filepath, index=False)

            # Para CSV no podemos incluir múltiples hojas, así que añadimos
            # un archivo adicional para los datos de convergencia
            if filepath:
                convergence_filepath = filepath.replace('.csv', '_convergencia.csv')
                # Calcular diferencias para cada perfil transitorio
                diffs = []
                convergence_status = []
                for perfil in transitorios:
                    diff = np.mean(np.abs(perfil - x_steady))
                    diffs.append(diff)
                    if tolerancia is not None:
                        convergence_status.append("CONVERGE" if diff <= tolerancia else "NO CONVERGE")
                    else:
                        convergence_status.append("N/A")

                df_convergence = pd.DataFrame({
                    'Tiempo [s]': tiempos,
                    'Diferencia promedio': diffs,
                    'Tolerancia': [tolerancia] * len(tiempos) if tolerancia is not None else ["N/A"] * len(tiempos),
                    'Estado': convergence_status
                })
                df_convergence.to_csv(convergence_filepath, index=False)
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}\ny\n{convergence_filepath}")
        else:
            # Excel 
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja de estado estacionario
                pd.DataFrame({
                    'Posición z [m]': z,
                    'Fracción molar x_A': x_steady
                }).to_excel(writer, sheet_name='Estacionario', index=False)

                # Hojas de transitorios con numeración optimizada
                df_trans_excel_current_sheet = pd.DataFrame({'z [m]': z})
                excel_sheet_counter = 1  # Contador para los nombres de hoja: Transitorios_1, Transitorios_2, ...

                for i, (t_excel, perfil_excel) in enumerate(zip(tiempos, transitorios)):
                    column_header_excel = f't={t_excel:.4f}s'
                    # Añadir distintivo si es el tiempo de convergencia
                    if tiempo_convergencia is not None and abs(t_excel - tiempo_convergencia) < 1e-9:  # Comparación de flotantes
                        column_header_excel += ' (Convergencia)'

                    df_trans_excel_current_sheet[column_header_excel] = perfil_excel


                    if (i + 1) % 50 == 0:
                        df_trans_excel_current_sheet.to_excel(writer, sheet_name=f'Transitorios_{excel_sheet_counter}', index=False)
                        # Resetear el DataFrame para la siguiente hoja, comenzando con la columna 'z [m]'
                        df_trans_excel_current_sheet = pd.DataFrame({'z [m]': z})
                        excel_sheet_counter += 1  # Incrementar para la siguiente hoja


                if len(df_trans_excel_current_sheet.columns) > 1:
                    df_trans_excel_current_sheet.to_excel(writer, sheet_name=f'Transitorios_{excel_sheet_counter}', index=False)

                diffs = []
                convergence_status = []
                for perfil in transitorios:
                    diff = np.mean(np.abs(perfil - x_steady))
                    diffs.append(diff)
                    if tolerancia is not None:
                        convergence_status.append("CONVERGE" if diff <= tolerancia else "NO CONVERGE")
                    else:
                        convergence_status.append("N/A")

                df_convergence = pd.DataFrame({
                    'Tiempo [s]': tiempos,
                    'Diferencia promedio': diffs,
                    'Tolerancia': [tolerancia] * len(tiempos) if tolerancia is not None else ["N/A"] * len(tiempos),
                    'Estado': convergence_status
                })

                # Añadir una fila de resumen final
                if tiempo_convergencia is not None:
                    resumen = pd.DataFrame({
                        'Tiempo [s]': ["RESUMEN"],
                        'Diferencia promedio': ["---"],
                        'Tolerancia': [tolerancia if tolerancia is not None else "N/A"],
                        'Estado': [f"Convergencia alcanzada en t={tiempo_convergencia:.3e}s"]
                    })
                else:
                    resumen = pd.DataFrame({
                        'Tiempo [s]': ["RESUMEN"],
                        'Diferencia promedio': ["---"],
                        'Tolerancia': [tolerancia if tolerancia is not None else "N/A"],
                        'Estado': ["No se alcanzó convergencia"]
                    })

                # Concatenar el DataFrame original con la fila de resumen
                df_convergence = pd.concat([df_convergence, resumen], ignore_index=True)

                # Exportar a la hoja de Excel
                df_convergence.to_excel(writer, sheet_name='Convergencia', index=False)

            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")

    except Exception as e:
        if isinstance(e, NameError):
            messagebox.showerror("Error de Variable",
                                 f"No se pudo exportar: una variable necesaria (como 'z', 'tiempos', etc.) no fue definida.\n"
                                 f"Asegúrate de que la simulación ('caso_2') se haya ejecutado primero y haya definido las variables globales.\nDetalle: {str(e)}")
        else:
            messagebox.showerror("Error",
                                 f"No se pudo exportar los datos:\n{str(e)}\n")

def exportar_s2(opcion):
    try:

        # Determinar el nombre inicial del archivo basado en la opción
        initial_filename = (
            f"simulacion_estacionario_caso_2_instantaneo"
            if opcion == 'Reacción instantánea Simulador Estacionario'
            else "simulacion_estacionario_caso_2_no_instantaneo"
        )

        # Preguntar al usuario dónde guardar y el tipo de archivo
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=initial_filename,
            filetypes=[("Archivos Excel", "*.xlsx"), ("CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar datos de estado estacionario (Caso 2)"
        )

        if not filepath:
            return

        df = pd.DataFrame({'z [m]': z_points, 'Fracción molar de A (xA)': x_A_profile, 'Fracción molar de B (xB)': x_B_profile})

        if filepath.endswith('.csv'):
            df.to_csv(filepath, index=False)
            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")
        elif filepath.endswith('.xlsx'):
            df.to_excel(filepath, index=False, sheet_name='Concentraciones')
            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")
        else:
            messagebox.showerror("Error", "Formato de archivo no válido. Por favor, elija .csv o .xlsx.")

    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce valores numéricos válidos en los campos.")
    except Exception as e:
        messagebox.showerror("Error al Exportar", f"Ocurrió un error al exportar los datos:\n{str(e)}")

# Función para limpiar la simulación
def limpiar_c2():
    for widget in graf_frame_c2.winfo_children():
        widget.destroy()
    for widget in respuestas_frame_c2.winfo_children():
        widget.destroy()
    
    boton_exportar_c2.grid_forget()
    boton_pausa_c2.grid_forget()
    boton_reanudar_c2.grid_forget()
    # Restablecer valores por defecto
    entry_D_AB_c2.delete(0, 'end')
    entry_x_A0_c2.delete(0, 'end')
    entry_delta_c2.delete(0, 'end')
    entry_N_c2.delete(0, 'end')
    entry_tsim_c2.delete(0, 'end')
    entry_dt_c2.delete(0, 'end')
    entry_tolerancia_c2.delete(0, 'end')
    entry_k.delete(0, 'end')   
    entry_c_2.delete(0, 'end')
    entry_D_AB_c2.insert(0, "5.43e-6")
    entry_x_A0_c2.insert(0, "0.996")
    entry_delta_c2.insert(0, "0.1")
    entry_N_c2.insert(0, "100")
    entry_tsim_c2.insert(0, "0.001")
    entry_dt_c2.insert(0, "1e-7")
    entry_tolerancia_c2.insert(0, "5e-3")
    entry_k.insert(0, "0.75")
    entry_c_2.insert(0, "41.04")

def caso_2(opcion):
    global transitorios, tiempos, x_steady, z, tiempo_convergencia, ani
    boton_exportar_c2.grid(row=1, column=1, pady=5, padx=5, sticky="nsew")
    boton_pausa_c2.grid(row=0, column=0, padx=5, pady=0)
    boton_reanudar_c2.grid(row=0, column=1, padx=5, pady=0)
    
    try:
        # Obtener parámetros del usuario
        D_AB = float(entry_D_AB_c2.get())
        x_A0 = float(entry_x_A0_c2.get())
        delta = float(entry_delta_c2.get()) / 1000  # Convertir mm a m
        N = int(entry_N_c2.get())
        t_sim = float(entry_tsim_c2.get())
        dt_us = float(entry_dt_c2.get())
        tolerancia = float(entry_tolerancia_c2.get())
        k = float(entry_k.get())
        c = float(entry_c_2.get())

        # Validación de parámetros
        if not (0 < x_A0 < 1):
            raise ValueError("x_A0 debe estar entre 0 y 1")
        if N <= 2 or dt_us <= 0 or t_sim <= 0:
            raise ValueError("N debe ser >2, Δt y tiempo de simulación deben ser positivos")
        if k <= 0 or c <= 0:
            raise ValueError("k y c deben ser positivos")

        # Limpiar frames anteriores
        for widget in graf_frame_c2.winfo_children():
            widget.destroy()
        for widget in respuestas_frame_c2.winfo_children():
            widget.destroy()

        # Discretización
        iteraciones = math.ceil(t_sim/dt_us)
        dz = delta / (N - 1)
        z = np.linspace(0, delta, N)

        # SOLUCIÓN ANALÍTICA DE ESTADO ESTACIONARIO
        if opcion == 'Reacción instantánea Simulador Transitorio':
            factor = 1 - (1/2) * x_A0
            x_A_analitico = 2 * (1 - factor ** (1 - z/delta))
        
        elif opcion == 'Reacción no instantánea Simulador Transitorio':
            N_Az_inicial = 1e-6
            N_Az_calculado_array, info, ier, mesg = fsolve(
                lambda N_Az: N_Az - (2 * c * D_AB / delta) * np.log((1 - 0.5 * (N_Az / (k*c))) / (1 - 0.5 * x_A0)),
                N_Az_inicial,
                full_output=True
            )
            if ier != 1:
                raise ValueError(f"No se pudo encontrar N_Az: {mesg}")
            N_Az_calculado = N_Az_calculado_array[0]
            
            x_A_analitico = np.zeros(len(z))
            for i, zi in enumerate(z):
                term1 = (1 - 0.5 * (N_Az_calculado / (k*c)))**(zi / delta)
                term2 = (1 - 0.5 * x_A0)**(1 - (zi / delta))
                x_A_analitico[i] = 2 * (1 - term1 * term2)

        # --- SOLUCIÓN NUMÉRICA DE ESTADO ESTACIONARIO ---
        def solve_ec_diff(x_internal_points):
            F = np.zeros(len(x_internal_points))
            
            if opcion == 'Reacción instantánea Simulador Transitorio':
                x_A_total = np.concatenate(([x_A0], x_internal_points, [0]))
            else:
                x_A_total = np.concatenate(([x_A0], x_internal_points, [x_A_delta_steady]))

            for i in range(1, N - 1):
                denom_safe = 1 - 0.5 * x_A_total[i]
                if abs(denom_safe) < 1e-10:
                    denom_safe = np.sign(denom_safe) * 1e-10 + 1e-10

                dx_dz = (x_A_total[i+1] - x_A_total[i-1]) / (2 * dz)
                d2x_dz2 = (x_A_total[i+1] - 2 * x_A_total[i] + x_A_total[i-1]) / (dz**2)

                term1 = (D_AB / (2 * denom_safe**2)) * dx_dz**2
                term2 = (D_AB / denom_safe) * d2x_dz2

                F[i-1] = term1 + term2

            return F

        # Calcular condición de frontera para estado estacionario
        if opcion == 'Reacción no instantánea Simulador Transitorio':
            def eq_N_Az(N_Az_val):
                numerator = 1 - 0.5 * N_Az_val / (k * c)
                denominator = 1 - 0.5 * x_A0
                if numerator <= 0 or denominator <= 0:
                    return 1e10
                return N_Az_val - (2 * c * D_AB / delta) * np.log(numerator / denominator)

            N_Az_steady = fsolve(eq_N_Az, D_AB * x_A0 / delta)[0]
            x_A_delta_steady = N_Az_steady / (k * c)
        else:
            x_A_delta_steady = 0.0

        # Resolver estado estacionario
        if opcion == 'Reacción instantánea Simulador Transitorio':
            x_steady_init = np.linspace(x_A0, 0, N)[1:-1]
        else:
            x_steady_init = np.linspace(x_A0, x_A_delta_steady, N)[1:-1]

        try:
            x_steady_interior = fsolve(solve_ec_diff, x_steady_init)
            if opcion == 'Reacción instantánea Simulador Transitorio':
                x_steady = np.concatenate(([x_A0], x_steady_interior, [0]))
            else:
                x_steady = np.concatenate(([x_A0], x_steady_interior, [x_A_delta_steady]))
        except Exception as e:
            x_steady = None

        # --- SOLUCIÓN TRANSITORIA CORREGIDA (CRANK-NICOLSON CON FLUJO DINÁMICO) ---
        dt = dt_us
        x_A = np.zeros(N)

        transitorios = []
        tiempos = []
        tiempo_convergencia = None
        perfil_convergido = None

        transitorios.append(x_A.copy())
        tiempos.append(0.0)

        for n in range(iteraciones):
            x_old = x_A.copy()
            
            if opcion == 'Reacción no instantánea Simulador Transitorio':               
                def boundary_equation(x_A_delta_new):
                    # Verificar límites físicos
                    if x_A_delta_new <= 0:
                        return 1e10
                    if x_A_delta_new >= x_A0:
                        return 1e10
                    
                    # Denominador seguro
                    denom = 1 - 0.5 * x_A_delta_new
                    if abs(denom) < 1e-10:
                        denom = np.sign(denom) * 1e-10 + 1e-10

                    flux_diffusive = -D_AB * c * (x_A_delta_new - x_old[-2]) / dz * denom
                    
                    # Flujo reactivo
                    flux_reactive = k * c * x_A_delta_new
                    
                    # Balance: flujo difusivo = flujo reactivo
                    return flux_diffusive - flux_reactive
                

                x_A_delta_new = fsolve(boundary_equation, x_old[-1], xtol=1e-12)[0]
                
                # Verificaciones de estabilidad
                if x_A_delta_new < 0:
                    x_A_delta_new = max(0.0, x_old[-1] * 0.9)
                elif x_A_delta_new > x_A0:
                    x_A_delta_new = min(x_A0 * 0.9, x_old[-1] * 1.1)
                
                # Limitar cambios bruscos para estabilidad numérica
                cambio_max_permitido = 0.1 * x_old[-1] if x_old[-1] > 1e-6 else 0.01 * x_A0
                if abs(x_A_delta_new - x_old[-1]) > cambio_max_permitido:
                    if x_A_delta_new > x_old[-1]:
                        x_A_delta_new = x_old[-1] + cambio_max_permitido
                    else:
                        x_A_delta_new = max(0.0, x_old[-1] - cambio_max_permitido)
                            
            else:
                x_A_delta_new = 0.0  # Reacción instantánea

            # Manejo seguro de denominadores
            x_old_denom_safe = np.where(np.abs(1 - 0.5 * x_old) < 1e-10, 
                                       np.sign(1 - 0.5 * x_old) * 1e-10 + 1e-10, 
                                       1 - 0.5 * x_old)

            # Matrices para sistema tridiagonal
            main_diag = np.zeros(N - 2)
            lower_diag = np.zeros(N - 3)
            upper_diag = np.zeros(N - 3)
            rhs_vector = np.zeros(N - 2)

            for j in range(N - 2):
                i = j + 1  # Mapeo del índice del sistema reducido al índice completo
                
                # Coeficiente efectivo para parte lineal
                coeff_linear_implicit = D_AB / x_old_denom_safe[i]
                alpha = dt / (2 * dz**2) * coeff_linear_implicit

                # Matriz tridiagonal
                main_diag[j] = 1 + 2 * alpha
                if j > 0:
                    lower_diag[j - 1] = -alpha
                if j < (N - 2) - 1:
                    upper_diag[j] = -alpha

                # Término no lineal explícito
                dx_dz_old = (x_old[i+1] - x_old[i-1]) / (2 * dz)
                coeff_nonlinear_explicit = D_AB / (2 * x_old_denom_safe[i]**2)
                rhs_nonlinear_term = dt * coeff_nonlinear_explicit * (dx_dz_old**2)

                # Término lineal explícito
                d2x_dz2_old = (x_old[i+1] - 2 * x_old[i] + x_old[i-1]) / (dz**2)
                rhs_linear_explicit_part = coeff_linear_implicit * dt / 2 * d2x_dz2_old

                # Vector del lado derecho
                rhs_vector[j] = x_old[i] + rhs_nonlinear_term + rhs_linear_explicit_part

                # Aplicar condiciones de frontera
                if i == 1:  # Primer punto interior
                    rhs_vector[j] += alpha * x_A0
                if i == N - 2:  # Último punto interior
                    rhs_vector[j] += alpha * x_A_delta_new  # USAR EL VALOR DINÁMICO

            # Resolver sistema tridiagonal
            ab = np.zeros((3, N - 2))
            ab[0, 1:] = upper_diag
            ab[1, :] = main_diag
            ab[2, :-1] = lower_diag

            x_A_interior = solve_banded((1, 1), ab, rhs_vector)

            # Reconstruir perfil completo con condición de frontera dinámica
            x_A = np.concatenate(([x_A0], x_A_interior, [x_A_delta_new]))

            # Guardar transitorios y verificar convergencia
            if (n+1) % max(1, iteraciones // 50) == 0 or (n+1) == iteraciones or n == 0:
                transitorios.append(x_A.copy())
                tiempos.append((n+1) * dt)

                if x_steady is not None:
                    diff_promedio = np.mean(np.abs(x_A - x_steady))
                    
                    if diff_promedio <= tolerancia and tiempo_convergencia is None:
                        tiempo_convergencia = (n+1) * dt
                        perfil_convergido = x_A.copy()
                        
                        if (n+1) % max(1, iteraciones // 50) != 0 and (n+1) != iteraciones and n != 0:
                            transitorios.append(x_A.copy())
                            tiempos.append((n+1) * dt)

        perfil_final = perfil_convergido if perfil_convergido is not None else x_A.copy()

        # --RESULTADOS--
        if tiempo_convergencia is not None:
            resultado_texto = (
                f"Tipo de reacción: {opcion}\n"
                f"Iteraciones realizadas: {iteraciones}\n"
                f"Convergencia alcanzada en la iteración {tiempo_convergencia/dt:.0f}\n"
                f"Tiempo de convergencia: {tiempo_convergencia:.3e} s\n"
                f"Diferencia entre estado estacionario y transitorio: {diff_promedio:.3e}\n"
                f"Tiempo simulado: {t_sim:.3f} s\n"
                f"Paso temporal (Δt): {dt:.3e} s"
            )
        else:
            resultado_texto = (
                f"Tipo de reacción: {opcion}\n"
                f"Iteraciones realizadas: {iteraciones}\n"
                f"El sistema NO CONVERGE con {iteraciones} iteraciones\na una tolerancia de {tolerancia:.3e}\n"
                f"Diferencia entre estado estacionario y transitorio: {diff_promedio:.3e}\n"
                f"Tiempo simulado: {t_sim:.3f} s\n"
                f"Paso temporal (Δt): {dt:.3e} s"
            )

        respuestas_label = ctk.CTkLabel(
            respuestas_frame_c2,
            text=resultado_texto,
            font=('Consolas', 12),
            justify="left"
        )
        respuestas_label.pack(pady=10)

        # --GRÁFICAS--
        fig, ax = plt.subplots(figsize=(8, 5))
        escala_y = escala_y_seleccionada_2.get()
        escala_x = escala_x_seleccionada_2.get()

        # Aplicar escalas
        if escala_y == "Logarítmica":
            ax.set_yscale('log')
        else:
            ax.set_yscale('linear')

        if escala_x == "Logarítmica":
            ax.set_xscale('log')
        else:
            ax.set_xscale('linear')

        lines = []
        for _ in range(len(transitorios)):
            line, = ax.plot([], [], '--', alpha=0.6)
            lines.append(line)
        
        steady_line_numerico = ax.plot(z * 1000, x_steady, 'r-', linewidth=2, label='Estado estacionario - Sol. Numérica')
        steady_line_analitico = ax.plot(z * 1000, x_A_analitico, 'k.-', linewidth=2, label='Estado estacionario - Sol. Analítica')
        convergido = ax.plot(z * 1000, perfil_final, 'b:', linewidth=4, label=f'Converge a t = {tiempo_convergencia:.4f}s')
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10, verticalalignment='top')

        ax.set_xlabel('Posición z [mm]', fontsize=12)
        ax.set_ylabel('Fracción molar $x_A$', fontsize=12)
        ax.set_title(f'Difusión con Reacción Heterogénea - {opcion}', fontsize=14)
        ax.legend(loc='upper right', fontsize=10, framealpha=0.95)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlim(0, delta * 1000)

        # Ajustar límites Y
        all_data = transitorios + [x_steady]
        min_y_data = min(np.min(d) for d in all_data)
        max_y_data = max(np.max(d) for d in all_data)
        if escala_y == "Logarítmica":
            ax.set_ylim(max(1e-9, min_y_data), max_y_data * 1.1)
        else:
            ax.set_ylim(0, x_A0 * 1.1)

        def animate(i):
            lines[i].set_data(z * 1000, transitorios[i])
            time_text.set_text(f'Tiempo t = {tiempos[i]:.4f} s')
            return (*lines[:i+1], time_text)

        ani = animation.FuncAnimation(fig, animate, frames=len(transitorios), interval=200, blit=True, repeat=True)

        canvas = FigureCanvasTkAgg(fig, master=graf_frame_c2)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, graf_frame_c2)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    except Exception as e:
        messagebox.showerror("Error", f"Error en simulación:\n{str(e)}")

#_______________________________________________________________________________________________________________________________________

#-----------------------CASO 1----------------------DIFUSIÓN PELÍCULA ESTANCADA------------------------------
#_______________________________________________________________________________________________________________________________________

# Configuración específica para Caso 1
frame_c1 = menu.tab("Caso 1")
content_c1 = ctk.CTkFrame(frame_c1)
content_c1.pack(padx=10, pady=5, fill="both", expand=True)

# Frame para las suposiciones
inicio_c1 = ctk.CTkFrame(content_c1)
inicio_c1.pack(padx=10, pady=5, fill="both", expand=True)

#Esquema
esquema_frame = ctk.CTkFrame(inicio_c1, width=int(principal.winfo_screenwidth()*0.3))
esquema_frame.pack(side = 'right', expand = False, padx = 15, pady = (5,5))

# Obtiene el directorio del script actual
script_dir = os.path.dirname(os.path.abspath(__file__))
imagen_path = os.path.join(script_dir, "caso_1.png")

try:
    imagen_pil = Image.open(imagen_path)

    # Crea una versión CTkImage para modo claro y oscuro (puedes usar la misma imagen PIL)
    esquema_ctk_image = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size = (277,600)) # Ajusta el tamaño

    esquema_label = ctk.CTkLabel(esquema_frame, image=esquema_ctk_image, text="")
    esquema_label.pack(padx=10, pady=10)

except FileNotFoundError:
    print(f"Error: No se encontró la imagen en la ruta: {imagen_path}")
except Exception as e:
    print(f"Error al cargar la imagen: {e}")

#Suposiciones 
suposiciones_frame = ctk.CTkFrame(inicio_c1)
suposiciones_frame.pack(side = 'left', fill='both', expand=True, padx=5, pady=5)

# Frame de suposiciones caso 1 
f_caso_1 = ctk.CTkFrame(suposiciones_frame)
f_caso_1.pack( padx=(10,10), pady=10)

sup_caso_1 = ctk.CTkLabel(f_caso_1, 
                        text="Suposiciones para la Difusión a través de una película estancada",
                        font=('Times New Roman', 22),
                        justify="center")
sup_caso_1.pack(pady=(10,10))

desp_caso_1 = ctk.CTkLabel(f_caso_1, 
                            text="Tenemos de un líquido A en la película estancada de B con las siguientes consideraciones:\n\n"
                                "- La solubilidad de B en A es despreciable.\n\n"
                                "- A y B son gases ideales.\n\n"
                                "- La presión y la temperatura del sistema son constantes.\n\n"
                                "- Se supone que la velocidad del gas en z, no depende de la coordenada radial.\n\n"
                                "- El gas B es estacionario y se encuentra “estancado”, es decir, N_Bz=0.",
                            font=('Times New Roman', 20),
                            justify="left")
desp_caso_1.pack(padx=10, pady=10, fill="both", expand=True)

# --- Frame para los controles de la escala de los ejes ---
escala_frame = ctk.CTkFrame(suposiciones_frame)
escala_frame.pack(fill='both', expand=False, padx=20, pady=(10,5))
escala_frame.columnconfigure(0, weight=1)
escala_frame.columnconfigure(1, weight=1)
escala_frame.rowconfigure(0, weight=2)
escala_frame.rowconfigure(1, weight=1)

# --- Controles para la Escala del Eje Y ---
escala_y_label = ctk.CTkLabel(escala_frame, text="Escala Eje Y:")
escala_y_label.grid(row = 0, column = 1, padx=5, pady=(5, 0))

escala_y_opciones = ["Lineal", "Logarítmica"]
escala_y_seleccionada = ctk.StringVar(value="Lineal")
escala_y_menu = ctk.CTkComboBox(escala_frame, values=escala_y_opciones, variable=escala_y_seleccionada)
escala_y_menu.grid(row = 1, column = 1, padx=5, pady=(0, 5))

# --- Controles para la Escala del Eje X ---
escala_x_label = ctk.CTkLabel(escala_frame, text="Escala Eje X:")
escala_x_label.grid(row = 0, column = 0, padx=5, pady=(5, 0))

escala_x_opciones = ["Lineal", "Logarítmica"]
escala_x_seleccionada = ctk.StringVar(value="Lineal")
escala_x_menu = ctk.CTkComboBox(escala_frame, values=escala_x_opciones, variable=escala_x_seleccionada)
escala_x_menu.grid(row = 1, column = 0, padx=5, pady=(0, 5))

# Frame de simulación (oculto inicialmente)
simulacion_frame = ctk.CTkFrame(content_c1)
simulacion_frame.pack_forget()

# Configuración inicial
solver_frame_c1 = ctk.CTkFrame(content_c1)
solver_frame_c1.pack_forget()

def mostrar_solver():
    global entry_D_AB_s1, entry_x_A1_s1, entry_x_A2_s1, entry_z1_s1, entry_z2_s1, entry_At_s1, entry_c_s1, resultados_frame_s1, graf_frame_s1, toolbar_frame_s1, boton_exportar_s1
    # Ocultar frame de inicio y configurar solver
    inicio_c1.pack_forget()
    solver_frame_c1.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Limpiar frame existente
    for widget in solver_frame_c1.winfo_children():
        widget.destroy()
    
    # Frame de parámetros (30% del ancho)
    izq_frame_s1 = ctk.CTkFrame(solver_frame_c1, width=int(principal.winfo_screenwidth()*0.3))
    izq_frame_s1.pack(side='left', fill='both', padx=5, pady=5)

    # Frame de la gráfica (70% del ancho)
    right_container_s1 = ctk.CTkFrame(solver_frame_c1)
    right_container_s1.pack(side='right', fill='both', expand=True, padx=5, pady=5)

    # ----------------------------
    # Frame del gráfico 
    # ----------------------------
    graf_frame_s1 = ctk.CTkFrame(right_container_s1)
    graf_frame_s1.pack(fill='both', expand=True, padx=5, pady=5)

    # Frame para la barra de herramientas
    toolbar_frame_s1 = ctk.CTkFrame(right_container_s1, height=40)
    toolbar_frame_s1.pack(fill='x', padx=5, pady=(0,5))
      
    # ----------------------------
    # Frame de parámetros (arriba)
    # ----------------------------
    param_frame_s1 = ctk.CTkFrame(izq_frame_s1)
    param_frame_s1.pack(fill='both', expand=True, padx=5, pady=5)

    resultados_frame_s1 = ctk.CTkFrame(izq_frame_s1)
    resultados_frame_s1.pack(fill='both', padx=5, pady=5, expand=False)  # Cambiado de grid a pack

    # Campos de entrada
    entry_D_AB_s1 = crear_entry(param_frame_s1, 0, "Coeficiente de difusión (D_AB) [m²/s]:", "8.8e-6")
    entry_x_A1_s1 = crear_entry(param_frame_s1, 1, "Fracción molar en z1 (x_A1):", "0.152")
    entry_x_A2_s1 = crear_entry(param_frame_s1, 2, "Fracción molar en z2 (x_A2):", "0")
    entry_z1_s1 = crear_entry(param_frame_s1, 3, "z1 [m]:", "0.2")
    entry_z2_s1 = crear_entry(param_frame_s1, 4, "z2 [m]:", "5")
    entry_At_s1 = crear_entry(param_frame_s1, 5, "Área Transversal [m²]:", "3.1416")
    entry_c_s1 = crear_entry(param_frame_s1, 6, "Concentración del sistema [mol/m³]:", "39.6")

    # Botones de control
    button_frame_s1 = ctk.CTkFrame(izq_frame_s1)
    button_frame_s1.pack(fill='x', padx=5, pady=(5, 10), expand=False)  # Cambiado de grid a pack
    
    # Configurar grid para los botones
    button_frame_s1.columnconfigure(0, weight=1)
    button_frame_s1.columnconfigure(1, weight=1)
    button_frame_s1.columnconfigure(2, weight=1)
    button_frame_s1.rowconfigure(0, weight=1)
    button_frame_s1.rowconfigure(1, weight=1)

    boton_simular_s1 = ctk.CTkButton(
        button_frame_s1, 
        text="Simular", 
        command=solver_1, 
        height=40, 
        font=('Arial', 14)
    )
    boton_simular_s1.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

    boton_borrar_s1 = ctk.CTkButton(
        button_frame_s1, 
        text="Borrar", 
        command=limpiar_s1, 
        fg_color="#d9534f", 
        hover_color="#c9302c", 
        height=40, 
        font=('Arial', 14)
    )
    boton_borrar_s1.grid(row=0, column=1, pady=5, padx=5, sticky="nsew")

    boton_volver_s1 = ctk.CTkButton(
        button_frame_s1,
        text="Volver",
        command=volver_inicio_c1,
        fg_color="#6c757d",
        hover_color="#5a6268",
        height=40,
        font=('Arial', 14)
    )
    boton_volver_s1.grid(row=0, column=2, pady=5, padx=5, sticky="nsew")

    boton_exportar_s1 = ctk.CTkButton(
        button_frame_s1,
        text="Exportar Datos",
        command=exportar_s1,
        fg_color="#27ae60",  # Cambiado a verde para mejor identificación
        hover_color="#219653",
        height=40,
        font=('Arial', 14)
    )
    boton_exportar_s1.grid_forget()

def solver_1():
    global entry_x_A1_s1, entry_x_A2_s1
    boton_exportar_s1.grid(row=1, column=1, pady=5, padx=5, sticky="nsew")
    try:
        # Obtención de parámetros introducidos por el usuario
        D_AB = float(entry_D_AB_s1.get())   # Coeficiente de difusión [m²/s]
        x_A1 = float(entry_x_A1_s1.get())   # Fracción molar de A en z1 (x_A1)
        x_A2 = float(entry_x_A2_s1.get())   #Fracción Mmolar de A en z2 (x_A2)
        z1 = float(entry_z1_s1.get())     # Posición z1 [m]
        z2 = float(entry_z2_s1.get())     # Posición z2 [m]
        c = float(entry_c_s1.get())       # Concentración total [mol/m³]
        A_transversal = float(entry_At_s1.get())   # Área transversal [m²]

        # Validación de parámetros
        if not (0 < x_A1 < 1):
            raise ValueError("Las fracciones molares deben estar entre 0 y 1")
        if z1 >= z2:
            raise ValueError("z1 debe ser menor que z2")
        if D_AB <= 0 or c <= 0 or A_transversal <= 0:
            raise ValueError("D_AB, c y A_transversal deben ser positivos")

        # Limpiar frames anteriores
        for widget in graf_frame_s1.winfo_children():
            widget.destroy()
        for widget in resultados_frame_s1.winfo_children():
            widget.destroy()

        x_B1 = 1 - x_A1
        x_B2 = 1 - x_A2

        # 1. Cálculo de la media logarítmica de x_B (Ec. 18.2-13)
        x_B_media = (x_B2 - x_B1) / np.log(x_B2 / x_B1)

        # 2. Cálculo de N_Az (Ec. 18.2-14)
        N_Az = (c * D_AB / (z2 - z1)) * np.log(x_B2 / x_B1)

        # 3. Cálculo de W_A (flujo másico)
        W_A = N_Az * A_transversal   # [mol/s]

        # 4. Perfil de concentración (Ec. 18.2-11)
        z_points = np.linspace(z1, z2, 10000)
        x_A_profile = 1 - (1 - x_A1) * ((1 - x_A2) / (1 - x_A1))**((z_points - z1)/(z2 - z1))
        x_B_profile = 1 - x_A_profile

        # Mostrar resultados en el frame de respuestas
        resultado_texto = (
            f"Resultados del cálculo:\n"
            f"1. Fracción molar media de B (x_B,media): {x_B_media:.2f}\n"
            f"2. Densidad de flujo molar (N_Az): {N_Az:.2e} mol/(m²·s)\n"
            f"3. Velocidad de transferencia (W_A): {W_A:.2e} mol/s\n\n")

        respuestas_label = ctk.CTkLabel(
            resultados_frame_s1,
            text=resultado_texto,
            font=('Consolas', 12),
            justify="left"
        )
        respuestas_label.pack(pady=10)

        # Crear gráficos
        fig, ax1 = plt.subplots(figsize=(9, 6.5))

        # Aplicar la escala al eje Y
        escala_y_s1 = escala_y_seleccionada.get()
        if escala_y_s1 == "Logarítmica":
            ax1.set_yscale('log')
        else:
            ax1.set_yscale('linear')

        # Aplicar la escala al eje X
        escala_x_s1 = escala_x_seleccionada.get()
        if escala_x_s1 == "Logarítmica":
            ax1.set_xscale('log')
        else:
            ax1.set_xscale('linear')

        # Gráfico 1: Perfil de concentración de A
        ax1.plot(z_points, x_A_profile, 'b-', linewidth=2, label='$x_A$')
        ax1.plot(z_points, x_B_profile, 'r-', linewidth=2, label='$x_B$')
        ax1.set_xlabel('Posición z [m]', fontsize=12)
        ax1.set_ylabel('Fracción molar', fontsize=12)
        ax1.set_title('Perfiles de concentración (Estado Estacionario)', fontsize=14)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, linestyle='--', alpha=0.6)
        ax1.set_xlim(z1, z2)
        ax1.set_ylim(0, 1.1) # Ajuste para asegurar que las curvas estén dentro del rango

        plt.tight_layout()

        # Mostrar gráficos en la interfaz
        canvas = FigureCanvasTkAgg(fig, master=graf_frame_s1)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, graf_frame_s1)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    except Exception as e:
        messagebox.showerror("Error", f"Error en simulación:\n{str(e)}")

def mostrar_sim():
    global entry_D_AB, entry_dt, entry_z1, entry_z2, entry_tolerancia, entry_N, entry_x_A1, entry_x_A2, entry_t_sim
    global graf_frame, main_frame, izq_frame, respuestas_frame, param_frame, boton_exportar, boton_pausa, boton_reanudar, botones_anim

    # Ocultar frames de suposiciones y la barra de opciones
    suposiciones_frame.pack_forget()
    inicio_c1.pack_forget()
    botones_inicio.pack_forget()
    
    # Mostrar frame de simulación
    simulacion_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Configurar título dinámico
    for widget in simulacion_frame.winfo_children():
        widget.destroy()
      
    # Main frame para la interfaz de simulación
    main_frame = ctk.CTkFrame(simulacion_frame)
    main_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Frame de parámetros (30% del ancho)
    izq_frame = ctk.CTkFrame(main_frame, width=int(principal.winfo_screenwidth()*0.3))
    izq_frame.pack(side='left', fill='y', padx=5, pady=5)
    
    # Frame de la gráfica (70% del ancho)
    right_container = ctk.CTkFrame(main_frame)
    right_container.pack(side='right', fill='both', expand=True, padx=5, pady=5)

    botones_anim = ctk.CTkFrame(right_container)  
    botones_anim.pack(fill='both', expand=False, padx=5, pady=(0,0))
    botones_anim.columnconfigure(0, weight=1)
    botones_anim.columnconfigure(1, weight=1)

    # Contenedor para gráfica
    graf_frame = ctk.CTkFrame(right_container)
    graf_frame.pack(fill='both', expand=True, padx=5, pady=5)        
      
    # Controles en izq_frame_c2
    param_frame = ctk.CTkScrollableFrame(izq_frame)
    param_frame.pack(fill='both', expand=True, padx=10, pady=(5,5))
    
    # Frame para respuestas
    respuestas_frame = ctk.CTkFrame(izq_frame)
    respuestas_frame.pack(fill='both', padx=10, pady=(5,5), expand = False)
    
    # Campos de entrada para el caso 1
    entry_D_AB = crear_entry(param_frame, 0, "Coeficiente de difusión (D_AB) [m²/s]:", "8.8e-6")
    entry_x_A1 = crear_entry(param_frame, 1, "Fracción molar inicial (x_A1):", "0.152")
    entry_x_A2 = crear_entry(param_frame, 2, "Fracción molar final (x_A2):", "0")
    entry_z1 = crear_entry(param_frame, 3, "z1 [m]:", "0.2")
    entry_z2 = crear_entry(param_frame, 4, "z1 [m]:", "5")
    entry_N = crear_entry(param_frame, 5, "Número de puntos (N):", "100")
    entry_dt = crear_entry(param_frame, 6, "Δt de simulación [s]:", "500")
    entry_t_sim = crear_entry(param_frame, 7, "Tiempo de simulación [s]:", "1100000")    
    entry_tolerancia = crear_entry(param_frame, 8, "Tolerancia:", "1e-3")

    # Botones de control
    button_frame = ctk.CTkFrame(izq_frame)
    button_frame.pack(fill='both', expand=False, padx=5, pady=(5,0))
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)
    button_frame.rowconfigure(0, weight=1)
    button_frame.rowconfigure(1, weight=1)

    boton_simular = ctk.CTkButton(
        button_frame, 
        text="Simular", 
        command=caso_1, 
        height=40, 
        font=('Arial', 14)
    )
    boton_simular.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

    boton_borrar = ctk.CTkButton(
        button_frame, 
        text="Borrar", 
        command=limpiar_c1, 
        fg_color="#d9534f", 
        hover_color="#c9302c", 
        height=40, 
        font=('Arial', 14)
    )
    boton_borrar.grid(row=0, column=1, pady=5, padx=5, sticky="nsew")

    boton_volver = ctk.CTkButton(
        button_frame,
        text="Volver",
        command=volver_inicio_c1,
        fg_color="#6c757d",
        hover_color="#5a6268",
        height=40,
        font=('Arial', 14)
    )
    boton_volver.grid(row=0, column=2, pady=5, padx=5, sticky="nsew")

    boton_exportar = ctk.CTkButton(
        button_frame,
        text="Exportar Datos",
        command=exportar_c1,
        fg_color="#27ae60",  # Cambiado a verde para mejor identificación
        hover_color="#219653",
        height=40,
        font=('Arial', 14)
    )
    boton_exportar.grid_forget()

        # En la parte de la interfaz donde creas los controles
    boton_pausa = ctk.CTkButton(botones_anim, text="⏸️", command=lambda: ani.event_source.stop(), fg_color="#000000", 
        hover_color="#000000", 
        height=40, 
        font=('Arial', 14))
    boton_pausa.grid_forget()

    boton_reanudar = ctk.CTkButton(botones_anim, text="▶️", command=lambda: ani.event_source.start(), fg_color="#000000",  
        hover_color="#000000",
        height=40,
        font=('Arial', 14)
    )
    boton_reanudar.grid_forget()

def exportar_c1():
    try:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx"), ("CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar datos de simulación",
            initialfile="simulacion_transitorio_caso_1.xlsx"
        )
        if not filepath:
            return

        # Obtener la tolerancia desde la interfaz
        try:
            tolerancia = float(entry_tolerancia.get())
        except:
            tolerancia = None  # Si no se puede obtener, se manejará más adelante

        if filepath.endswith('.csv'):
            # CSV para casos muy grandes (una sola hoja)
            df_csv = pd.DataFrame({'z [m]': z, 'Estado Estacionario': x_steady})
            for t_csv, perfil_csv in zip(tiempos, transitorios):
                column_name_csv = f't={t_csv:.2f}s'
                # Añadir distintivo si es el tiempo de convergencia
                if tiempo_convergencia is not None and abs(t_csv - tiempo_convergencia) < 1e-9:  # Comparación de flotantes
                    column_name_csv += ' (Convergencia)'
                df_csv[column_name_csv] = perfil_csv
            df_csv.to_csv(filepath, index=False)
            
            # Para CSV no podemos incluir múltiples hojas, así que añadimos
            # un archivo adicional para los datos de convergencia
            if filepath:
                convergence_filepath = filepath.replace('.csv', '_convergencia.csv')
                # Calcular diferencias para cada perfil transitorio
                diffs = []
                convergence_status = []
                for perfil in transitorios:
                    diff = np.mean(np.abs(perfil - x_steady))
                    diffs.append(diff)
                    if tolerancia is not None:
                        convergence_status.append("CONVERGE" if diff <= tolerancia else "NO CONVERGE")
                    else:
                        convergence_status.append("N/A")
                
                df_convergence = pd.DataFrame({
                    'Tiempo [s]': tiempos,
                    'Diferencia promedio': diffs,
                    'Tolerancia': [tolerancia] * len(tiempos) if tolerancia is not None else ["N/A"] * len(tiempos),
                    'Estado': convergence_status
                })
                df_convergence.to_csv(convergence_filepath, index=False)
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}\ny\n{convergence_filepath}")
        else:
            # Excel con organización por hojas optimizada
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja de estado estacionario
                pd.DataFrame({
                    'Posición z [m]': z,
                    'Fracción molar x_A': x_steady
                }).to_excel(writer, sheet_name='Estacionario', index=False)
                
                # Hoja(s) consolidada(s) de transitorios con numeración optimizada
                df_trans_excel_current_sheet = pd.DataFrame({'z [m]': z})
                excel_sheet_counter = 1  # Contador para los nombres de hoja: Transitorios_1, Transitorios_2, ...

                for i, (t_excel, perfil_excel) in enumerate(zip(tiempos, transitorios)):
                    column_header_excel = f't={t_excel:.2f}s'
                    # Añadir distintivo si es el tiempo de convergencia
                    if tiempo_convergencia is not None and abs(t_excel - tiempo_convergencia) < 1e-9:  # Comparación de flotantes
                        column_header_excel += ' (Convergencia)'
                    
                    df_trans_excel_current_sheet[column_header_excel] = perfil_excel

                    if (i + 1) % 50 == 0:
                        df_trans_excel_current_sheet.to_excel(writer, sheet_name=f'Transitorios_{excel_sheet_counter}', index=False)
                        # Resetear el DataFrame para la siguiente hoja, comenzando con la columna 'z [m]'
                        df_trans_excel_current_sheet = pd.DataFrame({'z [m]': z})
                        excel_sheet_counter += 1  # Incrementar para la siguiente hoja
                

                if len(df_trans_excel_current_sheet.columns) > 1:
                    df_trans_excel_current_sheet.to_excel(writer, sheet_name=f'Transitorios_{excel_sheet_counter}', index=False)
                
                # NUEVA HOJA: Información de convergencia
                # Calcular diferencias para cada perfil transitorio
                diffs = []
                convergence_status = []
                for perfil in transitorios:
                    diff = np.mean(np.abs(perfil - x_steady))
                    diffs.append(diff)
                    if tolerancia is not None:
                        convergence_status.append("CONVERGE" if diff <= tolerancia else "NO CONVERGE")
                    else:
                        convergence_status.append("N/A")
                
                df_convergence = pd.DataFrame({
                    'Tiempo [s]': tiempos,
                    'Diferencia promedio': diffs,
                    'Tolerancia': [tolerancia] * len(tiempos) if tolerancia is not None else ["N/A"] * len(tiempos),
                    'Estado': convergence_status
                })
                
                # Añadir una fila de resumen final
                if tiempo_convergencia is not None:
                    resumen = pd.DataFrame({
                        'Tiempo [s]': ["RESUMEN"],
                        'Diferencia promedio': ["---"],
                        'Tolerancia': [tolerancia if tolerancia is not None else "N/A"],
                        'Estado': [f"Convergencia alcanzada en t={tiempo_convergencia:.4f}s"]
                    })
                else:
                    resumen = pd.DataFrame({
                        'Tiempo [s]': ["RESUMEN"],
                        'Diferencia promedio': ["---"],
                        'Tolerancia': [tolerancia if tolerancia is not None else "N/A"],
                        'Estado': ["No se alcanzó convergencia"]
                    })
                
                # Concatenar el DataFrame original con la fila de resumen
                df_convergence = pd.concat([df_convergence, resumen], ignore_index=True)
                
                # Exportar a la hoja de Excel
                df_convergence.to_excel(writer, sheet_name='Convergencia', index=False)

            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")

    except Exception as e:
        if isinstance(e, NameError):
             messagebox.showerror("Error de Variable", 
                f"No se pudo exportar: una variable necesaria (como 'z', 'tiempos', etc.) no fue definida.\n"
                f"Asegúrate de que la simulación ('caso_1') se haya ejecutado primero y haya definido las variables globales.\nDetalle: {str(e)}")
        else:
            messagebox.showerror("Error", 
                f"No se pudo exportar los datos:\n{str(e)}\n")

def exportar_s1():
    try:
        # Obtener los parámetros de entrada (solo para generar los puntos z y concentraciones)
        z1 = float(entry_z1_s1.get())
        z2 = float(entry_z2_s1.get())
        x_A1 = float(entry_x_A1_s1.get())
        x_A2 = float(entry_x_A2_s1.get())

        # Obtener los datos del perfil de concentración
        z_points = np.linspace(z1, z2, 10000)
        x_A_profile = 1 - (1 - x_A1) * ((1 - x_A2) / (1 - x_A1))**((z_points - z1)/(z2 - z1))
        x_B_profile = 1 - x_A_profile

        # Preguntar al usuario dónde guardar y el tipo de archivo
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile="estado_estacionario_caso_1",
            filetypes=[("Archivos Excel", "*.xlsx"), ("CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar datos de estado estacionario"
        )

        if filepath:
            df = pd.DataFrame({'z [m]': z_points, 'Fracción molar de A (xA)': x_A_profile, 'Fracción molar de B (xB)': x_B_profile})

            if filepath.endswith('.csv'):
                df.to_csv(filepath, index=False)
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")
            elif filepath.endswith('.xlsx'):
                df.to_excel(filepath, index=False, sheet_name='Concentraciones')
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")
            else:
                messagebox.showerror("Error", "Formato de archivo no válido. Por favor, elija .csv o .xlsx.")

    except Exception as e:
        messagebox.showerror("Error al Exportar", f"Ocurrió un error al exportar los datos:\n{str(e)}")

def volver_inicio_c1():
    # Ocultar frame de simulación
    solver_frame_c1.pack_forget()
    simulacion_frame.pack_forget()
    inicio_c1.pack(padx=10, pady=5, fill="both", expand=True)
    suposiciones_frame.pack(fill='both', expand=True, padx=5, pady=5)
    botones_inicio.pack(fill='both', expand=True, padx=20, pady=20)

def limpiar_c1():
    for widget in graf_frame.winfo_children():
        widget.destroy()
    for widget in respuestas_frame.winfo_children():
        widget.destroy()
   
    boton_exportar.grid_forget()
    boton_pausa.grid_forget()
    boton_reanudar.grid_forget()
    entry_D_AB.delete(0, 'end')
    entry_x_A1.delete(0, 'end')
    entry_x_A2.delete(0, 'end')
    entry_z1.delete(0, 'end')
    entry_z2.delete(0, 'end')
    entry_N.delete(0, 'end')
    entry_dt.delete(0, 'end')
    entry_tolerancia.delete(0, 'end')
    entry_t_sim.delete(0, 'end')
    entry_D_AB.insert(0, "8.8e-6")
    entry_x_A1.insert(0, "0.152")
    entry_x_A2.insert(0, "0")
    entry_z1.insert(0, "0.2")
    entry_z2.insert(0, "5")
    entry_N.insert(0, "100")
    entry_dt.insert(0, "500")
    entry_tolerancia.insert(0, "1e-3")
    entry_t_sim.insert(0, "1100000")

def limpiar_s1():
    for widget in graf_frame_s1.winfo_children():
        widget.destroy()
    for widget in toolbar_frame_s1.winfo_children():
        widget.destroy()
    for widget in resultados_frame_s1.winfo_children():
        widget.destroy()
    boton_exportar_s1.grid_forget()
    entry_D_AB_s1.delete(0, 'end')
    entry_x_A1_s1.delete(0, 'end')
    entry_x_A2_s1.delete(0, 'end')
    entry_z1_s1.delete(0, 'end')
    entry_z2_s1.delete(0, 'end')
    entry_c_s1.delete(0, 'end')
    entry_At_s1.delete(0, 'end')
    entry_D_AB_s1.insert(0, "8.8e-6")
    entry_x_A1_s1.insert(0, "0.152")
    entry_x_A2_s1.insert(0, "0.0")
    entry_z1_s1.insert(0, "0.2")
    entry_z2_s1.insert(0, "5")
    entry_c_s1.insert(0, "39.6")
    entry_At_s1.insert(0, "3.1416")

def caso_1():
    global transitorios, tiempos, x_steady, z, tiempo_convergencia, ani
    boton_exportar.grid(row=1, column=1, pady=5, padx=5, sticky="nsew")
    boton_pausa.grid(row = 0, column = 0, padx=5, pady=0)
    boton_reanudar.grid(row = 0, column = 1, padx=5, pady=0)

    try:
# Obtener parámetros introducidos por el usuario
        D_AB = float(entry_D_AB.get())
        x_A1 = float(entry_x_A1.get())
        x_A2 = float(entry_x_A2.get())
        z1 = float(entry_z1.get())
        z2 = float(entry_z2.get())
        t_sim = float(entry_t_sim.get())
        N = int(entry_N.get())
        dt_us = float(entry_dt.get())
        tolerancia = float(entry_tolerancia.get())

        # Validación de parámetros
        if not (0 < x_A1 < 1):
            raise ValueError("x_A1 debe estar entre 0 y 1")
        if not (0 <= x_A2 < 1):
            raise ValueError("x_A2 debe estar entre 0 y 1")
        if N <= 2 or dt_us <= 0 or t_sim <= 0: # N debe ser > 2 para dz válido
            raise ValueError("N debe ser >2, Δt y tiempo de simulación deben ser positivos")

        # limpiar_c1 frames anteriores
        for widget in graf_frame.winfo_children():
            widget.destroy()
        for widget in respuestas_frame.winfo_children():
            widget.destroy()

        # 2. Discretización
        iteraciones = math.ceil(t_sim/dt_us)
        dz = (z2 - z1) / (N - 1)
        z = np.linspace(z1, z2, N)
        
        #SOLUCIÓN ANALÍTICA ESTADO ESTACIONARIO (tal como la tienes)
        x_A_analitica = 1 - (1 - x_A1) * ((1 - x_A2) / (1 - x_A1))**((z - z1)/(z2 - z1))

        #SOLUCIÓN NUMÉRICA ESTADO ESTACIONARIO (tal como la tienes)
        def solve_ec_diff(x):
            F = np.zeros(N - 2)
            x_A_total = np.concatenate(([x_A1], x, [x_A2]))
            for i in range(1, N - 1):
                denom1 = (1 - x_A_total[i])**2
                denom2 = (1 - x_A_total[i])
                
                if abs(denom1) < 1e-10: denom1 = 1e-10
                if abs(denom2) < 1e-10: denom2 = 1e-10
                
                dx_dz = (x_A_total[i+1] - x_A_total[i-1]) / (2 * dz)
                dx2_dz2 = (x_A_total[i+1] - 2 * x_A_total[i] + x_A_total[i-1]) / (dz**2)
                
                term_nolineal = (1 / denom1) * (dx_dz**2)
                term_lineal = (1 / denom2) * dx2_dz2

                F[i-1] = term_nolineal + term_lineal
            return F

        initial_guess_steady = np.linspace(x_A1, x_A2, N)[1:-1]
        try:
            x_steady_interior = fsolve(solve_ec_diff, initial_guess_steady)
            x_steady = np.concatenate(([x_A1], x_steady_interior, [x_A2]))
        except Exception as e:
            x_steady = None


        # --- SOLUCIÓN NUMÉRICA DE ESTADO TRANSITORIO (CRANK-NICOLSON) ---
        dt = dt_us 
        iteraciones = math.ceil(t_sim / dt)
        x_A = np.zeros(N)
        # Condición inicial: perfil de ceros, pero con las condiciones de frontera aplicadas
        x_A[0], x_A[-1] = x_A1, x_A2

        transitorios = []
        tiempos = []
        tiempo_convergencia = None
        perfil_convergido = None

        transitorios.append(x_A.copy())
        tiempos.append(0.0)

        for n in range(iteraciones):
            x_old = x_A.copy() 
            
            # Asegurarse de que los denominadores no sean cero o muy cercanos a cero para x_old
            x_old_denom_safe = np.where(np.abs(1 - x_old) < 1e-10, np.sign(1 - x_old) * 1e-10 + 1e-10, 1 - x_old) # Añadido 1e-10 para asegurar que no sea 0 si sign es 0

            main_diag = np.zeros(N - 2)
            lower_diag = np.zeros(N - 3)
            upper_diag = np.zeros(N - 3)
            rhs_vector = np.zeros(N - 2)

            for j in range(N - 2):
                i = j + 1 # Mapeo del índice del sistema reducido (j) al índice de la malla completa (i)
                coeff_linear_implicit = D_AB / x_old_denom_safe[i]
                alpha = dt / (2 * dz**2) * coeff_linear_implicit
                
                main_diag[j] = 1 + 2 * alpha 
                if j > 0:
                    lower_diag[j - 1] = -alpha 
                if j < (N - 2) - 1:
                    upper_diag[j] = -alpha 
               
                dx_dz_old = (x_old[i+1] - x_old[i-1]) / (2 * dz)
                
                # D_AB / (1-x_old[i])**2 * (dx_dz_old)**2
                coeff_nonlinear_explicit = D_AB / (x_old_denom_safe[i])**2 
                
                rhs_nonlinear_term = dt * coeff_nonlinear_explicit * (dx_dz_old)**2
                # alpha * (x_old[i+1] - 2*x_old[i] + x_old[i-1])
                d2x_dz2_old = (x_old[i+1] - 2 * x_old[i] + x_old[i-1]) / (dz**2)
                rhs_linear_explicit_part = (D_AB / x_old_denom_safe[i]) * dt / 2 * d2x_dz2_old # Esto es alpha_val * 2 * d2x_dz2_old * dz**2 / D_eff_linear_old

                rhs_vector[j] = x_old[i] + rhs_nonlinear_term + rhs_linear_explicit_part
                
                if i == 1: # Si es el primer punto interior (j=0)
                    rhs_vector[j] += alpha * x_A1 
                if i == N - 2: # Si es el último punto interior (j=N-3)
                    rhs_vector[j] += alpha * x_A2 
            
            ab = np.zeros((3, N - 2)) 
            ab[0, 1:] = upper_diag
            ab[1, :] = main_diag
            ab[2, :-1] = lower_diag

            x_A_interior = solve_banded((1, 1), ab, rhs_vector)
            
            x_A = np.concatenate(([x_A1], x_A_interior, [x_A2]))

            # Sección de guardado de transitorios y verificación de convergencia
            if (n+1) % max(1,iteraciones // 50) == 0 or (n+1) == iteraciones or n == 0:
                transitorios.append(x_A.copy())
                tiempos.append((n+1) * dt)

                if x_steady is not None:
                    diff_promedio = np.mean(np.abs(x_A - x_steady)) 
                    
                    if diff_promedio <= tolerancia and tiempo_convergencia is None:
                        tiempo_convergencia = (n+1) * dt
                        perfil_convergido = x_A.copy()
                        
                        if (n+1) % max(1,iteraciones // 50) != 0 and (n+1) != iteraciones and n != 0:
                            transitorios.append(x_A.copy())
                            tiempos.append((n+1) * dt)
                                    
        perfil_final = perfil_convergido if perfil_convergido is not None else x_A.copy()
       
        #--RESULTADOS--

        if tiempo_convergencia is not None:
            resultado_texto = (
                f"Iteraciones realizadas: {iteraciones}\n"
                f"Convergencia alcanzada en la iteración {tiempo_convergencia/dt:.0f}\n"
                f"Tiempo de convergencia: {format_time(tiempo_convergencia)}\n"
                f"Diferencia entre estado estacionario y transitorio: {diff_promedio:.3e}\n"
                f"Tiempo simulado: {format_time(t_sim)} - {t_sim:.3f} s\n"
                f"Paso temporal (Δt): {format_time(dt)} - {dt:.3f} s" 
            )
        else:
            resultado_texto = (
                f"Iteraciones realizadas: {iteraciones}\n"
                f"El sistema NO CONVERGE con {iteraciones} iteraciones\na una tolerancia de {tolerancia:.3e}\n"
                f"Diferencia entre estado estacionario y transitorio: {diff_promedio:.2e}\n"
                f"Tiempo simulado: {format_time(t_sim)} - {t_sim:.3f} s\n"
                f"Paso temporal (Δt): {format_time(dt)} - {dt:.3f} s"
            )

        respuestas_label = ctk.CTkLabel(
            respuestas_frame,
            text=resultado_texto,
            font=('Consolas', 12),
            justify="left"
        )
        respuestas_label.pack(pady=10)

                #--GRÁFICAS--

        fig, ax = plt.subplots(figsize=(8, 5))
        escala_y = escala_y_seleccionada.get()
        escala_x = escala_x_seleccionada.get()

        # Aplicar la escala al eje Y
        if escala_y == "Logarítmica":
            ax.set_yscale('log')
        else:
            ax.set_yscale('linear')

        # Aplicar la escala al eje X
        if escala_x == "Logarítmica":
            ax.set_xscale('log')
        else:
            ax.set_xscale('linear')

        lines = []
        for _ in range(len(transitorios)):
            line, = ax.plot([], [], '--', alpha=0.6)
            lines.append(line)
        steady_line_num = ax.plot(z, x_steady, 'r-', linewidth=2, label='Estado estacionario - Sol. Numérica')
        steady_line_analitic = ax.plot(z, x_A_analitica, 'k.-', linewidth=2, label='Estado estacionario - Sol. Analítica')
        convergido = ax.plot(z, perfil_final, 'b:', linewidth = 4, label = f'Converge a t = {tiempo_convergencia}s')
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10, verticalalignment='top')

        ax.set_xlabel('Posición z [m]', fontsize=12)
        ax.set_ylabel('Fracción molar $x_A$', fontsize=12)
        ax.set_title(f'Difusión en Película Estancada ($x_A1$={x_A1})', fontsize=14)
        ax.legend(loc='upper right', fontsize=10, framealpha=0.95)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlim(z1, z2)

        # Ajustar los límites del eje Y considerando la escala
        all_data = transitorios + [x_steady]
        min_y_data = min(np.min(d) for d in all_data)
        max_y_data = max(np.max(d) for d in all_data)
        if escala_y == "Logarítmica":
            ax.set_ylim(max(1e-9, min_y_data), max_y_data * 1.1)
        else:
            ax.set_ylim(0, x_A1 * 1.1)

        def animate(i):
            lines[i].set_data(z, transitorios[i])
            time_text.set_text(f'Tiempo t = {tiempos[i]:.2f} s')
            return (*lines[:i+1], time_text)

        ani = animation.FuncAnimation(fig, animate, frames=len(transitorios), interval=200, blit=True, repeat=True)

        canvas = FigureCanvasTkAgg(fig, master=graf_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, graf_frame)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    except Exception as e:
        messagebox.showerror("Error", f"Error en simulación:\n{str(e)}")

# Frame para botones de opciones
botones_inicio = ctk.CTkFrame(suposiciones_frame)
botones_inicio.pack(fill='both', expand=True, padx=20, pady=20)
botones_inicio.columnconfigure(0, weight=3)
botones_inicio.columnconfigure(1, weight=3)
botones_inicio.rowconfigure(0, weight=3)

#Botones para usuario
boton_simulador = ctk.CTkButton(botones_inicio, text="Simulador Gráfico Transitorio", command=mostrar_sim, height=80, font=('Arial', 20))
boton_simulador.grid(row = 0, column = 0, pady=15, padx = 5)

boton_solver= ctk.CTkButton(botones_inicio, text="Solver Estado Estacionario", command=mostrar_solver, height=80, font=('Arial', 20))
boton_solver.grid(row = 0, column = 1, pady=15, padx = 5)

principal.mainloop()