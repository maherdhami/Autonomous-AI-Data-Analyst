import json
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional


class ChatService:
    def run_code(self, df: pd.DataFrame, question: str) -> Tuple[str, Any]:
        """Mode 1: Run pandas code on the dataset and return (code, result)."""
        code = self._build_pandas_code(df, question)
        try:
            local_vars = {"df": df, "pd": pd, "np": np}
            exec(code, {}, local_vars)
            result = local_vars.get("result", "No result variable found.")
            # Convert pandas types to plain Python
            if isinstance(result, pd.DataFrame):
                result = result.head(10).to_dict(orient="records")
            elif isinstance(result, pd.Series):
                result = result.to_dict()
            elif isinstance(result, (np.floating,)):
                result = round(float(result), 2)
            elif isinstance(result, (np.integer,)):
                result = int(result)
        except Exception as e:
            result = f"Error: {e}"
        return code, result

    def answer_question(self, summary: Dict[str, Any], df: Optional[pd.DataFrame], question: str) -> str:
        """Mode 2: Answer a question using dataset summary stats."""
        rows = summary.get("rows", 0)
        cols = summary.get("columns", [])
        num_cols = summary.get("numerical_columns", [])
        cat_cols = summary.get("categorical_columns", [])

        # Run code to get a computed answer
        if df is not None and len(df) > 0:
            _, result = self.run_code(df, question)
            computed = f"`{result}`" if result else "N/A"
        else:
            computed = "No dataset loaded."

        return (
            f"**Answer:** {computed}\n\n"
            f"**Dataset:** {rows:,} rows × {len(cols)} columns\n"
            f"**Numeric columns:** {', '.join(num_cols[:6]) or 'None'}\n"
            f"**Category columns:** {', '.join(cat_cols[:6]) or 'None'}\n\n"
            f"*Tip: Switch to Code mode for precise calculations.*"
        )

    def _build_pandas_code(self, df: pd.DataFrame, question: str) -> str:
        """Build simple pandas code based on keywords in the question."""
        q = question.lower()
        cols = df.columns.tolist()
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        # Pick a numeric column mentioned in the question, or use first
        metric = next((c for c in num_cols if c.lower() in q), num_cols[0] if num_cols else None)
        # Pick a category column mentioned in the question, or use first
        dim = next((c for c in cat_cols if c.lower() in q), cat_cols[0] if cat_cols else None)

        # Top N
        import re
        top_match = re.search(r"top\s+(\d+)", q)
        if top_match and metric:
            n = int(top_match.group(1))
            id_col = cols[0]
            return f"result = df.nlargest({n}, '{metric}')[['{id_col}', '{metric}']].reset_index(drop=True)"

        # Group by
        if dim and metric and any(k in q for k in ["by ", "per ", "each ", "breakdown", "across"]):
            agg = "mean" if any(k in q for k in ["average", "mean", "avg"]) else "sum"
            return f"result = df.groupby('{dim}')['{metric}'].{agg}().round(2).reset_index()"

        # Max
        if any(k in q for k in ["highest", "max", "maximum", "largest", "most", "top", "best"]):
            if metric:
                return f"result = df.loc[df['{metric}'].idxmax()].to_dict()"

        # Min
        if any(k in q for k in ["lowest", "min", "minimum", "smallest", "least", "worst"]):
            if metric:
                return f"result = df.loc[df['{metric}'].idxmin()].to_dict()"

        # Average
        if any(k in q for k in ["average", "mean", "avg"]):
            if metric:
                return f"result = round(float(df['{metric}'].mean()), 2)"
            return "result = df.select_dtypes(include='number').mean().round(2).to_dict()"

        # Sum / Total
        if any(k in q for k in ["total", "sum", "overall"]):
            if metric:
                return f"result = round(float(df['{metric}'].sum()), 2)"
            return "result = df.select_dtypes(include='number').sum().round(2).to_dict()"

        # Correlation
        if any(k in q for k in ["correlation", "corr", "relationship"]):
            return "result = df.select_dtypes(include='number').corr().round(3).to_dict()"

        # Unique values
        if any(k in q for k in ["unique", "distinct"]) and dim:
            return f"result = df['{dim}'].unique().tolist()"

        # Count
        if "count" in q or "how many" in q:
            if dim:
                return f"result = df['{dim}'].value_counts().to_dict()"
            return "result = len(df)"

        # Default: describe
        if metric:
            return f"result = df['{metric}'].describe().round(2).to_dict()"
        return "result = df.head(5).to_dict(orient='records')"


chat_service = ChatService()