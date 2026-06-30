import { apiGet, apiPost } from "../api/client";
import { showToast } from "../components/toast";
import type { PipelineRun, TranscriptomeRef } from "../types";

const BASE = "/transcriptomics";

export async function renderRunCreate(container: HTMLElement): Promise<void> {
  container.innerHTML = '<div class="loading">Carregando...</div>';
  try {
    const refs = await apiGet<TranscriptomeRef[]>("/references");
    const refOptions = refs
      .map(r => `<option value="${r.name}" ${r.is_default ? "selected" : ""}>${r.name} (${r.species})</option>`)
      .join("");

    container.innerHTML = `
      <h1>Nova Execução</h1>
      <div class="card">
        <form id="run-form">
          <div class="form-group">
            <label for="name">Nome</label>
            <input type="text" id="name" name="name" required placeholder="cohort_rnaseq_01" />
          </div>
          <div class="form-group">
            <label for="samplesheet_path">Samplesheet (caminho MinIO)</label>
            <input type="text" id="samplesheet_path" name="samplesheet_path" required placeholder="minio://samplesheets/cohort_01.csv" />
          </div>
          <div class="form-group">
            <label for="reference">Referência</label>
            <select id="reference" name="reference" required>
              <option value="">Selecione...</option>
              ${refOptions}
            </select>
          </div>
          <div class="form-group">
            <label for="design_formula">Design Formula</label>
            <input type="text" id="design_formula" name="design_formula" value="~condition" placeholder="~batch + condition" />
          </div>
          <div class="form-group">
            <label for="params">Parâmetros Extras (JSON)</label>
            <textarea id="params" name="params" rows="4" placeholder='{"min_count": 10, "lfc_threshold": 1.0}'></textarea>
          </div>
          <button type="submit" class="btn btn-primary">Disparar Pipeline</button>
        </form>
      </div>
    `;

    document.getElementById("run-form")!.addEventListener("submit", async (e) => {
      e.preventDefault();
      const form = e.target as HTMLFormElement;
      const data = {
        name: (form.elements.namedItem("name") as HTMLInputElement).value,
        samplesheet_path: (form.elements.namedItem("samplesheet_path") as HTMLInputElement).value,
        reference: (form.elements.namedItem("reference") as HTMLSelectElement).value,
        design_formula: (form.elements.namedItem("design_formula") as HTMLInputElement).value,
        params: JSON.parse((form.elements.namedItem("params") as HTMLTextAreaElement).value || "{}"),
      };
      try {
        const run = await apiPost<PipelineRun>("/runs", data);
        showToast(`Execução "${run.name}" iniciada!`, "success");
        history.pushState(null, "", `${BASE}/runs/${run.id}`);
        window.dispatchEvent(new PopStateEvent("popstate"));
      } catch (err) {
        showToast(`Erro: ${err}`, "error");
      }
    });
  } catch (err) {
    container.innerHTML = `<div class="empty-state">Erro ao carregar referências: ${err}</div>`;
  }
}
