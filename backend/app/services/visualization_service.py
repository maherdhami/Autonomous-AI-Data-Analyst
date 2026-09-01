import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm_service import LLMService
from app.utils.chart_generator import generate_plotly_json

prompt3_template = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Business Intelligence Visualization Architect.

Analyze the dataset summary.
Recommend the 5 most important visualizations.
Return ONLY valid JSON format:

{{
  "charts":[
    {{
      "chart_type":"bar",
      "x_column":"",
      "y_column":"",
      "aggregation":"sum",
      "title":"",
      "business_reason":""
    }}
  ]
}}

Supported chart types: bar, line, scatter, pie, histogram, heatmap, boxplot.

Dataset Summary:
{summary}""")
])

class VisualizationService:
    """Service strictly responsible for Output 3: Recommended Visualizations."""

    def generate_visualizations(
        self,
        summary: Dict[str, Any],
        df: pd.DataFrame,
        api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        chart_configs = []
        if api_key and api_key.strip() and not api_key.startswith("gsk_U4QkWe0uvas"):
            try:
                llm = LLMService(api_key=api_key)
                chart_res_text = llm.invoke_chain_with_retry(
                    prompt3_template,
                    {"summary": json.dumps(summary, indent=2)}
                )
                cleaned_json = chart_res_text.strip().replace("```json", "").replace("```", "").strip()
                parsed = json.loads(cleaned_json)
                chart_configs = parsed.get("charts", [])
            except Exception:
                chart_configs = []

        if not chart_configs or len(chart_configs) < 3:
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
            date_cols = summary.get("date_columns", [])
            
            # Select target metrics and dimensions dynamically
            primary_num = num_cols[0] if num_cols else None
            secondary_num = num_cols[1] if len(num_cols) > 1 else primary_num
            primary_cat = cat_cols[0] if cat_cols else None
            secondary_cat = cat_cols[1] if len(cat_cols) > 1 else primary_cat

            chart_configs = []

            # 1. Primary Aggregate Bar Chart (Category vs Metric)
            if primary_cat and primary_num:
                chart_configs.append({
                    "chart_type": "bar",
                    "x_column": primary_cat,
                    "y_column": primary_num,
                    "aggregation": "sum",
                    "title": f"Total {primary_num} Distribution by {primary_cat}",
                    "business_reason": f"Evaluates categorical contribution of {primary_num} across distinct {primary_cat} segments."
                })

            # 2. Proportion / Market Share Donut/Pie Chart
            if primary_cat:
                chart_configs.append({
                    "chart_type": "pie",
                    "x_column": primary_cat,
                    "y_column": primary_num if primary_num else None,
                    "aggregation": "sum" if primary_num else "count",
                    "title": f"Composition Share Across {primary_cat}",
                    "business_reason": f"Visualizes overall concentration and segment share distribution for {primary_cat}."
                })

            # 3. Correlation Scatter Plot (Metric vs Metric)
            if len(num_cols) >= 2:
                chart_configs.append({
                    "chart_type": "scatter",
                    "x_column": primary_num,
                    "y_column": secondary_num,
                    "title": f"{secondary_num} vs {primary_num} Correlation Analysis",
                    "business_reason": f"Inspects linear covariance, cluster grouping, and outlier distribution between {primary_num} and {secondary_num}."
                })

            # 4. Secondary Breakdown or Top Entities Bar Chart
            if secondary_cat and primary_num:
                chart_configs.append({
                    "chart_type": "bar",
                    "x_column": secondary_cat,
                    "y_column": primary_num,
                    "aggregation": "sum",
                    "title": f"Top Performing {secondary_cat} by {primary_num}",
                    "business_reason": f"Identifies highest-velocity driver segments in {secondary_cat} contributing to {primary_num}."
                })

            # 5. Dispersion & Outlier Box Plot
            if (primary_cat or secondary_cat) and (secondary_num or primary_num):
                box_cat = secondary_cat if secondary_cat else primary_cat
                box_num = secondary_num if secondary_num else primary_num
                chart_configs.append({
                    "chart_type": "boxplot",
                    "x_column": box_cat,
                    "y_column": box_num,
                    "title": f"{box_num} Dispersion & Outliers by {box_cat}",
                    "business_reason": f"Uncovers variance range, quartile spreads, and anomalous outlier deviations per {box_cat} group."
                })

            # Fallback if few columns
            if not chart_configs and len(df.columns) > 0:
                first_col = df.columns[0]
                second_col = df.columns[1] if len(df.columns) > 1 else None
                chart_configs.append({
                    "chart_type": "bar",
                    "x_column": first_col,
                    "y_column": second_col,
                    "title": f"Distribution of {first_col}",
                    "business_reason": "Baseline exploratory data distribution."
                })

        charts_list = []
        for c in chart_configs:
            plotly_json = generate_plotly_json(df, c)
            if plotly_json:
                c["plotly_json"] = plotly_json
                charts_list.append(c)

        return charts_list

visualization_service = VisualizationService()
