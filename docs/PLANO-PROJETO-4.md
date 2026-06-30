# Plano de Implementação — Projeto 4: Transcriptomics Pipeline

## Visão Geral

Pipeline RNA-Seq para expressão diferencial.

Entrada: FASTQ (paired-end) → Saída: genes diferencialmente expressos + relatórios.

Orquestrado via Nextflow (nf-core/rnaseq + módulo DESeq2 customizado),
com API FastAPI para disparo e monitoramento. Repositório **independente**.

---

## Escopo

| Item | Incluído |
|---|---|
| Alinhamento | STAR 2-pass |
| Quantificação | featureCounts (gene-level) |
| Expressão diferencial | DESeq2 (R), design formula flexível (multi-grupo) |
| Controle de qualidade | FastQC, TrimGalore, MultiQC |
| Saídas | Matriz de contagens, DEG tables, PCA, volcano/MA plots |
| API REST | Disparar runs, consultar status, baixar resultados |
| Referência | GRCh38 + GTF gencode + índice STAR |
| Execução | CLI (Nextflow) + API FastAPI |

---

## Stack

| Área | Tecnologia |
|---|---|
| Workflow base | Nextflow + nf-core/rnaseq |
| Alinhador | STAR 2-pass |
| Quantificação | featureCounts (subread) |
| DE analysis | DESeq2 (R/Bioconductor) |
| QC | FastQC, TrimGalore, MultiQC |
| Relatórios | MultiQC + RMarkdown (DESeq2 report) |
| Orquestração | Python, FastAPI, SQLAlchemy async |
| Container | Docker (nf-core/modules) |
| Gerenciador | uv (API Python), renv (R) |

---

## Estrutura de Diretórios

```
projeto4-transcriptomica/
├── docker-compose.yml
├── .env.example
│
├── pipeline/                    # Nextflow pipeline
│   ├── main.nf                  # Importa nf-core/rnaseq + módulo deseq2
│   ├── nextflow.config
│   ├── modules/
│   │   └── deseq2/              # Módulo customizado para DE
│   │       ├── main.nf
│   │       ├── deseq2.R         # Script R com DESeq2
│   │       ├── report.Rmd       # Template de relatório
│   │       └── environment.yml  # Conda/R env
│   ├── conf/
│   │   ├── base.config
│   │   ├── docker.config
│   │   └── grch38.config        # Referência transcriptoma
│   └── assets/
│       └── samplesheet.csv      # sample,fastq_1,fastq_2,condition,batch
│
├── api/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── run.py           # PipelineRun ORM
│   │   │   └── reference.py     # TranscriptomeRef ORM
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── run.py
│   │   │   └── reference.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── runs.py
│   │   │   └── references.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── pipeline_service.py
│   │       ├── minio_service.py
│   │       └── monitor_service.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_api/
│       └── test_services/
│
├── scripts/
│   ├── download-ref-grch38.sh   # FASTA + GTF gencode + STAR index
│   └── setup-env.sh
│
└── docs/
    └── README.md
```

---

## Pipeline (estágios)

```
samplesheet.csv (sample,fastq_1,fastq_2,condition,batch)
         │
         ▼
┌─────────────────────────────┐
│  1. FastQC (raw)            │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  2. TrimGalore              │  adapter + quality trimming
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  3. FastQC (trimmed)        │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  4. STAR 2-pass alignment   │  genome + transcriptome
│     (BAM por amostra)       │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  5. featureCounts           │  gene-level count matrix
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  6. MultiQC                 │  QC consolidado
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│  7. DESeq2                  │  normalização + DE
│     (R/Bioconductor)        │  design: ~batch + condition
├─────────────────────────────┤
│  Saídas:                    │
│  ├── normalized_counts.csv  │
│  ├── deg_results.csv        │  (padj, log2FC, baseMean)
│  ├── pca_plot.png           │
│  ├── volcano_plot.png       │
│  ├── ma_plot.png            │
│  ├── heatmap.png            │
│  └── deseq2_report.html     │  RMarkdown
└─────────────────────────────┘
```

---

## Modelo de Dados

### PipelineRun

| Campo | Tipo | Descrição |
|---|---|---|
| id | UUID (PK) | Identificador único |
| name | str | Nome da execução |
| status | enum(pending, queued, running, completed, failed, cancelled) | Estado |
| samplesheet_path | str | Samplesheet no MinIO |
| reference | str | Transcriptoma de referência |
| design_formula | str | Ex: `~batch + condition` |
| params | JSONB | Parâmetros extras |
| nextflow_run_id | str | ID do Nextflow |
| output_dir | str | Diretório de saída no MinIO |
| report_path | str? | MultiQC report |
| deseq2_report_path | str? | DESeq2 report |
| started_at | timestamptz | Início |
| completed_at | timestamptz? | Término |
| error_message | text? | Erro se falhou |

### TranscriptomeRef

| Campo | Tipo | Descrição |
|---|---|---|
| id | UUID (PK) | Identificador único |
| name | str | grch38_gencode_vXX |
| species | str | Homo sapiens |
| fasta_path | str | FASTA transcriptoma |
| gtf_path | str | GTF gencode |
| star_index_path | str | Índice STAR |
| is_default | bool | Padrão |
| created_at | timestamptz | Data de registro |

---

## Endpoints da API

| Método | Caminho | Descrição |
|---|---|---|
| `POST` | `/runs` | Disparar pipeline (body: samplesheet, reference, design_formula, params) |
| `GET` | `/runs` | Listar execuções |
| `GET` | `/runs/{id}` | Detalhes + status |
| `GET` | `/runs/{id}/report` | MultiQC report |
| `GET` | `/runs/{id}/deseq2-report` | DESeq2 RMarkdown report |
| `GET` | `/runs/{id}/results/{file}` | Baixar arquivo de resultado |
| `GET` | `/runs/{id}/logs` | Logs Nextflow |
| `POST` | `/runs/{id}/cancel` | Cancelar |
| `GET` | `/references` | Listar transcriptomas |
| `POST` | `/references` | Registrar referência |
| `GET` | `/health` | Healthcheck |

---

## Docker Compose

```yaml
services:
  api:         # FastAPI, porta 8000
  postgres:    # postgres:16-alpine
  minio:       # minio/minio, portas 9000/9001
  ref-dl:      # one-shot: download GRCh38 + GTF gencode + STAR index
```

---

## Fases de Implementação

### Fase 1 — Fundação (dias 1-2)

- `pipeline/` — `main.nf` importando nf-core/rnaseq, `nextflow.config`
- Módulo custom `deseq2/` (main.nf, deseq2.R, report.Rmd, environment.yml)
- `api/` — FastAPI scaffold, models (PipelineRun, TranscriptomeRef)
- `docker-compose.yml` — api, postgres, minio
- Script `download-ref-grch38.sh` — FASTA + GTF gencode + STAR index
- `.env.example`

### Fase 2 — Pipeline Nextflow (dias 3-6)

- Configuração nf-core/rnaseq (samplesheet, parâmetros STAR, featureCounts)
- Módulo DESeq2 custom:
  - `deseq2.R` — lê count matrix, design formula, executa DESeq2
  - Gera: normalized counts, DEG table, PCA, volcano, MA, heatmap
  - `report.Rmd` — relatório parametrizado
- Teste com dados sintéticos (chr22 RNA-Seq simulado)

### Fase 3 — API + Orquestração (dias 7-9)

- `services/pipeline_service.py` — `nextflow run` via subprocess async
- `services/monitor_service.py` — poll trace + log parsing
- `services/minio_service.py` — upload/download
- `api/runs.py` — CRUD + cancel
- `api/references.py` — listar/registrar transcriptomas

### Fase 4 — Qualidade (dias 10-11)

- Ruff + mypy
- Testes unitários (mock Nextflow)
- Teste de integração com dados sintéticos
- README.md com setup, parâmetros, arquitetura

---

## Convenções

- **Código**: identificadores em inglês
- **Documentação**: português brasileiro
- **QC obrigatório**: FastQC antes/depois do trimming, MultiQC final
- **STAR 2-pass**: necessário para melhor detecção de splicing
- **Design formula**: flexível (`~condition`, `~batch+condition`), documentada no run
- **Nomenclatura**: amostras padronizadas (`sample_001`, `sample_002`...)
- **Resultados**: `runs/{run_id}/` no MinIO, bucket `processed`
- **Imutabilidade**: dados brutos nunca alterados
- **Reprodutibilidade**: seed fixo no R (`set.seed(42)`), parâmetros registrados
- **Normalização**: DESeq2 median-of-ratios (padrão), documentar critérios de exclusão
- **Estatística**: reportar p-value, padj (BH), log2FC para cada gene
