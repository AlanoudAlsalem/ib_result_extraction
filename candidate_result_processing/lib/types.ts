export interface Analytics {
  diploma_totals:      number[];
  courses_totals:      number[];
  avg_diploma:         number;
  avg_courses:         number;
  percent_40_plus:     number;
  subject_averages:    Record<string, number>;
  avg_diploma_subject: number;
  avg_courses_subject: number;
  thresholds:          Record<string, number>;
}

export interface Message {
  type:    'warning' | 'error';
  message: string;
}

export interface StudentRow {
  name:  string;
  total: number;
  [subject: string]: string | number;
}

export interface ExtractionResult {
  diploma_rows: StudentRow[];
  courses_rows: StudentRow[];
  diploma_cols: string[];
  courses_cols: string[];
  analytics:    Analytics;
  messages:     Message[];
  excel_base64: string | null;
}
