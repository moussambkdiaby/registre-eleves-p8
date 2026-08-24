const API_BASE = "http://127.0.0.1:8000";

async function apiFetch(url, options = {}) {
  const reponse = await fetch(`${API_BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!reponse.ok) {
    const erreur = await reponse.json().catch(() => ({ detail: reponse.statusText }));
    throw new Error(erreur.detail || "Erreur inconnue");
  }
  return reponse.json();
}

const api = {
  getEtudiants(params = {}) {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v !== null && v !== undefined)
    ).toString();
    return apiFetch(`/etudiants?${query}`);
  },
  getArchives() {
    return apiFetch(`/etudiants/archives`);
  },
  creerEtudiant(donnees) {
    return apiFetch(`/etudiants`, { method: "POST", body: JSON.stringify(donnees) });
  },
  importerEtudiants(numeros) {
    return apiFetch(`/etudiants/importer`, {
      method: "POST",
      body: JSON.stringify({ numeros }),
    });
  },
  modifierEtudiant(id, champs) {
    return apiFetch(`/etudiants/${id}`, { method: "PATCH", body: JSON.stringify(champs) });
  },
  modifierNote(id, matiere, champs) {
    return apiFetch(`/etudiants/${id}/notes/${matiere}`, {
      method: "PATCH",
      body: JSON.stringify(champs),
    });
  },
  archiverEtudiant(id) {
    return apiFetch(`/etudiants/${id}/archiver`, { method: "PATCH" });
  },
  restaurerEtudiant(id) {
    return apiFetch(`/etudiants/${id}/restaurer`, { method: "PATCH" });
  },
  getStats(route) {
    return apiFetch(`/stats/${route}`);
  },
};