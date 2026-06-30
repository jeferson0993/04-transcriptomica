import { apiGet, apiPost } from "../api/client";
import { showToast } from "../components/toast";
import type { TranscriptomeRef } from "../types";

export async function renderReferences(container: HTMLElement): Promise<void> {
  container.innerHTML = '<div class="loading">Carregando...</div>';
  try {
    const refs = await apiGet<TranscriptomeRef[]>("/references");
    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem">
        <h1>Referências</h1>
        <button class="btn btn-primary" id="btn-show-form">Nova Referência</button>
      </div>
      <div id="ref-form" style="display:none" class="card">
        <form id="reference-form">
          <div class="form-group">
            <label for="name">Nome</label>
            <input type="text" id="name" name="name" required placeholder="grch38_gencode_v44" />
          </div>
          <div class="form-group">
            <label for="species">Espécie</label>
            <input type="text" id="species" name="species" value="Homo sapiens" />
          </div>
          <div class="form-group">
            <label for="fasta_path">Caminho FASTA</label>
            <input type="text" id="fasta_path" name="fasta_path" required placeholder="/ref/grch38/genome.fa" />
          </div>
          <div class="form-group">
            <label for="gtf_path">Caminho GTF</label>
            <input type="text" id="gtf_path" name="gtf_path" required placeholder="/ref/grch38/gencode.v44.annotation.gtf" />
          </div>
          <div class="form-group">
            <label for="star_index_path">Caminho Índice STAR</label>
            <input type="text" id="star_index_path" name="star_index_path" required placeholder="/ref/grch38/star_index" />
          </div>
          <div class="form-group">
            <label>
              <input type="checkbox" id="is_default" name="is_default" />
              Referência padrão
            </label>
          </div>
          <button type="submit" class="btn btn-primary">Registrar</button>
          <button type="button" class="btn" id="btn-cancel-form">Cancelar</button>
        </form>
      </div>
      ${refs.length === 0
        ? '<div class="empty-state">Nenhuma referência registrada</div>'
        : `
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Espécie</th>
              <th>FASTA</th>
              <th>GTF</th>
              <th>Padrão</th>
              <th>Criada em</th>
            </tr>
          </thead>
          <tbody>
            ${refs.map(ref => `
              <tr>
                <td>${ref.name}</td>
                <td><em>${ref.species}</em></td>
                <td style="font-size:0.8rem">${ref.fasta_path}</td>
                <td style="font-size:0.8rem">${ref.gtf_path}</td>
                <td>${ref.is_default ? "✅" : ""}</td>
                <td>${new Date(ref.created_at).toLocaleString("pt-BR")}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `}
    `;

    document.getElementById("btn-show-form")!.addEventListener("click", () => {
      document.getElementById("ref-form")!.style.display = "block";
    });
    document.getElementById("btn-cancel-form")!.addEventListener("click", () => {
      document.getElementById("ref-form")!.style.display = "none";
    });
    document.getElementById("reference-form")!.addEventListener("submit", async (e) => {
      e.preventDefault();
      const form = e.target as HTMLFormElement;
      const data = {
        name: (form.elements.namedItem("name") as HTMLInputElement).value,
        species: (form.elements.namedItem("species") as HTMLInputElement).value,
        fasta_path: (form.elements.namedItem("fasta_path") as HTMLInputElement).value,
        gtf_path: (form.elements.namedItem("gtf_path") as HTMLInputElement).value,
        star_index_path: (form.elements.namedItem("star_index_path") as HTMLInputElement).value,
        is_default: (form.elements.namedItem("is_default") as HTMLInputElement).checked,
      };
      try {
        await apiPost("/references", data);
        showToast("Referência registrada!", "success");
        window.dispatchEvent(new PopStateEvent("popstate"));
      } catch (err) {
        showToast(`Erro: ${err}`, "error");
      }
    });
  } catch (err) {
    container.innerHTML = `<div class="empty-state">Erro ao carregar referências: ${err}</div>`;
  }
}
