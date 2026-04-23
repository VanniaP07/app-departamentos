import customtkinter as ctk
from tkcalendar import Calendar
from tkinter import messagebox
from datetime import datetime
import json
import os
import streamlit as st
import pandas as pd

class AppRentas(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Rentas Pro")
        self.geometry("1100x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.archivo_datos = "datos_reservas.json"
        self.reservas = []
        self.reserva_en_edicion = None
        
        # Diccionario para convertir números a nombres de meses
        self.meses_es = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }

        self.cargar_de_disco()
        self.contenedor_principal = ctk.CTkFrame(self)
        self.contenedor_principal.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.contenedor_principal.grid_columnconfigure(0, weight=1)
        self.contenedor_principal.grid_rowconfigure(0, weight=1)
        self.mostrar_menu_principal()

    # --- Lógica de Formateo de Fechas ---
    def formatear_fecha_lectura(self, fecha_str):
        """Convierte DD/MM/YY a 'DD de Mes de YYYY'"""
        try:
            dt = datetime.strptime(fecha_str, "%d/%m/%y")
            mes_nombre = self.meses_es[dt.month]
            return f"{dt.day} de {mes_nombre} de {dt.year}"
        except:
            return fecha_str

    def ordenar_reservas(self):
        """Ordena la lista por fecha real de inicio"""
        def obtener_clave(reserva):
            try:
                return datetime.strptime(reserva["inicio"], "%d/%m/%y")
            except:
                return datetime.min
        self.reservas.sort(key=obtener_clave)

    # --- Navegación ---
    def mostrar_menu_principal(self):
        for widget in self.contenedor_principal.winfo_children(): widget.destroy()
        menu_frame = ctk.CTkFrame(self.contenedor_principal, fg_color="transparent")
        menu_frame.grid(row=0, column=0)
        
        ctk.CTkLabel(menu_frame, text="MENÚ PRINCIPAL", font=("Arial", 35, "bold")).pack(pady=20)
        ctk.CTkButton(menu_frame, text="📝 REALIZAR NUEVA RESERVA", font=("Arial", 20), height=60, width=450, 
                      command=self.abrir_solo_registro).pack(pady=10)
        ctk.CTkButton(menu_frame, text="📋 ADMINISTRACIÓN GENERAL", font=("Arial", 20), height=60, width=450, 
                      fg_color="#555555", command=self.abrir_solo_admin_general).pack(pady=10)
        
        ctk.CTkLabel(menu_frame, text="VER POR TRABAJADOR:", font=("Arial", 16, "bold"), text_color="gray").pack(pady=(30, 10))
        botones_trabajadores = ctk.CTkFrame(menu_frame, fg_color="transparent")
        botones_trabajadores.pack()
        for nombre in ["Jaky", "Miriam", "Pepillo"]:
            ctk.CTkButton(botones_trabajadores, text=f"👤 {nombre}", width=140, height=50,
                          command=lambda n=nombre: self.abrir_admin_trabajador(n)).pack(side="left", padx=5)

    def abrir_solo_registro(self):
        for widget in self.contenedor_principal.winfo_children(): widget.destroy()
        ctk.CTkButton(self.contenedor_principal, text="⬅ Menú Principal", command=self.mostrar_menu_principal, 
                      fg_color="#333333", width=150).pack(anchor="nw", padx=20, pady=10)
        self.vista_registro = ctk.CTkFrame(self.contenedor_principal)
        self.vista_registro.pack(fill="both", expand=True, padx=10, pady=10)
        self.vista_registro.grid_columnconfigure((0, 1), weight=1)
        self.vista_registro.grid_rowconfigure(0, weight=1)
        self.setup_registro()

    def abrir_admin_trabajador(self, nombre):
        for widget in self.contenedor_principal.winfo_children(): widget.destroy()
        ctk.CTkButton(self.contenedor_principal, text="⬅ Menú Principal", command=self.mostrar_menu_principal, 
                      fg_color="#333333", width=150).pack(anchor="nw", padx=20, pady=10)
        self.vista_admin = ctk.CTkFrame(self.contenedor_principal)
        self.vista_admin.pack(fill="both", expand=True, padx=10, pady=10)
        self.vista_admin.grid_columnconfigure(0, weight=1)
        self.vista_admin.grid_rowconfigure(0, weight=1)
        self.combo_filtro = ctk.CTkComboBox(self.vista_admin, values=["Todos", "Jaky", "Miriam", "Pepillo"], 
                                            command=lambda x: self.actualizar_lista())
        self.combo_filtro.set(nombre)
        self.setup_admin()

    def abrir_solo_admin_general(self):
        self.abrir_admin_trabajador("Todos")

    def setup_registro(self):
        self.frame_form = ctk.CTkFrame(self.vista_registro)
        self.frame_form.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_form.grid_columnconfigure(0, weight=1)
        for i in range(12): self.frame_form.grid_rowconfigure(i, weight=1)

        ctk.CTkLabel(self.frame_form, text="Trabajador:").grid(row=0, column=0, sticky="w", padx=25)
        self.combo_dueño = ctk.CTkComboBox(self.frame_form, values=["Jaky", "Miriam", "Pepillo"])
        self.combo_dueño.grid(row=1, column=0, pady=(0,10), padx=20, sticky="ew")

        self.entry_nombre = ctk.CTkEntry(self.frame_form, placeholder_text="Nombre del cliente")
        self.entry_nombre.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        self.entry_depa = ctk.CTkEntry(self.frame_form, placeholder_text="Depto / Casa")
        self.entry_depa.grid(row=3, column=0, pady=10, padx=20, sticky="ew")

        self.entry_precio = ctk.CTkEntry(self.frame_form, placeholder_text="Precio Noche ($)")
        self.entry_precio.grid(row=4, column=0, pady=10, padx=20, sticky="ew")
        self.entry_precio.bind("<KeyRelease>", lambda e: self.calcular_total())

        self.check_trans = ctk.CTkCheckBox(self.frame_form, text="Transporte (+$100)", command=self.calcular_total)
        self.check_trans.grid(row=5, column=0, pady=10, padx=20, sticky="w")

        self.label_f_inicio = ctk.CTkLabel(self.frame_form, text="Llegada: --", text_color="#3b8ed0")
        self.label_f_inicio.grid(row=6, column=0)
        self.label_f_fin = ctk.CTkLabel(self.frame_form, text="Salida: --", text_color="#e5ad45")
        self.label_f_fin.grid(row=7, column=0)

        self.label_noches = ctk.CTkLabel(self.frame_form, text="Noches: 0", font=("Arial", 14, "bold"))
        self.label_noches.grid(row=8, column=0)

        self.label_total = ctk.CTkLabel(self.frame_form, text="TOTAL: $0", font=("Arial", 22, "bold"), text_color="lightgreen")
        self.label_total.grid(row=9, column=0, pady=10)

        self.btn_guardar = ctk.CTkButton(self.frame_form, text="Guardar Reserva", command=self.guardar_datos, fg_color="green")
        self.btn_guardar.grid(row=10, column=0, pady=20, padx=20, sticky="ew")

        # Calendario
        self.frame_cal = ctk.CTkFrame(self.vista_registro)
        self.frame_cal.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.frame_cal.grid_columnconfigure(0, weight=1)
        self.frame_cal.grid_rowconfigure(0, weight=1)
        self.cal = Calendar(self.frame_cal, selectmode='day', locale='es_ES')
        self.cal.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        btn_f = ctk.CTkFrame(self.frame_cal, fg_color="transparent")
        btn_f.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        btn_f.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_f, text="LLEGADA", command=lambda: self.asignar_fecha("in"), fg_color="#3b8ed0").grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btn_f, text="SALIDA", command=lambda: self.asignar_fecha("out"), fg_color="#e5ad45").grid(row=0, column=1, padx=5, sticky="ew")

    def setup_admin(self):
        self.lista_frame = ctk.CTkScrollableFrame(self.vista_admin, label_text="Historial por Fechas")
        self.lista_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.actualizar_lista()

    def asignar_fecha(self, tipo):
        fecha = self.cal.get_date()
        if tipo == "in": self.label_f_inicio.configure(text=fecha)
        else: self.label_f_fin.configure(text=fecha)
        self.calcular_total()

    def calcular_total(self):
        try:
            f1, f2 = self.label_f_inicio.cget("text"), self.label_f_fin.cget("text")
            p = self.entry_precio.get()
            ex = 100 if self.check_trans.get() else 0
            if "Llegada" not in f1 and "Salida" not in f2:
                d1, d2 = datetime.strptime(f1, "%d/%m/%y"), datetime.strptime(f2, "%d/%m/%y")
                noches = (d2 - d1).days
                if noches >= 0:
                    self.label_noches.configure(text=f"Noches: {noches}")
                    if p.isdigit(): self.label_total.configure(text=f"TOTAL: ${(noches * int(p)) + ex}")
        except: pass

    def guardar_datos(self):
        dueño = self.combo_dueño.get()
        reserva = {
            "dueño": dueño, "cliente": self.entry_nombre.get(),
            "depa": self.entry_depa.get(), "precio": self.entry_precio.get(),
            "inicio": self.label_f_inicio.cget("text"), "fin": self.label_f_fin.cget("text"),
            "transporte": self.check_trans.get(), "total": self.label_total.cget("text")
        }
        if self.reserva_en_edicion: self.reservas.remove(self.reserva_en_edicion)
        self.reservas.append(reserva); self.guardar_en_disco()
        
        # Pop up
        msg = ctk.CTkToplevel(self)
        msg.geometry("350x180"); msg.attributes("-topmost", True)
        ctk.CTkLabel(msg, text="✅ Guardado", font=("Arial", 16, "bold")).pack(pady=20)
        ctk.CTkButton(msg, text=f"Ver Reservas de {dueño}", command=lambda: [msg.destroy(), self.abrir_admin_trabajador(dueño)]).pack(pady=5)
        ctk.CTkButton(msg, text="Seguir", fg_color="gray", command=lambda: [msg.destroy(), self.limpiar_formulario()]).pack(pady=5)

    def actualizar_lista(self):
        for w in self.lista_frame.winfo_children(): w.destroy()
        self.ordenar_reservas()
        filtro = self.combo_filtro.get()
        for res in self.reservas:
            if filtro != "Todos" and res.get("dueño") != filtro: continue
            f = ctk.CTkFrame(self.lista_frame); f.pack(fill="x", pady=5, padx=5)
            
            # MOSTRAR FECHA CON NOMBRE DE MES
            fecha_linda = self.formatear_fecha_lectura(res['inicio'])
            info = f"📅 {fecha_linda}\n👤 {res['cliente']} | 🏠 {res['depa']} | 💰 {res['total']}"
            
            ctk.CTkLabel(f, text=info, justify="left").pack(side="left", padx=15, pady=5)
            ctk.CTkButton(f, text="X", fg_color="red", width=40, command=lambda r=res: self.eliminar(r)).pack(side="right", padx=10)
            ctk.CTkButton(f, text="Edit", fg_color="gray", width=40, command=lambda r=res: self.preparar_edicion(r)).pack(side="right", padx=5)

    def eliminar(self, res):
        if messagebox.askyesno("Eliminar", "Borrar reserva?"): self.reservas.remove(res); self.guardar_en_disco(); self.actualizar_lista()

    def preparar_edicion(self, res):
        self.reserva_en_edicion = res; self.abrir_solo_registro()
        self.entry_nombre.insert(0, res["cliente"]); self.entry_depa.insert(0, res["depa"])
        self.entry_precio.insert(0, res["precio"]); self.label_f_inicio.configure(text=res["inicio"])
        self.label_f_fin.configure(text=res["fin"])
        self.calcular_total(); self.btn_guardar.configure(text="Actualizar", fg_color="orange")

    def limpiar_formulario(self):
        self.entry_nombre.delete(0, 'end'); self.label_total.configure(text="TOTAL: $0")
        self.label_f_inicio.configure(text="Llegada: --"); self.label_f_fin.configure(text="Salida: --")

    def guardar_en_disco(self):
        with open(self.archivo_datos, "w") as f: json.dump(self.reservas, f)

    def cargar_de_disco(self):
        if os.path.exists(self.archivo_datos):
            with open(self.archivo_datos, "r") as f: self.reservas = json.load(f)

if __name__ == "__main__":
    app = AppRentas()
    app.mainloop()
