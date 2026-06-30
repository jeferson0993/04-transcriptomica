export interface PipelineRun {
  id: string;
  name: string;
  status: "pending" | "queued" | "running" | "completed" | "failed" | "cancelled";
  samplesheet_path: string;
  reference: string;
  design_formula: string;
  params: Record<string, unknown> | null;
  nextflow_run_id: string | null;
  output_dir: string | null;
  report_path: string | null;
  deseq2_report_path: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface TranscriptomeRef {
  id: string;
  name: string;
  species: string;
  fasta_path: string;
  gtf_path: string;
  star_index_path: string;
  is_default: boolean;
  created_at: string;
}
