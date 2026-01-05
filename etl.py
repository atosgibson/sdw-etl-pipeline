import os
import json
from typing import Any, Dict, List

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_IDS = "data/SDW2023.csv"     # CSV com coluna UserID (ou id)
INPUT_FULL = "data/users.csv"      # CSV completo (modo offline)
OUT_DIR = "output"
OUT_JSON = os.path.join(OUT_DIR, "users_enriched.json")
OUT_CSV = os.path.join(OUT_DIR, "messages.csv")


def read_user_ids(csv_path: str) -> List[int]:
    df = pd.read_csv(csv_path)
    for col in ["UserID", "user_id", "id"]:
        if col in df.columns:
            return [int(x) for x in df[col].dropna().tolist()]
    raise ValueError("Coluna de IDs não encontrada. Use UserID (ou id/user_id).")


def read_users_from_full_csv(csv_path: str) -> List[Dict[str, Any]]:
    df = pd.read_csv(csv_path)
    return df.to_dict(orient="records")


def build_prompt(user: Dict[str, Any]) -> str:
    name = user.get("name") or user.get("Nome") or "Cliente"
    balance = user.get("balance") or user.get("Saldo")
    limit_ = user.get("limit") or user.get("Limite")
    return (
        f"Crie uma mensagem curta (até 280 caracteres), amigável e personalizada para {name}. "
        f"Se possível, mencione educação financeira. Contexto: saldo={balance}, limite={limit_}. "
        f"Evite promessas irreais e linguagem agressiva."
    )


def generate_message(prompt: str) -> str:
    resp = client.responses.create(
        model="gpt-4o-mini",
        instructions="Você é um redator de marketing bancário. Escreva em PT-BR, tom humano e claro.",
        input=prompt,
    )
    return resp.output_text.strip()


def attach_message(user: Dict[str, Any], message: str) -> Dict[str, Any]:
    # padroniza campos
    if "name" not in user and "Nome" in user:
        user["name"] = user["Nome"]
    user["message"] = message
    return user


def save_outputs(users: List[Dict[str, Any]]) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

    df = pd.DataFrame(
        [{"name": u.get("name", ""), "message": u.get("message", "")} for u in users]
    )
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")


def main():
    # Modo 1: CSV completo (offline)
    if os.path.exists(INPUT_FULL):
        users = read_users_from_full_csv(INPUT_FULL)

    # Modo 2: CSV só com IDs (vai criar usuários fictícios com base no ID)
    elif os.path.exists(INPUT_IDS):
        ids = read_user_ids(INPUT_IDS)
        users = [{"id": uid, "name": f"Cliente {uid}"} for uid in ids]

    else:
        raise FileNotFoundError("Crie data/users.csv (completo) OU data/SDW2023.csv (com IDs).")

    enriched = []
    for user in users:
        prompt = build_prompt(user)
        msg = generate_message(prompt)
        enriched.append(attach_message(user, msg))

    save_outputs(enriched)
    print(f"OK! Processados: {len(enriched)}")
    print(f"Gerados: {OUT_JSON} e {OUT_CSV}")


if __name__ == "__main__":
    main()
