import "./style.css";

import { renderRunsList } from "./pages/runs-list";
import { renderRunCreate } from "./pages/run-create";
import { renderRunDetail } from "./pages/run-detail";
import { renderReferences } from "./pages/references";

const BASE = "/transcriptomics";

function route(): void {
  const path = location.pathname.replace(BASE, "") || "/";
  const main = document.getElementById("main-content")!;

  if (path === "/" || path === "") {
    renderRunsList(main);
  } else if (path === "/runs/new") {
    renderRunCreate(main);
  } else if (path.startsWith("/runs/")) {
    const id = path.replace("/runs/", "");
    renderRunDetail(main, id);
  } else if (path === "/references") {
    renderReferences(main);
  } else {
    main.innerHTML = "<h1>404 — Página não encontrada</h1>";
  }
}

window.addEventListener("popstate", route);
document.addEventListener("click", (e) => {
  const link = (e.target as HTMLElement).closest("[data-nav]");
  if (link) {
    e.preventDefault();
    const href = (link as HTMLAnchorElement).getAttribute("href")!;
    history.pushState(null, "", href);
    route();
  }
});

route();
