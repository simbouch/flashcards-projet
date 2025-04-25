#!/usr/bin/env python3
import os

# Liste des répertoires à créer
dirs = [
    "ocr_service/src",
    "llm_service/src",
    "db_module",
    "backend_service/src",
    "frontend_service/src/components",
    "frontend_service/src/store",
    "infra/helm-chart",
    ".github/workflows",
]

def main():
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✔️  {d}")

if __name__ == "__main__":
    main()
