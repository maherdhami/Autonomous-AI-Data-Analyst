export interface User {
  user_id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  subscription: string;
  created_at: number;
  last_login: number;
  preferences?: Record<string, any>;
}

export interface FileMetadata {
  file_id: string;
  filename: string;
  size_bytes: number;
  rows: number;
  columns_count: number;
  columns: string[];
}

export interface ChartConfig {
  chart_type: string;
  x_column?: string;
  y_column?: string;
  aggregation?: string;
  title: string;
  business_reason?: string;
  plotly_json?: any;
}

export interface AnalysisData {
  analysis_id: string;
  user_id: string;
  file_metadata: FileMetadata;
  quality_assessment: string;
  business_analysis: string;
  executive_strategy: string;
  quality_score: number;
  charts: ChartConfig[];
  created_at: number;
  dataset_summary?: any;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  code?: string;
  execution_result?: any;
  timestamp: number;
}
