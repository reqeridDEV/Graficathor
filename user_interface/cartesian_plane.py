import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from core.calculate_line_direction.calculate_line_direction import CalculateLineDirection
from core.calculate_slope.calculate_slope import CalculateSlope
from core.dda_line.dda_line import DDALinea
import csv
from models.triangle_model import TriangleModel
from core.calculate_triangle.triangle import Triangle


class UltimateLineVisualizer:
    """Visualizador avanzado de líneas y triángulos con algoritmo DDA"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Graficathor")
        self.root.geometry("1300x850")
        self.root.configure(background='#171717')
        
        self.dark_mode = False
        self.triangle_mode = False
        
        self._setup_color_palette()
        self._setup_styles()
        self._setup_ui()

    def _setup_color_palette(self):
        """Define la paleta de colores de la aplicación"""
        self.PALETTE = {
            'celeste': "#8FDDFF",
            'accent': '#D94E5A',
            'light': "#2E2E2E",
            'text': "#BAD8E7",
            'danger': '#D90404',
            'dark': '#730707',
            'black': '#0D0D0D',
            'panel': '#171717'
        }

    def _setup_styles(self):
        """Configura los estilos visuales de ttk"""
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            self.style.theme_use("alt")
        self._update_styles()

    def _update_styles(self):
        """Aplica los estilos personalizados a todos los widgets"""
        bg = self.PALETTE['black']
        panel = self.PALETTE['panel']
        text = self.PALETTE['text']
        accent = self.PALETTE['danger']
        celeste = self.PALETTE['celeste']
        accent2= self.PALETTE['accent']
        light= self.PALETTE['light']
        
        # Frames y Labels
        self.style.configure("TFrame", background=panel)
        self.style.configure("TLabel", background=panel, foreground=text, font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 11, "bold"), foreground=text #color del texto coordenadas
                            , background=panel) #color del fondo coordenadas
        self.style.configure("Data.TLabel", background=panel,# color del fondo panel de datos
                              foreground=text)# color del texto panel de datos
        self.style.configure("TLabelframe", background=panel # color del fondo del labelframe
                             )
        self.style.configure("TLabelframe.Label", background=panel,# color del fondo del labelframe
                              foreground=text) # color del texto del los textos coordenadas y datos
        
        #Estilo y botones de dibujar, triangulo, borrar y crear csv
        self.style.configure("TButton", background=bg, foreground="white", relief="", padding=6, bordecolor=bg) #bordercolor="red", borderwidth=2
        self.style.map('TButton', background=[('active', accent)])
        
        # Notebook y Treeview
        self.style.configure('TNotebook', background=panel,
                             bordercolor=panel,
                             borderwidth=2,
                             relief='solid',
                             bd=2) #Color del fondo del notebook
        self.style.configure('TNotebook.Tab', background="", #Color del fondo de las tabs
                              foreground=bg,#Color del texto de los botos ab, bd, ac
                              bd=0,
                              padding=[4, 2],
                              borderwidth=0,
                              bordercolor=panel) #Color del borde de las tabs
        self.style.configure('Treeview', 
                           background=self.PALETTE['light'],
                           fieldbackground=self.PALETTE['light'],
                           foreground=self.PALETTE['text'],
                           bd=0,
                           highlightthickness=0,

                           )
        self.style.configure('Treeview.Heading', 
                           background=panel, 
                           foreground='white', #color del texto de X y Y
                           font=("Helvetica", 10, 'bold'),
                           borderwidth=1,
                           bordercolor=panel,
                           bd=0,
                           highlightthickness=0,
                           ) #Color del borde de X y Y

        #RECONSTRUCCIÓN DE ESTILOS
        
        # Frames y Labels


        # 🔹 Aquí estilizamos los LabelFrame (Coordenadas y Datos)
        self.style.configure(
            "Accent.TLabelframe",
            background=panel,  # color del fondo panel
            bordercolor=light,   # color del borde accent
            
            relief="solid"        # tipo de borde
        )

        self.style.configure(
            "Accent.TLabelframe.Label",
            background=panel,
            foreground=text,
            font=("Helvetica", 11, "bold")
        )




    def _setup_ui(self):
        """Construye la interfaz principal"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel izquierdo
        left_frame = self._create_left_panel(main_frame)
        
        # Panel derecho (gráfica)
        self._create_plot_panel(main_frame)

    def _create_left_panel(self, parent):
        """Crea el panel izquierdo con controles y tablas"""
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Tablas de datos
        self._create_data_tables(left_frame)
        
        # Controles de entrada
        self._create_input_controls(left_frame)
        
        # Panel de información
        self._create_info_panel(left_frame)
        
        return left_frame

    def _create_data_tables(self, parent):
        """Crea las tablas para mostrar coordenadas"""
        table_notebook = ttk.Notebook(parent) #Estilo del notebook
        table_notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Crear tablas AB, BC, AC
        self.table_ab = self._create_table(table_notebook, "AB")
        self.table_bc = self._create_table(table_notebook, "BC")
        self.table_ac = self._create_table(table_notebook, "AC")

    def _create_table(self, notebook, label):
        """Crea una tabla individual"""
        tab = ttk.Frame(notebook)
        table = ttk.Treeview(tab, columns=("X", "Y"), show="headings", height=6)
        table.heading("X", text="X")
        table.heading("Y", text="Y")
        table.pack(fill=tk.BOTH, expand=True)
        notebook.add(tab, text=label)
        return table

    def _create_input_controls(self, parent):
        """Crea los controles de entrada de coordenadas"""
        input_frame = ttk.LabelFrame(parent, text="Coordenadas", padding=15, style="Accent.TLabelframe")
        input_frame.pack(fill=tk.X, pady=10)
        
        # Punto A
        ttk.Label(input_frame, text="Punto A (X1, Y1):", style="Header.TLabel").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        self.x1_entry = ttk.Entry(input_frame, width=10)
        self.x1_entry.grid(row=0, column=1, padx=5)
        self.y1_entry = ttk.Entry(input_frame, width=10)
        self.y1_entry.grid(row=0, column=2, padx=5)
        
        # Punto B
        ttk.Label(input_frame, text="Punto B (X2, Y2):", style="Header.TLabel").grid(
            row=1, column=0, padx=5, pady=5, sticky="w")
        self.x2_entry = ttk.Entry(input_frame, width=10)
        self.x2_entry.grid(row=1, column=1, padx=5)
        self.y2_entry = ttk.Entry(input_frame, width=10)
        self.y2_entry.grid(row=1, column=2, padx=5)
        
        # Punto C (para triángulos)
        self.x3_label = ttk.Label(input_frame, text="Punto C (X3, Y3):", style="Header.TLabel")
        self.x3_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.x3_entry = ttk.Entry(input_frame, width=10)
        self.x3_entry.grid(row=2, column=1, padx=5)
        self.y3_entry = ttk.Entry(input_frame, width=10)
        self.y3_entry.grid(row=2, column=2, padx=5)
        self._hide_triangle_inputs()
        
        # Botones
        self._create_action_buttons(input_frame)

    def _hide_triangle_inputs(self):
        """Oculta los campos del punto C"""
        self.x3_label.grid_remove()
        self.x3_entry.grid_remove()
        self.y3_entry.grid_remove()

    def _show_triangle_inputs(self):
        """Muestra los campos del punto C"""
        self.x3_label.grid()
        self.x3_entry.grid()
        self.y3_entry.grid()

    def _create_action_buttons(self, parent):
        """Crea los botones de acción"""
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="Dibujar", command=self.draw_geometry).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Triángulo", command=self.toggle_triangle_mode).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Borrar", command=self.clear_all).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Crear CSV", command=self.export_csv).pack(side=tk.LEFT, padx=6)

    def _create_info_panel(self, parent):
        """Crea el panel de información"""
        data_frame = ttk.LabelFrame(parent, text="Datos", padding=15, style="Accent.TLabelframe")
        data_frame.pack(fill=tk.BOTH, pady=10)
        
        self.direction_label = ttk.Label(data_frame, style="Data.TLabel")
        self.direction_label.pack(fill=tk.X, pady=3)
        self.slope_label = ttk.Label(data_frame, style="Data.TLabel")
        self.slope_label.pack(fill=tk.X, pady=3)
        self.points_label = ttk.Label(data_frame, style="Data.TLabel")
        self.points_label.pack(fill=tk.X, pady=3)

    def _create_plot_panel(self, parent):
        """Crea el panel de la gráfica"""
        fig = plt.figure(figsize=(8, 6), facecolor=self.PALETTE['black'])
        self.ax = fig.add_subplot(111)
        self._setup_plot_style()
        
        self.canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10)
        
        try:
            canvas_widget.configure(background=self.PALETTE['panel'])
        except Exception:
            pass
        
        # Toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, parent)
        self._style_toolbar()
    
   
    def _style_toolbar(self): #estilos en la toolbar
        """Aplica estilos personalizados a la toolbar"""
        panel = self.PALETTE['panel']
        fg = self.PALETTE['light']
        accent = self.PALETTE['accent']
        celeste= self.PALETTE['celeste']
        text= self.PALETTE['text']
        danger= self.PALETTE['danger']
        
        try:
            self.toolbar.configure(background=panel, relief='flat', bd=0)
        except Exception:
            pass
        
        # Estilizar todos los widgets hijos
        
        for child in self.toolbar.winfo_children():
            try:
                child.configure(
                    background=panel,
                    activebackground=accent,
                    bd=0,
                    relief='flat',
                    highlightthickness=0,
                )
            except Exception:
                pass


        
        children = self.toolbar.winfo_children()
        try:
            # Estilizar solo el 2do y 3er elemento (índices 1 y 2)
            for i in [1, 2]:
                if i < len(children):
                    btn = children[i]
                    if isinstance(btn, tk.Button):
                        current_text = btn.cget('text') if hasattr(btn, 'cget') else ''

                        
                        btn.configure(
                            background=text,
                        )
            for child in children:
                if isinstance(child, tk.Checkbutton):
                    child.configure(
                        selectcolor=accent,)

                if isinstance(child, tk.Label):
                    child.configure(
                        foreground=text,
                    )

        except Exception as e:
            pass


        self.toolbar.update()


    def _setup_plot_style(self):
        """Configura el estilo del plot de matplotlib"""
        bg_color = self.PALETTE['black']
        text_color = self.PALETTE['light']
        grid_color = self.PALETTE['accent']
        
        self.ax.set_facecolor(bg_color)
        self.ax.set_xlim(0, 500)
        self.ax.set_ylim(0, 500)
        self.ax.tick_params(colors=text_color)
        self.ax.xaxis.label.set_color(text_color)
        self.ax.yaxis.label.set_color(text_color)
        self.ax.title.set_color(text_color)
        self.ax.grid(True, linestyle="--", linewidth=0.5, color=grid_color)

    def toggle_triangle_mode(self):
        """Alterna entre modo línea y modo triángulo"""
        self.triangle_mode = not self.triangle_mode
        if self.triangle_mode:
            self._show_triangle_inputs()
        else:
            self._hide_triangle_inputs()
        self.clear_all()

    def clear_all(self):
        """Limpia todos los campos y la gráfica"""
        entries = [self.x1_entry, self.y1_entry, self.x2_entry, 
                  self.y2_entry, self.x3_entry, self.y3_entry]
        for entry in entries:
            entry.delete(0, tk.END)
        
        self.ax.clear()
        self._setup_plot_style()
        self.canvas.draw()
        
        for table in [self.table_ab, self.table_bc, self.table_ac]:
            table.delete(*table.get_children())
        
        self.direction_label.config(text="")
        self.slope_label.config(text="")
        self.points_label.config(text="")

    def draw_geometry(self):
        """Dibuja línea o triángulo según el modo activo"""
        if self.triangle_mode:
            self.draw_triangle()
        else:
            self.draw_line()

    def draw_line(self):
        """Dibuja una línea usando el algoritmo DDA"""
        try:
            x1 = float(self.x1_entry.get())
            y1 = float(self.y1_entry.get())
            x2 = float(self.x2_entry.get())
            y2 = float(self.y2_entry.get())
            
            # Validaciones
            if not all(0 <= coord <= 500 for coord in [x1, y1, x2, y2]):
                raise ValueError("Rango permitido: 0-500")
            if (x1, y1) == (x2, y2):
                raise ValueError("Los puntos deben ser diferentes")
            
            # Calcular línea
            A, B = (x1, y1), (x2, y2)
            direction = CalculateLineDirection(A, B).line_direction()
            slope = CalculateSlope(A, B).slope()
            line = DDALinea(A, B, slope, direction)
            points = line.calculate_line()
            
            # Dibujar
            self._plot_line(x1, y1, x2, y2, points)
            
            # Actualizar UI
            self._update_line_info(direction, slope, points)
            
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")

    def _plot_line(self, x1, y1, x2, y2, points):
        """Renderiza la línea en el plot"""
        self.ax.clear()
        self._setup_plot_style()
        
        line_color = self.PALETTE['accent']
        marker_a = self.PALETTE['celeste']
        marker_b = self.PALETTE['dark']
        
        self.ax.plot([x1, x2], [y1, y2], color=line_color, linewidth=3)
        self.ax.plot(x1, y1, 'o', markersize=8, color=marker_a)
        self.ax.plot(x2, y2, 'o', markersize=8, color=marker_b)
        self.ax.set_title(f"Línea: ({x1}, {y1}) → ({x2}, {y2})", fontsize=12)
        self.canvas.draw()
        
        # Actualizar tabla
        self.table_ab.delete(*self.table_ab.get_children())
        for p in points:
            self.table_ab.insert("", "end", values=(round(p[0], 2), round(p[1], 2)))

    def _update_line_info(self, direction, slope, points):
        """Actualiza la información de la línea"""
        direction_desc = {
            1: "↗ Izquierda-Derecha | Abajo-Arriba",
            2: "↘ Izquierda-Derecha | Arriba-Abajo",
            3: "→ Horizontal Derecha",
            4: "↖ Derecha-Izquierda | Abajo-Arriba",
            5: "↙ Derecha-Izquierda | Arriba-Abajo",
            6: "← Horizontal Izquierda",
            7: "↑ Vertical Arriba",
            8: "↓ Vertical Abajo"
        }
        
        self.direction_label.config(
            text=f"Dirección: {direction_desc[direction]} (Caso {direction})")
        self.slope_label.config(
            text=f"Pendiente: {slope if slope is not None else 'Infinita'}")
        self.points_label.config(text=f"Puntos Generados: {len(points)}")

    def draw_triangle(self):
        """Dibuja un triángulo relleno"""
        try:
            A = (float(self.x1_entry.get()), float(self.y1_entry.get()))
            B = (float(self.x2_entry.get()), float(self.y2_entry.get()))
            C = (float(self.x3_entry.get()), float(self.y3_entry.get()))
            
            # Validar que forman un triángulo
            area = abs((B[0]*(C[1]-A[1]) + C[0]*(A[1]-B[1]) + A[0]*(B[1]-C[1]))) / 2
            if area < 1:
                raise ValueError("¡Los puntos deben formar un triángulo válido!")
            
            # Calcular pendientes
            slope_ab = CalculateSlope(A, B).slope()
            slope_bc = CalculateSlope(B, C).slope()
            slope_ac = CalculateSlope(A, C).slope()
            
            # Generar triángulo
            triangle_model = TriangleModel(A, B, C)
            triangle = Triangle(triangle_model)
            filled_data = triangle.calculate_triangle_fill()
            
            # Dibujar
            self._plot_triangle(A, B, C, filled_data, slope_ab, slope_bc, slope_ac)
            
            # Actualizar UI
            self._update_triangle_info(filled_data, area, slope_ab, slope_bc, slope_ac)
            
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Error en triángulo:\n{str(e)}")

    def _plot_triangle(self, A, B, C, filled_data, slope_ab, slope_bc, slope_ac):
        """Renderiza el triángulo en el plot"""
        self.ax.clear()
        self._setup_plot_style()
        
        line_color = self.PALETTE['accent']
        fill_color = f"{self.PALETTE['accent']}40"
        
        # Dibujar bordes con etiquetas
        self._draw_edge_with_label(A, B, slope_ab, line_color, "AB")
        self._draw_edge_with_label(B, C, slope_bc, line_color, "BC")
        self._draw_edge_with_label(C, A, slope_ac, line_color, "AC")
        
        # Relleno optimizado
        segments = []
        for fill_line in filled_data["AC"]:
            points = fill_line["coordenadas"]
            if len(points) >= 2:
                segments.append([
                    (points[0][0], points[0][1]), 
                    (points[-1][0], points[-1][1])
                ])
        
        lc = LineCollection(segments, colors=fill_color, linewidths=1)
        self.ax.add_collection(lc)
        
        self.canvas.draw()

    def _draw_edge_with_label(self, start, end, slope, color, label):
        """Dibuja un borde del triángulo con su etiqueta"""
        midpoint = ((start[0] + end[0])/2, (start[1] + end[1])/2)
        slope_text = f"{label}: {slope:.2f}" if slope is not None else f"{label}: Inf"
        
        self.ax.plot([start[0], end[0]], [start[1], end[1]], 
                    color=color, linewidth=3)
        
        label_bg = self.PALETTE['light']
        self.ax.text(
            midpoint[0], midpoint[1], slope_text,
            color=color, fontsize=9, ha='center', va='center',
            bbox=dict(facecolor=label_bg, alpha=0.9, 
                     edgecolor='none', boxstyle='round,pad=0.3')
        )

    def _update_triangle_info(self, filled_data, area, slope_ab, slope_bc, slope_ac):
        """Actualiza las tablas y estadísticas del triángulo"""
        # Limpiar tablas
        for table in [self.table_ab, self.table_bc, self.table_ac]:
            table.delete(*table.get_children())
        
        # Procesar puntos únicos para cada arista
        def process_points(points, table):
            unique_points = {(round(p[0], 2), round(p[1], 2)) for p in points}
            for x, y in sorted(unique_points):
                table.insert("", "end", values=(x, y))
        
        # AB
        process_points(filled_data["AB"]["coordenadas"], self.table_ab)
        
        # BC
        process_points(filled_data["BC"]["coordenadas"], self.table_bc)
        
        # AC (relleno)
        ac_points = [p for fill_line in filled_data["AC"] 
                    for p in fill_line["coordenadas"]]
        process_points(ac_points, self.table_ac)
        
        # Formatear pendientes
        def fmt_slope(s):
            return f"{s:.2f}" if s is not None else "∞"
        
        slopes_text = (
            f"AB: {fmt_slope(slope_ab)} | "
            f"BC: {fmt_slope(slope_bc)} | "
            f"AC: {fmt_slope(slope_ac)}"
        )
        
        # Actualizar estadísticas
        total_points = sum(len(t.get_children()) 
                          for t in [self.table_ab, self.table_bc, self.table_ac])
        
        self.direction_label.config(text="Triángulo Rellenado")
        self.slope_label.config(text=f"Pendientes: {slopes_text}")
        self.points_label.config(text=f"Área: {area:.2f} px² | Puntos: {total_points}")

    def export_csv(self):
        """Exporta las coordenadas a un archivo CSV"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if not file_path:
                return
            
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Edge", "X", "Y"])
                
                # Exportar todas las tablas
                for table, edge_name in [(self.table_ab, "AB"), 
                                        (self.table_bc, "BC"), 
                                        (self.table_ac, "AC")]:
                    for child in table.get_children():
                        x, y = table.item(child)['values']
                        writer.writerow([edge_name, x, y])
            
            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")


def main():
    """Función principal para iniciar la aplicación"""
    root = tk.Tk()
    app = UltimateLineVisualizer(root)
    root.mainloop()


