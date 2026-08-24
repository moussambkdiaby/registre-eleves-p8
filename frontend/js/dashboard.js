const PALETTE = {
  tableau: "#16233F",
  bleu: "#2F80ED",
  db: "#1F8A70",
  json: "#5B5FC7",
  erreur: "#C15A44",
  ligne: "#D3DCEA",
  encreDouce: "#5B6B7D",
};

async function chargerResume() {
  try {
    const kpis = await api.getStats("kpis");
    const partDb = kpis.total_donnees > 0
      ? Math.round((kpis.nombre_db / kpis.total_donnees) * 100)
      : 0;
    document.getElementById("resumeBandeau").innerHTML = `
      Le registre suit actuellement <strong>${kpis.total_donnees} élèves</strong>.
      <strong>${kpis.nombre_db}</strong> sont déjà en base de données (${partDb}%),
      et <strong>${kpis.nombre_json}</strong> restent à importer depuis le fichier source.
      ${kpis.nombre_archivees > 0 ? `<strong>${kpis.nombre_archivees}</strong> élève(s) sont actuellement archivé(s).` : ""}
    `;
  } catch (err) {
    document.getElementById("resumeBandeau").textContent = "Impossible de charger le résumé.";
    console.error(err);
  }
}

async function chargerKpis() {
  try {
    const kpis = await api.getStats("kpis");
    document.getElementById("kpiTotal").textContent = kpis.total_donnees;
    document.getElementById("kpiDb").textContent = kpis.nombre_db;
    document.getElementById("kpiJson").textContent = kpis.nombre_json;
    document.getElementById("kpiValides").textContent = kpis.nombre_valides;
    document.getElementById("kpiInvalides").textContent = kpis.nombre_invalides;
    document.getElementById("kpiArchivees").textContent = kpis.nombre_archivees;
  } catch (err) {
    console.error("Erreur KPIs :", err);
  }
}

async function chargerGraphClasse() {
  try {
    const data = await api.getStats("repartition-classe");
    const ctx = document.getElementById("graphClasse");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.resultats.map((r) => r.classe),
        datasets: [{
          label: "Élèves",
          data: data.resultats.map((r) => r.nombre),
          backgroundColor: PALETTE.bleu,
          borderRadius: 4,
          maxBarThickness: 42,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.parsed.y} élève(s)`,
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: PALETTE.ligne },
            title: { display: true, text: "Nombre d'élèves" },
          },
          x: {
            grid: { display: false },
            title: { display: true, text: "Classe" },
          },
        },
      },
    });
  } catch (err) {
    console.error("Erreur répartition classe :", err);
  }
}

async function chargerGraphSource() {
  try {
    const data = await api.getStats("repartition-source");
    const total = data.resultats.reduce((s, r) => s + r.nombre, 0);
    const ctx = document.getElementById("graphSource");
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: data.resultats.map((r) => r.source === "DB" ? "En base (modifiable)" : "JSON (lecture seule)"),
        datasets: [{
          data: data.resultats.map((r) => r.nombre),
          backgroundColor: [PALETTE.db, PALETTE.json],
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 14, padding: 14 } },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const pct = total > 0 ? Math.round((ctx.parsed / total) * 100) : 0;
                return `${ctx.label} : ${ctx.parsed} (${pct}%)`;
              },
            },
          },
        },
      },
    });
  } catch (err) {
    console.error("Erreur répartition source :", err);
  }
}

async function chargerGraphMoyenne() {
  try {
    const data = await api.getStats("moyenne-classe-globale");
    const ctx = document.getElementById("graphMoyenne");

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.resultats.map((r) => r.classe),
        datasets: [{
          label: "Moyenne générale",
          data: data.resultats.map((r) => r.moyenne_classe),
          backgroundColor: PALETTE.tableau,
          borderRadius: 4,
          maxBarThickness: 42,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `Moyenne : ${ctx.parsed.y} / 20`,
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 20,
            grid: { color: PALETTE.ligne },
            title: { display: true, text: "Moyenne générale / 20" },
          },
          x: {
            grid: { display: false },
            title: { display: true, text: "Classe" },
          },
        },
      },
    });

    document.getElementById("noteMoyenne").textContent =
      "Ce graphique combine les élèves en base et ceux du fichier JSON, pour donner une vue complète par classe.";
  } catch (err) {
    console.error("Erreur moyenne par classe :", err);
  }
}
async function chargerTop10() {
  try {
    const data = await api.getStats("top10");
    const liste = document.getElementById("listeTop10");
    if (data.resultats.length === 0) {
      liste.innerHTML = `<li style="list-style:none; font-style:italic; color:var(--encre-douce);">Aucune donnée pour le moment.</li>`;
      return;
    }
    liste.innerHTML = data.resultats.map((e) => `
      <li>
        <span class="top10-nom">${e.prenom} ${e.nom}</span>
        <span class="top10-classe">${e.classe}</span>
        <span class="top10-moyenne">${e.moyenne_generale} / 20</span>
      </li>
    `).join("");
  } catch (err) {
    console.error("Erreur top 10 :", err);
  }
}

async function chargerArchivesDashboard() {
  const corps = document.getElementById("corpsArchivesDashboard");
  try {
    const data = await api.getArchives();
    if (data.resultats.length === 0) {
      corps.innerHTML = `<tr class="ligne-vide"><td colspan="5">Aucun élève archivé actuellement.</td></tr>`;
      return;
    }
    corps.innerHTML = data.resultats.map((e) => `
      <tr>
        <td class="numero">${e.numero}</td>
        <td>${e.nom}</td>
        <td>${e.prenom}</td>
        <td>${e.classe}</td>
        <td class="moyenne">${e.moyenne_generale ?? "—"}</td>
      </tr>
    `).join("");
  } catch (err) {
    corps.innerHTML = `<tr class="ligne-vide"><td colspan="5">Erreur de chargement.</td></tr>`;
    console.error(err);
  }
}

chargerResume();
chargerKpis();
chargerGraphClasse();
chargerGraphSource();
chargerGraphMoyenne();
chargerTop10();
chargerArchivesDashboard();