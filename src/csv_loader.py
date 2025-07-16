import pandas as pd

class CSVLoader:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = pd.read_csv(self.csv_path, encoding="utf-8-sig").fillna("")

    def get_context(self) -> str:
        context_lines = []
        for _, row in self.df.iterrows():
            line = " | ".join(f"{col.strip()}: {str(row[col]).strip()}" for col in self.df.columns)
            context_lines.append(line)
        return "\n".join(context_lines)
