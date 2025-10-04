// Pequeño helper para leer cookies en el navegador (solo usado por el cliente)
export function getCookie(name) {
  if (typeof document === "undefined") return null;
  const cookies = document.cookie ? document.cookie.split(";") : [];
  for (let i = 0; i < cookies.length; i++) {
    const part = cookies[i].trim();
    if (!part) continue;
    const eq = part.indexOf("=");
    if (eq === -1) continue;
    const key = decodeURIComponent(part.slice(0, eq));
    const val = decodeURIComponent(part.slice(eq + 1));
    if (key === name) return val;
  }
  return null;
}
