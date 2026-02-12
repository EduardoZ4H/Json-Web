import pandas as pd
import json

def validate_dataframe(df, required_columns):
    return df[df[required_columns].isnull().any(axis=1)]

def generate_xray_json(df, mappings, idioma_jira):

    map_plataforma = mappings["plataforma"]
    map_ambiente = mappings["ambiente"]
    map_marca = mappings["marca"]

    precond_key = "data" if idioma_jira == "en" else "precondiciones"

    output_json = []
    testset_ids = {}
    current_id = 1

    resumen = {
        "testsets": 0,
        "tests": 0,
        "marcas": set(),
        "plataformas": set(),
        "ambientes": set(),
        "directorios": set(),
        "labels": set()
    }

    # --- Test Sets ---
    for testset, group in df.groupby("Test Set"):
        etiquetas_raw = group["Etiquetas"].dropna().astype(str).tolist()
        etiquetas = (
            [e.strip() for e in etiquetas_raw[0].split(",") if e.strip()]
            if etiquetas_raw else []
        )

        resumen["labels"].update(etiquetas)

        testset_ids[testset] = str(current_id)

        output_json.append({
            "xray_issue_type": "testset",
            "xray_id": str(current_id),
            "fields": {
                "summary": testset,
                "labels": etiquetas
            }
        })

        resumen["testsets"] += 1
        current_id += 1

    # --- Tests ---
    for _, row in df.iterrows():

        resumen["tests"] += 1
        resumen["directorios"].add(str(row["Directorio"]))

        if pd.notna(row.get("Marca")):
            resumen["marcas"].add(str(row["Marca"]))

        if pd.notna(row.get("Plataforma")):
            resumen["plataformas"].add(str(row["Plataforma"]))

        if pd.notna(row.get("Ambiente")):
            resumen["ambientes"].add(str(row["Ambiente"]))

        etiquetas = [e.strip() for e in str(row["Etiquetas"]).split(",") if e.strip()]
        resumen["labels"].update(etiquetas)

    # Crear Tests
    for _, row in df.iterrows():
        plataforma_id = map_plataforma.get(str(row.get("Plataforma")).strip())
        ambiente_id = map_ambiente.get(str(row.get("Ambiente")).strip())
        marca_id = map_marca.get(str(row.get("Marca")).strip())

        steps = [{
            "action": str(row["Pasos para ejecutar"]).strip(),
            "result": str(row["Resultados esperados"]).strip(),
            precond_key: str(row["Precondiciones"]).strip()
        }]

        etiquetas = [e.strip() for e in str(row["Etiquetas"]).split(",") if e.strip()]

        test_entry = {
            "xray_issue_type": "test",
            "fields": {
                "summary": str(row["Descripción del caso de prueba"]),
                "priority": {"name": "High"},
                "description": str(row["Flujo-ID Caso"]),
                "labels": etiquetas,
                "customfield_10039": {"id": str(marca_id)} if marca_id else None,
                "customfield_10037": {"id": str(plataforma_id)} if plataforma_id else None,
                "customfield_10057": {"id": str(ambiente_id)} if ambiente_id else None,
                "assignee": {"name": str(row["Responsable"])} if pd.notna(row["Responsable"]) else None
            },
            "xray_test_repository_folder": str(row["Directorio"]),
            "xray_testtype": "Manual",
            "steps": steps,
            "xray_test_sets": [testset_ids.get(row["Test Set"])]
        }

        test_entry["fields"] = {
            k: v for k, v in test_entry["fields"].items() if v is not None
        }

        output_json.append(test_entry)

    return {
        "json": json.dumps(output_json, indent=2, ensure_ascii=False),
        "resumen": resumen
    }
