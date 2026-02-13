import pandas as pd
import json

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

    testset_details = {}

    # --- Crear Test Sets ---
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

        # Detalles por Test Set
        testset_details[testset] = {
            "num_casos": len(group),
            "marca": str(group["Marca"].dropna().unique()[0]) if not group["Marca"].dropna().empty else None,
            "etiquetas": etiquetas,
            "directorio": str(group["Directorio"].dropna().unique()[0]) if not group["Directorio"].dropna().empty else None
        }

        current_id += 1

    # --- Crear Tests ---
    for _, row in df.iterrows():
        resumen["tests"] += 1
        if pd.notna(row.get("Marca")):
            resumen["marcas"].add(str(row["Marca"]))
        if pd.notna(row.get("Plataforma")):
            resumen["plataformas"].add(str(row["Plataforma"]))
        if pd.notna(row.get("Ambiente")):
            resumen["ambientes"].add(str(row["Ambiente"]))
        resumen["directorios"].add(str(row["Directorio"]))

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

        test_entry["fields"] = {k: v for k, v in test_entry["fields"].items() if v is not None}
        output_json.append(test_entry)

    return {
        "json": json.dumps(output_json, indent=2, ensure_ascii=False),
        "resumen": resumen,
        "testset_details": testset_details
    }



#Forma manual

def generate_manual_xray_json(req, casos):
    """
    req: str -> REQ único ingresado por el usuario
    casos: list[dict] -> lista de casos ingresados manualmente
    """
    output_json = []
    testset_ids = {}
    current_id = 1

    # Crear Test Sets
    for caso in casos:
        ts_name = caso["Test Set"]
        if ts_name not in testset_ids:
            testset_ids[ts_name] = str(current_id)
            etiquetas = [e.strip() for e in caso["Etiquetas"].split(",") if e.strip()]
            output_json.append({
                "xray_issue_type": "testset",
                "xray_id": str(current_id),
                "fields": {
                    "summary": ts_name,
                    "labels": etiquetas
                }
            })
            current_id += 1

    # Crear Tests
    for idx, caso in enumerate(casos):
        flujo_id = f"{req}-{idx+1}"
        etiquetas = [e.strip() for e in caso["Etiquetas"].split(",") if e.strip()]
        test_entry = {
            "xray_issue_type": "test",
            "fields": {
                "summary": caso["Descripción del caso de prueba"],
                "priority": {"name": "High"},
                "description": flujo_id,
                "labels": etiquetas,
                "assignee": {"name": caso["Responsable"]} if caso["Responsable"] else None
            },
            "xray_test_repository_folder": caso["Directorio"],
            "xray_testtype": "Manual",
            "steps": [{
                "action": caso["Pasos para ejecutar"],
                "result": caso["Resultados esperados"],
                "precondiciones": caso["Precondiciones"]
            }],
            "xray_test_sets": [testset_ids[caso["Test Set"]]]
        }
        test_entry["fields"] = {k: v for k, v in test_entry["fields"].items() if v is not None}
        output_json.append(test_entry)

    return json.dumps(output_json, indent=2, ensure_ascii=False)
