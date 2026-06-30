import { apiGet, apiPost } from "../api/client";
import { statusBadge } from "../components/badge";
import { showToast } from "../components/toast";
import type { PipelineRun } from "../types";

const BASE = "/api/transcriptomics";

export async function renderRunDetail(container: HTMLElement, id: string): Promise<void> {
  container.innerHTML = '<div class="loading">Carregando...</div>';
  try {
    const run = await apiGet<PipelineRun>(`/runs/${id}`);
    let logsHtml = "";
    try {
      const logData = await apiGet<{ logs: string }>(`/runs/${id}/logs`);
      logsHtml = `<h2>Logs</h2><pre class="logs">${logData.logs || "Nenhum log disponível"}</pre>`;
    } catch { }

    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem">
        <h1>${run.name}</h1>
        ${run.status === "pending" || run.status === "queued" || run.status === "running"
          ? `<button class="btn btn-danger" id="btn-cancel">Cancelar Execução</button>`
          : ""}
      </div>
      <div class="card">
        <div class="card-grid">
          <div class="card-item">
            <label>Status</label>
            <div>${statusBadge(run.status)}</div>
          </div>
          <div class="card-item">
            <label>Referência</label>
            <div>${run.reference}</div>
          </div>
          <div class="card-item">
            <label>Design Formula</label>
            <div><code>${run.design_formula}</code></div>
          </div>
          <div class="card-item">
            <label>Samplesheet</label>
            <div style="font-size:0.85rem">${run.samplesheet_path}</div>
          </div>
          ${run.nextflow_run_id ? `<div class="card-item"><label>Nextflow Run ID</label><div>${run.nextflow_run_id}</div></div>` : ""}
          ${run.started_at ? `<div class="card-item"><label>Início</label><div>${new Date(run.started_at).toLocaleString("pt-BR")}</div></div>` : ""}
          ${run.completed_at ? `<div class="card-item"><label>Término</label><div>${new Date(run.completed_at).toLocaleString("pt-BR")}</div></div>` : ""}
          ${run.duration_seconds ? `<div class="card-item"><label>Duração</label><div>${run.duration_seconds}s</div></div>` : ""}
        </div>
      </div>
      ${run.report_path
        ? `<div class="card"><a href="${BASE}/runs/${id}/report" class="btn" target="_blank">Ver Relatório MultiQC</a></div>`
        : ""}
      ${run.deseq2_report_path
        ? `<div class="card"><a href="${BASE}/runs/${id}/deseq2-report" class="btn" target="_blank">Ver Relatório DESeq2</a></div>`
        : ""}
      ${run.error_message ? `<div class="card"><h2>Erro</h2><pre class="logs" style="color:var(--danger)">${run.error_message}</pre></div>` : ""}
      ${logsHtml}
    `;

    const cancelBtn = document.getElementById("btn-cancel");
    if (cancelBtn) {
      cancelBtn.addEventListener("click", async () => {
        if (!confirm("Tem certeza que deseja cancelar esta execução?")) return;
        try {
          await apiPost<PipelineRun>(`/runs/${id}/cancel`, {});
          showToast("Execução cancelada!", "success");
          window.dispatchEvent(new PopStateEvent("popstate"));
        } catch (err) {
          showToast(`Erro ao cancelar: ${err}`, "error");
        }
      });
    }

    if (run.status === "running" || run.status === "queued") {
      setTimeout(() => window.dispatchEvent(new PopStateEvent("popstate")), 10000);
    }
  } catch (err) {
    container.innerHTML = `<div class="empty-state">Execução não encontrada: ${err}</div>`;
  }
}
