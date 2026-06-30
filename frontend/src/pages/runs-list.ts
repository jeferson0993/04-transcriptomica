import { apiGet } from "../api/client";
import { statusBadge } from "../components/badge";
import type { PipelineRun } from "../types";

const BASE = "/transcriptomics";

export async function renderRunsList(container: HTMLElement): Promise<void> {
  container.innerHTML = '<div class="loading">Carregando...</div>';
  try {
    const data = await apiGet<{ items: PipelineRun[]; total: number }>("/runs");
    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem">
        <h1>Execuções</h1>
        <a href="${BASE}/runs/new" class="btn btn-primary" data-nav>Nova Execução</a>
      </div>
      ${data.items.length === 0
        ? '<div class="empty-state">Nenhuma execução encontrada</div>'
        : `
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Status</th>
              <th>Referência</th>
              <th>Design</th>
              <th>Criada em</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            ${data.items.map(run => `
              <tr>
                <td>${run.name}</td>
                <td>${statusBadge(run.status)}</td>
                <td>${run.reference}</td>
                <td><code>${run.design_formula}</code></td>
                <td>${new Date(run.created_at).toLocaleString("pt-BR")}</td>
                <td><a href="${BASE}/runs/${run.id}" class="btn btn-sm" data-nav>Detalhes</a></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
        <p style="margin-top:1rem;color:var(--text-muted);font-size:0.85rem">Total: ${data.total} execuções</p>
      `}
    `;
  } catch (err) {
    container.innerHTML = `<div class="empty-state">Erro ao carregar execuções: ${err}</div>`;
  }
}
