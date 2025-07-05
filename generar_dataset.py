import pandas as pd
import os
import re

# Ruta base donde están los CSVs
ruta_base = r"C:\Users\Luisito\Desktop\programa predicciones"
os.chdir(ruta_base)

# Leer CSVs
df_info = pd.read_csv("momentaneo.csv", encoding="latin1", sep=";")  # columnas: Numero, informacion
df_info.columns = df_info.columns.str.strip().str.lower()  # limpiar y poner en minúscula

df_llamadas = pd.read_csv("reporte_cdr.csv", encoding="latin1", sep=";")  # columnas: origen, duracion
df_llamadas.columns = df_llamadas.columns.str.strip().str.lower()

# Función para limpiar texto
def limpiar_texto(texto):
    if pd.isnull(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = re.sub(r"[^a-zA-Z0-9\s]", "", texto)
    return texto

# Procesar df_info: separar nombre y número
def procesar_informacion(info_str):
    try:
        partes = info_str.split(",")
        nombre_completo = partes[0]
        numero = partes[2].split("-")[0] if len(partes) > 2 else ""
        return nombre_completo, numero
    except:
        return "", ""

# Asegurarse de que se llama correctamente la columna 'informacion'
df_info[["nombre_completo", "numero_extraido"]] = df_info["informacion"].apply(
    lambda x: pd.Series(procesar_informacion(x))
)

# Separar apellido y nombre
def separar_nombre_apellido(nombre_completo):
    partes = nombre_completo.strip().split()
    if len(partes) >= 2:
        return partes[0], " ".join(partes[1:])
    elif len(partes) == 1:
        return partes[0], ""
    else:
        return "", ""

df_info[["apellido", "nombre"]] = df_info["nombre_completo"].apply(
    lambda x: pd.Series(separar_nombre_apellido(x))
)

# Limpiar números (dejar solo dígitos)
df_info["numero_extraido"] = df_info["numero_extraido"].astype(str).str.replace(r'\D', '', regex=True)
df_llamadas["origen_limpio"] = df_llamadas["origen"].astype(str).str.replace(r'\D', '', regex=True)

# Unir por número
df_unido = pd.merge(
    df_info,
    df_llamadas,
    left_on="numero_extraido",
    right_on="origen_limpio",
    how="inner"
)

# Resultado final
resultado = df_unido[["apellido", "nombre", "numero_extraido", "duracion"]]
resultado.columns = ["Apellido", "Nombre", "Numero", "Duracion"]

# Guardar solo si hay coincidencias
if resultado.empty:
    print("⚠️ No se encontraron coincidencias entre los números.")
else:
    resultado.to_excel("resultado_llamadas.xlsx", index=False)
    print("✅ Archivo creado como 'resultado_llamadas.xlsx'")
