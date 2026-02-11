"""Gera sample_input.xlsx para demonstração."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def main():
    from datetime import datetime, timedelta
    import random

    categorias = ["Varejo", "Atacado", "E-commerce", "Serviços", "Outros"]
    produtos = ["Produto A", "Produto B", "Produto C", "Produto D", "Produto E"]
    base = datetime(2024, 1, 1)
    rows = []
    for i in range(120):
        data = base + timedelta(days=random.randint(0, 364))
        cat = random.choice(categorias)
        prod = random.choice(produtos)
        valor = round(random.uniform(100, 5000), 2)
        qtd = random.randint(1, 50)
        rows.append({
            "Data": data,
            "Categoria": cat,
            "Produto": prod,
            "Valor": valor,
            "Quantidade": qtd,
        })
    df = pd.DataFrame(rows)
    out = ROOT / "input" / "sample_input.xlsx"
    ROOT.mkdir(exist_ok=True)
    (ROOT / "input").mkdir(exist_ok=True)
    df.to_excel(out, index=False, sheet_name="Vendas")
    print("Gerado:", out)

if __name__ == "__main__":
    main()
