# Transcriptomics Pipeline

Pipeline RNA-Seq para expressão diferencial. Entrada: FASTQ → Saída: genes diferencialmente expressos + relatórios.

Orquestrado via Nextflow (nf-core/rnaseq + módulo DESeq2 customizado), com API FastAPI.

## Arquitetura

```
┌──────────┐     ┌──────────────────────┐     ┌──────────────┐
│  FastAPI │────▶│  Nextflow +          │────▶│  PostgreSQL  │
│  (runs,  │     │  nf-core/rnaseq +    │     │  (runs,      │
│  monitor)│     │  DESeq2 custom       │     │   referência)│
└────┬─────┘     └────────┬─────────────┘     └──────────────┘
     │                     │
     │            ┌────────▼───────────┐
     └───────────▶│  MinIO (S3)        │
                  │  samplesheets/     │
                  │  runs/{id}/        │
                  └────────────────────┘
```

## Pipeline (7 estágios)

```
samplesheet.csv (sample,fastq_1,fastq_2,condition,batch)
         │
         ▼
┌─────────────────────────────┐
│  1. FastQC (raw reads)      │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  2. TrimGalore              │  adapter + quality trimming
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  3. FastQC (trimmed reads)  │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  4. STAR 2-pass alignment   │  GRCh38 + Gencode
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  5. featureCounts           │  matriz de contagens gene-level
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  6. MultiQC                 │  QC consolidado
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  7. DESeq2 (R/Bioconductor) │  design: ~batch + condition
├─────────────────────────────┤
│  Saídas:                    │
│  ├── normalized_counts.csv  │
│  ├── deg_results.csv        │  padj, log2FC, baseMean
│  ├── pca_plot.png           │
│  ├── volcano_plot.png       │
│  ├── ma_plot.png            │
│  ├── heatmap.png            │
│  └── deseq2_report.html     │  RMarkdown
└─────────────────────────────┘
```

## Estrutura do Projeto

```
04-transcriptomica/
├── docker-compose.yml
├── .env.example
├── pipeline/
│   ├── main.nf                     # Importa nf-core/rnaseq + deseq2
│   ├── nextflow.config
│   ├── modules/
│   │   └── deseq2/                 # Módulo customizado
│   │       ├── main.nf
│   │       ├── deseq2.R            # DESeq2 script
│   │       ├── report.Rmd          # Template relatório
│   │       └── environment.yml     # Conda/R env
│   ├── conf/
│   │   ├── base.config
│   │   ├── docker.config
│   │   └── grch38.config
│   └── assets/
│       └── samplesheet.csv
├── api/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/                 # PipelineRun, TranscriptomeRef
│   │   ├── schemas/
│   │   ├── api/                    # runs, references
│   │   └── services/               # pipeline_service, minio_service,
│   │                               # monitor_service
│   └── tests/
├── scripts/
│   ├── download-ref-grch38.sh      # FASTA + GTF gencode + STAR index
│   └── setup-env.sh
└── docs/
```

## Pré-requisitos

- Docker + Docker Compose
- Nextflow + Java 17+
- uv (Python) / conda (R environment)

## Setup

```bash
# 1. Configure variáveis de ambiente
cp .env.example .env

# 2. Baixe a referência (GRCh38 + GTF gencode + índice STAR)
docker compose run --rm ref-dl

# 3. Suba os serviços
docker compose up -d

# 4. Verifique o healthcheck
curl http://localhost:8000/health
```

## API — Endpoints

| Método | Caminho | Descrição |
|--------|---------|----------|
| `POST` | `/runs` | Disparar pipeline |
| `GET` | `/runs` | Listar execuções |
| `GET` | `/runs/{id}` | Detalhes + status |
| `GET` | `/runs/{id}/report` | MultiQC report |
| `GET` | `/runs/{id}/deseq2-report` | DESeq2 RMarkdown |
| `GET` | `/runs/{id}/results/{file}` | Download resultado |
| `GET` | `/runs/{id}/logs` | Logs Nextflow |
| `POST` | `/runs/{id}/cancel` | Cancelar |
| `GET` | `/references` | Listar transcriptomas |
| `POST` | `/references` | Registrar referência |

### Disparar pipeline

```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "cohort_rnaseq_01",
    "samplesheet": "minio://samplesheets/cohort_01.csv",
    "reference": "grch38_gencode_v44",
    "design_formula": "~batch + condition"
  }'
```

## Modelo de Dados

### PipelineRun

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID (PK) | Identificador único |
| status | enum | pending → queued → running → completed / failed |
| samplesheet_path | str | Caminho no MinIO |
| reference | str | Transcriptoma de referência |
| design_formula | str | Fórmula do DESeq2 |
| params | JSONB | Parâmetros extras |
| output_dir | str | Diretório de saída |
| deseq2_report_path | str? | Caminho do DESeq2 report |
| nextflow_run_id | str | ID interno do Nextflow |

### TranscriptomeRef

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID (PK) | Identificador único |
| name | str | grch38_gencode_v44 |
| species | str | Homo sapiens |
| fasta_path | str | FASTA transcriptoma |
| gtf_path | str | GTF gencode |
| star_index_path | str | Índice STAR |

## Convenções

- FastQC obrigatório antes e depois do trimming
- STAR 2-pass para melhor detecção de splicing
- Design formula flexível, documentada no run
- Amostras com nomenclatura padronizada (`sample_001`, `sample_002`...)
- Resultados em `runs/{run_id}/` no bucket `processed`
- Seed fixo no R (`set.seed(42)`)
- Normalização DESeq2 median-of-ratios
- p-value, padj (BH) e log2FC reportados para cada gene

## Testes

```bash
uv run pytest api/tests/ -v
```

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Workflow | Nextflow + nf-core/rnaseq |
| Alinhador | STAR 2-pass |
| Quantificação | featureCounts (subread) |
| DE analysis | DESeq2 (R/Bioconductor) |
| QC | FastQC, TrimGalore, MultiQC |
| Relatórios | MultiQC + RMarkdown |
| API | Python 3.12+ / FastAPI |
| ORM | SQLAlchemy 2.0 async |
| Storage | MinIO |
| Database | PostgreSQL 16 |
| Container | Docker |
| Lint / type | ruff, mypy |
# 04-transcriptomica
