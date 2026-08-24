const etat = {
  page: 1,
  limite: 5,
  filtres: { nom: "", numero: "", classe: "" },
  selectionJson: new Set(),
  vue: "liste",
};

const els = {
  corps: document.getElementById("corpsRegistre"),
  pageInfo: document.getElementById("pageInfo"),
  pagePrecedente: document.getElementById("pagePrecedente"),
  pageSuivante: document.getElementById("pageSuivante"),
  selectionCompteur: document.getElementById("selectionCompteur"),
  btnImporter: document.getElementById("btnImporter"),
  toutSelectionner: document.getElementById("toutSelectionner"),
  statTotal: document.getElementById("statTotal"),
  statDb: document.getElementById("statDb"),
  statJson: document.getElementById("statJson"),
};

function mentionClasse(moyenne) {
  if (moyenne === null || moyenne === undefined) return "";
  if (moyenne >= 16) return "mention-excellent";
  if (moyenne >= 12) return "mention-bien";
  if (moyenne < 8) return "mention-faible";
  return "";
}

function ligneHTML(e) {
  const estJson = e.source === "JSON";
  const checkbox = estJson
    ? `<input type="checkbox" class="case-json" data-numero="${e.numero}" ${etat.selectionJson.has(e.numero) ? "checked" : ""}>`
    : "";

  const moyenne = e.moyenne_generale ?? "—";
  const classeMoyenne = mentionClasse(e.moyenne_generale);

  const actions = estJson
    ? `<span class="encre-douce">lecture seule</span>`
    : `<button class="bouton bouton-fantome btn-archiver" data-id="${e.id}">Archiver</button>`;

  return `
    <tr data-id="${e.id ?? ""}" data-numero="${e.numero}" data-source="${e.source}">
      <td class="col-check">${checkbox}</td>
      <td class="numero">${e.numero}</td>
      <td class="${!estJson ? "cellule-editable" : ""}" data-champ="nom">${e.nom}</td>
      <td class="${!estJson ? "cellule-editable" : ""}" data-champ="prenom">${e.prenom}</td>
      <td class="${!estJson ? "cellule-editable" : ""}" data-champ="classe">${e.classe}</td>
      <td class="moyenne">
        <span class="pastille-moyenne ${classeMoyenne}">${moyenne}</span>
      </td>
      <td><span class="tampon tampon-${estJson ? "json" : "db"}">${e.source}</span></td>
      <td class="col-actions">${actions}</td>
    </tr>
  `;
}

async function chargerListe() {
  els.corps.innerHTML = `<tr class="ligne-chargement"><td colspan="8">Chargement du registre…</td></tr>`;

  try {
    const params = {
      page: etat.page,
      limite: etat.limite,
      nom: etat.filtres.nom,
      numero: etat.filtres.numero,
      classe: etat.filtres.classe,
    };
    const data = await api.getEtudiants(params);

    if (data.resultats.length === 0) {
      els.corps.innerHTML = `<tr class="ligne-vide"><td colspan="8">Aucun élève ne correspond à cette recherche.</td></tr>`;
    } else {
      els.corps.innerHTML = data.resultats.map(ligneHTML).join("");
    }

    const totalPages = Math.max(1, Math.ceil(data.total / data.limite));
    els.pageInfo.textContent = `Page ${data.page} / ${totalPages} — ${data.total} élève(s)`;
    els.pagePrecedente.disabled = data.page <= 1;
    els.pageSuivante.disabled = data.page >= totalPages;

    attacherEvenementsLignes();
    mettreAJourCompteurSelection();
  } catch (err) {
    els.corps.innerHTML = `<tr class="ligne-vide"><td colspan="8">Erreur de chargement : ${err.message}</td></tr>`;
  }
}

async function chargerStatsRapides() {
  try {
    const kpis = await api.getStats("kpis");
    els.statTotal.textContent = kpis.total_donnees;
    els.statDb.textContent = kpis.nombre_db;
    els.statJson.textContent = kpis.nombre_json;
  } catch (err) {
    console.error("Impossible de charger les KPIs :", err);
  }
}

async function chargerClasses() {
  try {
    const stats = await api.getStats("repartition-classe");
    const select = document.getElementById("rechClasse");
    stats.resultats.forEach((r) => {
      const option = document.createElement("option");
      option.value = r.classe;
      option.textContent = r.classe;
      select.appendChild(option);
    });
  } catch (err) {
    console.error("Impossible de charger les classes :", err);
  }
}

function attacherEvenementsLignes() {
  document.querySelectorAll(".case-json").forEach((cb) => {
    cb.addEventListener("change", (e) => {
      const numero = e.target.dataset.numero;
      if (e.target.checked) etat.selectionJson.add(numero);
      else etat.selectionJson.delete(numero);
      mettreAJourCompteurSelection();
    });
  });

  document.querySelectorAll(".btn-archiver").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const id = e.target.dataset.id;
      if (!confirm("Archiver cet élève ?")) return;
      try {
        await api.archiverEtudiant(id);
        chargerListe();
        chargerStatsRapides();
      } catch (err) {
        alert("Erreur : " + err.message);
      }
    });
  });

  document.querySelectorAll(".cellule-editable").forEach((cell) => {
    cell.addEventListener("dblclick", () => activerEditionCellule(cell));
  });
}

function activerEditionCellule(cell) {
  const valeurActuelle = cell.textContent.trim();
  const champ = cell.dataset.champ;
  const ligne = cell.closest("tr");
  const id = ligne.dataset.id;

  cell.innerHTML = `<input type="text" value="${valeurActuelle}">`;
  const input = cell.querySelector("input");
  input.focus();
  input.select();

  const valider = async () => {
    const nouvelleValeur = input.value.trim();
    if (nouvelleValeur === valeurActuelle || nouvelleValeur === "") {
      cell.textContent = valeurActuelle;
      return;
    }
    try {
      await api.modifierEtudiant(id, { [champ]: nouvelleValeur });
      cell.textContent = nouvelleValeur;
    } catch (err) {
      alert("Erreur : " + err.message);
      cell.textContent = valeurActuelle;
    }
  };

  input.addEventListener("blur", valider);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") input.blur();
    if (e.key === "Escape") {
      cell.textContent = valeurActuelle;
    }
  });
}

function mettreAJourCompteurSelection() {
  const n = etat.selectionJson.size;
  els.selectionCompteur.textContent = `${n} sélectionné(s)`;
  els.btnImporter.disabled = n === 0;
}

// --- Événements globaux ---

document.getElementById("rechNom").addEventListener("input", debounce((e) => {
  etat.filtres.nom = e.target.value;
  etat.page = 1;
  chargerListe();
}, 400));

document.getElementById("rechNumero").addEventListener("input", debounce((e) => {
  etat.filtres.numero = e.target.value;
  etat.page = 1;
  chargerListe();
}, 400));

document.getElementById("rechClasse").addEventListener("change", (e) => {
  etat.filtres.classe = e.target.value;
  etat.page = 1;
  chargerListe();
});

document.getElementById("rechLimite").addEventListener("change", (e) => {
  etat.limite = parseInt(e.target.value, 10);
  etat.page = 1;
  chargerListe();
});

document.getElementById("btnReinitialiser").addEventListener("click", () => {
  etat.filtres = { nom: "", numero: "", classe: "" };
  etat.page = 1;
  document.getElementById("rechNom").value = "";
  document.getElementById("rechNumero").value = "";
  document.getElementById("rechClasse").value = "";
  chargerListe();
});

els.pagePrecedente.addEventListener("click", () => {
  etat.page--;
  chargerListe();
});

els.pageSuivante.addEventListener("click", () => {
  etat.page++;
  chargerListe();
});

els.btnImporter.addEventListener("click", async () => {
  const numeros = Array.from(etat.selectionJson);
  try {
    const resultat = await api.importerEtudiants(numeros);
    let message = `${resultat.importes} élève(s) importé(s).`;
    if (resultat.ignores > 0) message += ` ${resultat.ignores} déjà en base.`;
    if (resultat.anomalies?.length > 0) message += ` ⚠ ${resultat.anomalies.length} anomalie(s) de notes détectée(s).`;
    alert(message);
    etat.selectionJson.clear();
    chargerListe();
    chargerStatsRapides();
  } catch (err) {
    alert("Erreur d'import : " + err.message);
  }
});

// --- Modale d'ajout ---

const modaleFond = document.getElementById("modaleFond");

document.getElementById("btnAjouter").addEventListener("click", () => {
  modaleFond.classList.add("ouverte");
});

document.getElementById("btnAnnulerAjout").addEventListener("click", () => {
  modaleFond.classList.remove("ouverte");
});

modaleFond.addEventListener("click", (e) => {
  if (e.target === modaleFond) modaleFond.classList.remove("ouverte");
});

document.getElementById("formAjout").addEventListener("submit", async (e) => {
  e.preventDefault();
  const donnees = Object.fromEntries(new FormData(e.target).entries());
  donnees.notes = {};
  try {
    await api.creerEtudiant(donnees);
    modaleFond.classList.remove("ouverte");
    e.target.reset();
    chargerListe();
    chargerStatsRapides();
  } catch (err) {
    alert("Erreur : " + err.message);
  }
});

// --- Utilitaire : anti-rebond pour la recherche ---
function debounce(fn, delai) {
  let minuteur;
  return (...args) => {
    clearTimeout(minuteur);
    minuteur = setTimeout(() => fn(...args), delai);
  };
}

// --- Démarrage ---
chargerListe();
chargerStatsRapides();
chargerClasses();

// --- Gestion des onglets Registre / Archives ---

document.querySelectorAll(".onglet[data-vue]").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".onglet[data-vue]").forEach((b) => b.classList.remove("actif"));
    btn.classList.add("actif");
    etat.vue = btn.dataset.vue;
    etat.page = 1;
    if (etat.vue === "archives") {
      chargerArchives();
    } else {
      chargerListe();
    }
  });
});

async function chargerArchives() {
  els.corps.innerHTML = `<tr class="ligne-chargement"><td colspan="8">Chargement des archives…</td></tr>`;
  document.getElementById("pagination").style.display = "none";

  try {
    const data = await api.getArchives();
    if (data.resultats.length === 0) {
      els.corps.innerHTML = `<tr class="ligne-vide"><td colspan="8">Aucun élève archivé.</td></tr>`;
    } else {
      els.corps.innerHTML = data.resultats.map(ligneArchiveHTML).join("");
    }
    attacherEvenementsRestauration();
  } catch (err) {
    els.corps.innerHTML = `<tr class="ligne-vide"><td colspan="8">Erreur : ${err.message}</td></tr>`;
  }
}

function ligneArchiveHTML(e) {
  const moyenne = e.moyenne_generale ?? "—";
  return `
    <tr data-id="${e.id}">
      <td class="col-check"></td>
      <td class="numero">${e.numero}</td>
      <td>${e.nom}</td>
      <td>${e.prenom}</td>
      <td>${e.classe}</td>
      <td class="moyenne"><span class="pastille-moyenne">${moyenne}</span></td>
      <td><span class="tampon tampon-db">DB</span></td>
      <td class="col-actions">
        <button class="bouton bouton-fantome btn-restaurer" data-id="${e.id}">Restaurer</button>
      </td>
    </tr>
  `;
}

function attacherEvenementsRestauration() {
  document.querySelectorAll(".btn-restaurer").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const id = e.target.dataset.id;
      try {
        await api.restaurerEtudiant(id);
        chargerArchives();
        chargerStatsRapides();
      } catch (err) {
        alert("Erreur : " + err.message);
      }
    });
  });
}