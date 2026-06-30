export function statusBadge(status: string): string {
  const colors: Record<string, string> = {
    pending: "#8b949e",
    queued: "#58a6ff",
    running: "#d29922",
    completed: "#3fb950",
    failed: "#f85149",
    cancelled: "#8b949e",
  };
  const color = colors[status] || "#8b949e";
  return `<span class="badge status-${status}" style="background:${color}22;color:${color};border:1px solid ${color}44">
    ${status}
  </span>`;
}
