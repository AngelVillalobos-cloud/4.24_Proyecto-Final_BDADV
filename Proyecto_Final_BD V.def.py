import re
import customtkinter as ctk
from tkinter import ttk, messagebox
from neo4j import GraphDatabase

# ── CREDENCIALES ──────────────────────────────
URI      = "neo4j://127.0.0.1:7687"
USER     = "neo4j"
PASSWORD = "happybeans"
DB_NAME  = "blog"
# ─────────────────────────────────────────────

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

try:
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    driver.verify_connectivity()
    print("✅ Conexión exitosa")
except Exception as e:
    print(f"❌ Error: {e}")
    driver = None

# ══════════════════════════════════════════════
# DATOS INICIALES (Schema SCOTT clásico)
# Se inyectan solo si la BD está vacía
# ══════════════════════════════════════════════

DATOS_INICIALES = {
    "departamentos": [
        {"deptno": 10, "dname": "CONTABILIDAD", "loc": "CIUDAD DE MEXICO"},
        {"deptno": 20, "dname": "INVESTIGACION", "loc": "GUADALAJARA"},
        {"deptno": 30, "dname": "VENTAS",        "loc": "MONTERREY"},
        {"deptno": 40, "dname": "OPERACIONES",   "loc": "CHIHUAHUA"},
    ],
    "empleados": [
        # DIRECTOR GENERAL
        {"empno": 7839, "ename": "REYES",    "job": "DIRECTOR",  "mgr": None,
         "hiredate": "1981-11-17", "sal": 5000.0, "comm": 0.0, "dept": "CONTABILIDAD"},
        # GERENTES
        {"empno": 7698, "ename": "MENDOZA",  "job": "GERENTE",   "mgr": "REYES",
         "hiredate": "1981-05-01", "sal": 2850.0, "comm": 0.0, "dept": "VENTAS"},
        {"empno": 7782, "ename": "HERRERA",  "job": "GERENTE",   "mgr": "REYES",
         "hiredate": "1981-06-09", "sal": 2450.0, "comm": 0.0, "dept": "CONTABILIDAD"},
        {"empno": 7566, "ename": "RAMIREZ",  "job": "GERENTE",   "mgr": "REYES",
         "hiredate": "1981-04-02", "sal": 2975.0, "comm": 0.0, "dept": "INVESTIGACION"},
        # ANALISTAS
        {"empno": 7788, "ename": "TORRES",   "job": "ANALISTA",  "mgr": "RAMIREZ",
         "hiredate": "1982-12-09", "sal": 3000.0, "comm": 0.0, "dept": "INVESTIGACION"},
        {"empno": 7902, "ename": "VARGAS",   "job": "ANALISTA",  "mgr": "RAMIREZ",
         "hiredate": "1981-12-03", "sal": 3000.0, "comm": 0.0, "dept": "INVESTIGACION"},
        # VENDEDORES
        {"empno": 7499, "ename": "GUTIERREZ","job": "VENDEDOR",  "mgr": "MENDOZA",
         "hiredate": "1981-02-20", "sal": 1600.0, "comm": 300.0,  "dept": "VENTAS"},
        {"empno": 7521, "ename": "CASTILLO", "job": "VENDEDOR",  "mgr": "MENDOZA",
         "hiredate": "1981-02-22", "sal": 1250.0, "comm": 500.0,  "dept": "VENTAS"},
        {"empno": 7654, "ename": "MORALES",  "job": "VENDEDOR",  "mgr": "MENDOZA",
         "hiredate": "1981-09-28", "sal": 1250.0, "comm": 1400.0, "dept": "VENTAS"},
        {"empno": 7844, "ename": "JIMENEZ",  "job": "VENDEDOR",  "mgr": "MENDOZA",
         "hiredate": "1981-09-08", "sal": 1500.0, "comm": 0.0,   "dept": "VENTAS"},
        # EMPLEADOS
        {"empno": 7369, "ename": "LOPEZ",    "job": "EMPLEADO",  "mgr": "VARGAS",
         "hiredate": "1980-12-17", "sal": 800.0,  "comm": 0.0, "dept": "INVESTIGACION"},
        {"empno": 7876, "ename": "GARCIA",   "job": "EMPLEADO",  "mgr": "TORRES",
         "hiredate": "1983-01-12", "sal": 1100.0, "comm": 0.0, "dept": "INVESTIGACION"},
        {"empno": 7900, "ename": "FLORES",   "job": "EMPLEADO",  "mgr": "MENDOZA",
         "hiredate": "1981-12-03", "sal": 950.0,  "comm": 0.0, "dept": "VENTAS"},
        {"empno": 7934, "ename": "CRUZ",     "job": "EMPLEADO",  "mgr": "HERRERA",
         "hiredate": "1982-01-23", "sal": 1300.0, "comm": 0.0, "dept": "CONTABILIDAD"},
    ]
}

def inyectar_datos_iniciales():
    """Crea departamentos y empleados de prueba si la BD está vacía."""
    try:
        with driver.session(database=DB_NAME) as session:
            total = session.run("MATCH (e:Emp) RETURN count(e) AS n").single()["n"]
            if total > 0:
                print(f"ℹ️  BD ya tiene {total} empleado(s), no se inyectan datos.")
                return

            print("⏳ Inyectando datos iniciales...")

            # Crear departamentos
            for d in DATOS_INICIALES["departamentos"]:
                session.run("""
                    MERGE (dept:Dept {dname: $dname})
                    SET dept.loc = $loc, dept.deptno = $deptno
                """, **d)

            # Crear empleados y relaciones
            for emp in DATOS_INICIALES["empleados"]:
                session.run("""
                    MATCH (d:Dept {dname: $dept})
                    CREATE (e:Emp {
                        empno: $empno, ename: $ename, job: $job,
                        mgr: $mgr, hiredate: $hiredate,
                        sal: $sal, comm: $comm
                    })
                    CREATE (e)-[:TRABAJA_EN]->(d)
                """, **emp)

            print(f"✅ {len(DATOS_INICIALES['empleados'])} empleados y "
                  f"{len(DATOS_INICIALES['departamentos'])} departamentos creados.")
    except Exception as e:
        print(f"❌ Error al inyectar datos: {e}")


# ══════════════════════════════════════════════
# FUNCIONES DE VALIDACIÓN
# ══════════════════════════════════════════════

def solo_letras(valor, campo):
    if valor and not valor.replace(" ", "").isalpha():
        messagebox.showerror("Error de validación",
            f"'{campo}' solo debe contener letras.\nEjemplo: GARCIA, VENTAS")
        return False
    return True

def validar_fecha(fecha_str):
    if not fecha_str:
        return True
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_str):
        messagebox.showerror("Error de validación",
            "Fecha inválida. Usa el formato AAAA-MM-DD\nEjemplo: 1981-05-01")
        return False
    anio, mes, dia = map(int, fecha_str.split("-"))
    if not (1900 <= anio <= 2100) or not (1 <= mes <= 12) or not (1 <= dia <= 31):
        messagebox.showerror("Error de validación",
            "Fecha fuera de rango.\nVerifica año (1900-2100), mes (1-12) y día (1-31).")
        return False
    return True

def validar_numerico(valor_str, campo):
    if not valor_str or not valor_str.replace("$","").strip():
        return True, 0.0
    try:
        valor = float(valor_str.replace("$", "").strip())
    except ValueError:
        messagebox.showerror("Error de validación",
            f"'{campo}' debe ser un número.\nEjemplo: 3000 o 500.50")
        return False, None
    if valor < 0:
        messagebox.showerror("Error de validación",
            f"'{campo}' no puede ser negativo.")
        return False, None
    return True, valor

def validar_empno(empno_str):
    if not empno_str:
        return True, None
    try:
        empno = int(empno_str)
        if empno <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error de validación",
            "EMPNO debe ser un entero positivo.\nEjemplo: 7369")
        return False, None
    return True, empno

def driver_ok():
    if not driver:
        messagebox.showerror("Sin conexión",
            "No hay conexión con Neo4j.\nReinicia la aplicación.")
        return False
    return True


# ══════════════════════════════════════════════
# OPERACIONES CRUD
# ══════════════════════════════════════════════

def alta_empleado():
    if not driver_ok(): return

    ename        = ent_name.get().strip().upper()
    job          = ent_job.get().strip().upper()
    dept_name    = ent_dept.get().strip().upper()
    loc          = ent_loc.get().strip().upper()
    mgr_str      = ent_mgr.get().strip().upper()
    hiredate_str = ent_hiredate.get().strip()
    empno_str    = ent_empno.get().strip()

    # Obligatorios
    if not ename or not job or not dept_name:
        messagebox.showwarning("Faltan datos",
            "Nombre, Puesto y Departamento son obligatorios.")
        return

    # Solo letras
    if not solo_letras(ename,     "Nombre"):       return
    if not solo_letras(job,       "Puesto"):       return
    if not solo_letras(dept_name, "Departamento"): return
    if not solo_letras(loc,       "Ubicación"):    return
    if not solo_letras(mgr_str,   "Jefe (MGR)"):  return

    # Numéricos
    ok, sal  = validar_numerico(ent_sal.get(),  "Salario");  
    if not ok: return
    ok, comm = validar_numerico(ent_comm.get(), "Comisión"); 
    if not ok: return
    ok, empno = validar_empno(empno_str)
    if not ok: return

    # Fecha
    if not validar_fecha(hiredate_str): return

    try:
        with driver.session(database=DB_NAME) as session:
            # Duplicado por nombre
            if session.run("MATCH (e:Emp {ename:$ename}) RETURN e",
                           ename=ename).single():
                messagebox.showerror("Duplicado",
                    f"Ya existe un empleado llamado '{ename}'.")
                return
            # Duplicado por EMPNO
            if empno and session.run("MATCH (e:Emp {empno:$empno}) RETURN e",
                                     empno=empno).single():
                messagebox.showerror("Duplicado",
                    f"Ya existe un empleado con EMPNO {empno}.")
                return
            # Jefe debe existir si se especificó
            if mgr_str and not session.run(
                    "MATCH (e:Emp {ename:$mgr}) RETURN e", mgr=mgr_str).single():
                if not messagebox.askyesno("Jefe no encontrado",
                        f"No existe ningún empleado llamado '{mgr_str}'.\n"
                        "¿Deseas registrar al empleado de todas formas?"):
                    return

            session.run("""
                MERGE (d:Dept {dname: $dept_name})
                ON CREATE SET d.loc = $loc
                CREATE (e:Emp {empno:$empno, ename:$ename, job:$job,
                               mgr:$mgr, hiredate:$hiredate, sal:$sal, comm:$comm})
                CREATE (e)-[:TRABAJA_EN]->(d)
            """, empno=empno, ename=ename, job=job,
                 mgr=mgr_str or None, hiredate=hiredate_str or None,
                 sal=sal, comm=comm, dept_name=dept_name, loc=loc or None)

            messagebox.showinfo("Éxito", f"Empleado '{ename}' registrado.")
            limpiar_campos(); consulta_empleados()
    except Exception as e:
        messagebox.showerror("Error Neo4j", str(e))


def consulta_empleados():
    if not driver_ok(): return
    for row in tabla.get_children():
        tabla.delete(row)
    try:
        with driver.session(database=DB_NAME) as session:
            results = session.run("""
                MATCH (e:Emp)-[:TRABAJA_EN]->(d:Dept)
                RETURN e.empno AS empno, e.ename AS ename, e.job AS job,
                       e.mgr AS mgr, e.hiredate AS hiredate,
                       e.sal AS sal, e.comm AS comm,
                       d.dname AS dname, d.loc AS loc
                ORDER BY e.ename
            """)
            total = 0
            for r in results:
                tabla.insert("", "end", values=(
                    r["empno"]    or "-",
                    r["ename"],
                    r["job"],
                    r["mgr"]      or "-",
                    r["hiredate"] or "-",
                    f"${r['sal']:.2f}",
                    f"${(r['comm'] or 0.0):.2f}",
                    r["dname"],
                    r["loc"]      or "-",
                ))
                total += 1
            lbl_total.configure(text=f"Total: {total} empleado(s)")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def buscar_empleado():
    if not driver_ok(): return
    busqueda = ent_buscar.get().strip().upper()
    if not busqueda:
        messagebox.showwarning("Faltan datos", "Escribe un nombre para buscar.")
        return
    if not solo_letras(busqueda, "Búsqueda"): return

    for row in tabla.get_children():
        tabla.delete(row)
    try:
        with driver.session(database=DB_NAME) as session:
            results = session.run("""
                MATCH (e:Emp)-[:TRABAJA_EN]->(d:Dept)
                WHERE e.ename CONTAINS $busqueda
                RETURN e.empno AS empno, e.ename AS ename, e.job AS job,
                       e.mgr AS mgr, e.hiredate AS hiredate,
                       e.sal AS sal, e.comm AS comm,
                       d.dname AS dname, d.loc AS loc
                ORDER BY e.ename
            """, busqueda=busqueda)
            encontrado = False
            total = 0
            for r in results:
                encontrado = True
                total += 1
                tabla.insert("", "end", values=(
                    r["empno"]    or "-",
                    r["ename"],
                    r["job"],
                    r["mgr"]      or "-",
                    r["hiredate"] or "-",
                    f"${r['sal']:.2f}",
                    f"${(r['comm'] or 0.0):.2f}",
                    r["dname"],
                    r["loc"]      or "-",
                ))
            if encontrado:
                lbl_total.configure(text=f"Resultados: {total}")
            else:
                messagebox.showinfo("Sin resultados",
                    f"No se encontró ningún empleado con '{busqueda}' en el nombre.")
                consulta_empleados()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def cambio_empleado():
    if not driver_ok(): return

    ename = ent_name.get().strip().upper()
    if not ename:
        messagebox.showwarning("Faltan datos",
            "El campo Nombre es obligatorio para actualizar.")
        return

    job_val      = ent_job.get().strip().upper()  or None
    mgr_val      = ent_mgr.get().strip().upper()  or None
    hiredate_val = ent_hiredate.get().strip()      or None

    if job_val and not solo_letras(job_val, "Puesto"):      return
    if mgr_val and not solo_letras(mgr_val, "Jefe (MGR)"): return

    ok, sal_val  = validar_numerico(ent_sal.get(),  "Salario");  
    if not ok: return
    ok, comm_val = validar_numerico(ent_comm.get(), "Comisión"); 
    if not ok: return

    sal_val  = sal_val  if ent_sal.get().strip()  else None
    comm_val = comm_val if ent_comm.get().strip() else None

    if not validar_fecha(hiredate_val): return

    try:
        with driver.session(database=DB_NAME) as session:
            if not session.run("MATCH (e:Emp {ename:$ename}) RETURN e",
                               ename=ename).single():
                messagebox.showwarning("No encontrado",
                    f"No existe ningún empleado llamado '{ename}'.")
                return

            # Validar que el jefe nuevo existe (si se cambió)
            if mgr_val and not session.run(
                    "MATCH (e:Emp {ename:$mgr}) RETURN e", mgr=mgr_val).single():
                if not messagebox.askyesno("Jefe no encontrado",
                        f"No existe ningún empleado llamado '{mgr_val}'.\n"
                        "¿Deseas guardar el cambio de todas formas?"):
                    return

            result = session.run("""
                MATCH (e:Emp {ename:$ename})
                SET e.job      = COALESCE($job,      e.job),
                    e.mgr      = COALESCE($mgr,      e.mgr),
                    e.hiredate = COALESCE($hiredate, e.hiredate),
                    e.sal      = COALESCE($sal,      e.sal),
                    e.comm     = COALESCE($comm,     e.comm)
                RETURN e
            """, ename=ename, job=job_val, mgr=mgr_val,
                 hiredate=hiredate_val, sal=sal_val, comm=comm_val)

            if result.consume().counters.properties_set > 0:
                messagebox.showinfo("Éxito", f"Datos de '{ename}' actualizados.")
                limpiar_campos(); consulta_empleados()
            else:
                messagebox.showinfo("Sin cambios",
                    "No se detectaron cambios. Modifica al menos un campo.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def baja_empleado():
    if not driver_ok(): return

    ename = ent_name.get().strip().upper()
    if not ename:
        messagebox.showwarning("Faltan datos",
            "Escribe el nombre del empleado a eliminar.")
        return
    if not solo_letras(ename, "Nombre"): return

    try:
        with driver.session(database=DB_NAME) as session:
            # Verificar que el empleado existe
            emp = session.run(
                "MATCH (e:Emp {ename:$ename})-[:TRABAJA_EN]->(d:Dept) "
                "RETURN e, d.dname AS dname", ename=ename).single()
            if not emp:
                messagebox.showwarning("No encontrado",
                    f"No existe ningún empleado llamado '{ename}'.")
                return

            dept_name = emp["dname"]

            # Verificar si este empleado es jefe de alguien
            subordinados = session.run(
                "MATCH (e:Emp {mgr:$ename}) RETURN e.ename AS nombre",
                ename=ename).values("nombre")
            if subordinados:
                lista = ", ".join([s[0] for s in subordinados])
                messagebox.showwarning("Empleado es jefe",
                    f"'{ename}' es jefe de: {lista}\n\n"
                    "Actualiza el campo MGR de esos empleados antes de eliminar.")
                return

            # Verificar cuántos empleados quedan en el departamento
            conteo = session.run("""
                MATCH (e:Emp)-[:TRABAJA_EN]->(d:Dept {dname:$dname})
                RETURN count(e) AS n
            """, dname=dept_name).single()["n"]

            es_ultimo = (conteo == 1)

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    # Confirmación de eliminación
    if not messagebox.askyesno("Confirmar eliminación",
            f"¿Seguro que deseas eliminar a '{ename}'?\n\n"
            "Esta acción no se puede deshacer."):
        return

    # Si es el último del depto, preguntar si también borrar el depto
    borrar_dept = False
    if es_ultimo:
        borrar_dept = messagebox.askyesno("Departamento vacío",
            f"'{ename}' es el único empleado en '{dept_name}'.\n\n"
            f"¿Deseas eliminar también el departamento '{dept_name}'?")

    try:
        with driver.session(database=DB_NAME) as session:
            session.run("MATCH (e:Emp {ename:$ename}) DETACH DELETE e", ename=ename)
            if borrar_dept:
                session.run(
                    "MATCH (d:Dept {dname:$dname}) "
                    "WHERE NOT (d)<-[:TRABAJA_EN]-() DELETE d",
                    dname=dept_name)
                messagebox.showinfo("Éxito",
                    f"Empleado '{ename}' y departamento '{dept_name}' eliminados.")
            else:
                messagebox.showinfo("Éxito", f"Empleado '{ename}' eliminado.")
            limpiar_campos(); consulta_empleados()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def seleccionar_fila(event):
    sel = tabla.focus()
    if not sel: return
    v = tabla.item(sel, "values")
    limpiar_campos()
    ent_empno.insert(0,    "" if v[0] == "-" else v[0])
    ent_name.insert(0,     v[1])
    ent_job.insert(0,      v[2])
    ent_mgr.insert(0,      "" if v[3] == "-" else v[3])
    ent_hiredate.insert(0, "" if v[4] == "-" else v[4])
    ent_sal.insert(0,      v[5].replace("$", ""))
    ent_comm.insert(0,     v[6].replace("$", ""))
    ent_dept.insert(0,     v[7])
    ent_loc.insert(0,      "" if v[8] == "-" else v[8])
    ent_dept.configure(state="disabled")

def deseleccionar_tabla(event):
    ent_dept.configure(state="normal")

def limpiar_campos():
    ent_dept.configure(state="normal")
    for c in (ent_empno, ent_name, ent_job, ent_mgr, ent_hiredate,
              ent_sal, ent_comm, ent_dept, ent_loc, ent_buscar):
        c.delete(0, "end")
    lbl_total.configure(text="")

def cerrar_app():
    if driver: driver.close()
    app.destroy()


# ══════════════════════════════════════════════
# INTERFAZ GRÁFICA
# ══════════════════════════════════════════════
app = ctk.CTk()
app.title("Blog DB — CRUD Neo4j v3.0")
app.geometry("1280x700")
app.protocol("WM_DELETE_WINDOW", cerrar_app)

frame_form = ctk.CTkFrame(app, width=310, corner_radius=15)
frame_form.pack(side="left", fill="y", padx=15, pady=15)
frame_form.pack_propagate(False)

ctk.CTkLabel(frame_form, text="Datos del Empleado",
             font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(18, 10))

campos = [
    ("EMPNO (clave numérica):",      "ent_empno"),
    ("Nombre (ENAME):",              "ent_name"),
    ("Puesto (JOB):",                "ent_job"),
    ("Jefe (MGR nombre):",           "ent_mgr"),
    ("Fecha contrato (AAAA-MM-DD):", "ent_hiredate"),
    ("Salario (SAL):",               "ent_sal"),
    ("Comisión (COMM):",             "ent_comm"),
    ("Departamento (DNAME):",        "ent_dept"),
    ("Ubicación (LOC):",             "ent_loc"),
]
entries = {}
for lbl, var in campos:
    ctk.CTkLabel(frame_form, text=lbl, anchor="w").pack(
        fill="x", padx=18, pady=(5, 0))
    e = ctk.CTkEntry(frame_form, width=270)
    e.pack(padx=18, pady=(0, 2))
    entries[var] = e

ent_empno    = entries["ent_empno"]
ent_name     = entries["ent_name"]
ent_job      = entries["ent_job"]
ent_mgr      = entries["ent_mgr"]
ent_hiredate = entries["ent_hiredate"]
ent_sal      = entries["ent_sal"]
ent_comm     = entries["ent_comm"]
ent_dept     = entries["ent_dept"]
ent_loc      = entries["ent_loc"]

fb = ctk.CTkFrame(frame_form, fg_color="transparent")
fb.pack(pady=16)
ctk.CTkButton(fb, text="Alta",
    fg_color="#28a745", hover_color="#218838",
    width=125, command=alta_empleado).grid(row=0, column=0, padx=5, pady=4)
ctk.CTkButton(fb, text="Baja",
    fg_color="#dc3545", hover_color="#c82333",
    width=125, command=baja_empleado).grid(row=0, column=1, padx=5, pady=4)
ctk.CTkButton(fb, text="Actualizar",
    fg_color="#ffc107", text_color="black", hover_color="#e0a800",
    width=125, command=cambio_empleado).grid(row=1, column=0, padx=5, pady=4)
ctk.CTkButton(fb, text="Limpiar",
    fg_color="gray", hover_color="darkgray",
    width=125, command=limpiar_campos).grid(row=1, column=1, padx=5, pady=4)

frame_datos = ctk.CTkFrame(app, corner_radius=15)
frame_datos.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)

frame_buscar = ctk.CTkFrame(frame_datos, fg_color="transparent")
frame_buscar.pack(fill="x", padx=20, pady=(18, 8))
ent_buscar = ctk.CTkEntry(frame_buscar,
    placeholder_text="Buscar por nombre (parcial)...", width=300)
ent_buscar.pack(side="left", padx=(0, 8))
ctk.CTkButton(frame_buscar, text="Buscar",
    width=100, command=buscar_empleado).pack(side="left")
ctk.CTkButton(frame_buscar, text="Ver Todos",
    fg_color="#17a2b8", hover_color="#138496",
    width=100, command=consulta_empleados).pack(side="left", padx=8)
lbl_total = ctk.CTkLabel(frame_buscar, text="", font=ctk.CTkFont(size=12))
lbl_total.pack(side="right", padx=10)

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview",
    background="#2b2b2b", foreground="white",
    rowheight=28, fieldbackground="#2b2b2b", borderwidth=0)
style.map("Treeview", background=[("selected", "#1f538d")])
style.configure("Treeview.Heading",
    background="#1f538d", foreground="white",
    relief="flat", font=("Arial", 10, "bold"))

columnas = ("EMPNO", "Nombre", "Puesto", "MGR", "Contratado",
            "Salario", "Comisión", "Depto", "LOC")
tabla = ttk.Treeview(frame_datos, columns=columnas, show="headings", height=18)
for col, w in zip(columnas, [60, 110, 100, 100, 110, 90, 90, 100, 100]):
    tabla.heading(col, text=col)
    tabla.column(col, anchor="center", width=w)
tabla.pack(fill="both", expand=True, padx=20, pady=10)
tabla.bind("<ButtonRelease-1>", seleccionar_fila)
frame_datos.bind("<Button-1>", deseleccionar_tabla)

# Inyectar datos y cargar tabla al arrancar
def inicio():
    inyectar_datos_iniciales()
    consulta_empleados()

app.after(500, inicio)
app.mainloop()
