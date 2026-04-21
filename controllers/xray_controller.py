import pandas as pd
from models.xray_model import generate_xray_json
from utils.mappings import mappings

'''
mappings = {
    "plataforma": {
        "iOS": 10110, "Android": 10111, "iOS & Android": 10112,
        "POS": 10024, "Web": 10026, "Web & Apps": 10025,
        "Web, Apps & POS": 10027, "Otro": 10113,
        "Call Center Ordering": 10154, "Web & Apps & Call Center Ordering": 10155,
        "Agregadores": 10161, "WhatsApp": 10168, "MDW": 10169, "Core": 10170,
        "PC Gerente": 10172
    },
    "ambiente": {
        "QA": 10086, "PROD": 10087
    },
    "marca": {
        "Chilis": 10043, "VIPS": 10044, "Italiannis": 10045, "PFChangs": 10046,
        "El Portón": 10047, "The Cheesecake Factory": 10048, "Starbucks": 10049,
        "Domino's Pizza": 10050, "Burger King": 10051, "WOW+": 10052,
        "ClubBy": 10053, "Foster’s Hollywood": 10054, "Archies": 10055,
        "Ginos": 10056, "TGI Fridays": 10057, "MyALSEA": 10147,
        "COG": 10148, "Delivery ALSEA": 10149, "ANS": 10150,
        "Casuales (Todos)": 10171, "MDW Spain": 10186
    }
}
'''
def process_file(uploaded_file, idioma_jira):
    df = pd.read_excel(uploaded_file)

    required_columns = [
        "REQ", "Flujo-ID Caso", "Importancia", "Tipo de prueba",
        "Descripción del caso de prueba", "Precondiciones",
        "Pasos para ejecutar", "Resultados esperados",
        "Responsable", "Etiquetas", "Directorio", "Test Set"
    ]

    missing_rows = df[df[required_columns].isnull().any(axis=1)]
    if not missing_rows.empty:
        raise ValueError(f"El archivo tiene {len(missing_rows)} filas con campos obligatorios vacíos")

    return generate_xray_json(df, mappings, idioma_jira)

#generacion manual

