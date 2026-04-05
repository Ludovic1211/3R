import re
from pathlib import Path
from pypdf import PdfReader

PDF = Path("3R_Matheo.pdf")
OUT = Path("section_empirique_matheo_full.tex")

reader = PdfReader(str(PDF))

pages = []
for page in reader.pages:
    try:
        txt = page.extract_text(extraction_mode="layout") or ""
    except TypeError:
        txt = page.extract_text() or ""
    pages.append(txt)

raw = "\n\n".join(pages)

# Normalize PDF ligatures/punctuation while keeping wording.
for a, b in {
    "ﬁ": "fi",
    "ﬀ": "ff",
    "ﬂ": "fl",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "’": "'",
    "‘": "'",
    "“": '"',
    "”": '"',
    "−": "-",
    "–": "-",
    "—": "-",
    "∘": " deg",
}.items():
    raw = raw.replace(a, b)

lines = [ln.rstrip() for ln in raw.splitlines()]
clean = []
for ln in lines:
    s = ln.strip()
    if not s:
        clean.append("")
        continue

    # Drop lone page numbers and common footer noise.
    if re.fullmatch(r"\d+", s):
        continue
    if s.lower().startswith("ignoring wrong pointing object"):
        continue

    clean.append(ln)

text = "\n".join(clean)
text = re.sub(r"\n{3,}", "\n\n", text).strip()

order = [
    "8.1", "8.2", "8.3", "8.4", "8.4.1", "8.4.2", "8.4.3", "8.4.4",
    "8.5", "8.5.1", "8.5.2", "8.6", "8.6.1", "8.6.2", "8.6.3", "8.6.4",
    "8.7", "8.8", "8.8.1", "8.8.2", "8.8.3", "8.9", "8.10", "8.11",
]

anchors = []
for i, ln in enumerate(text.splitlines()):
    s = ln.strip()
    m = re.match(r"^(8\.\d+(?:\.\d+)?)\.\s*", s)
    if m and m.group(1) in order and not any(k == m.group(1) for _, k in anchors):
        anchors.append((i, m.group(1)))

anchors.sort(key=lambda x: x[0])
found = [k for _, k in anchors]
missing = [k for k in order if k not in found]
if missing:
    raise RuntimeError(f"Missing numeric headings: {missing}")

all_lines = text.splitlines()
intro = "\n".join(all_lines[:anchors[0][0]]).strip()

segments = {}
for idx, (line_no, key) in enumerate(anchors):
    next_line = anchors[idx + 1][0] if idx + 1 < len(anchors) else len(all_lines)
    body = all_lines[line_no + 1:next_line]

    # Remove wrapped heading leftovers right after heading lines.
    while body and body[0].strip() and len(body[0].strip().split()) <= 8 and not re.search(r"[\.:;!?]$", body[0].strip()):
        body = body[1:]

    segments[key] = "\n".join(body).strip()

concl = re.search(r"Conclusion\s+Générale\s*:\s*Dépasser la\s*\"?Vision Tunnel\"?\s*pour une\s*Régulation Holistique", text)
if not concl:
    raise RuntimeError("Conclusion heading not found")

persp = re.search(r"\nPerspectives\b", text)
if not persp:
    raise RuntimeError("Perspectives heading not found")

conclusion_body = text[concl.end():persp.start()].strip()
perspectives_body = text[persp.end():].strip()

headings = {
    "8.1": "Déterminants des émissions de CO2 : Une confirmation empirique de l'impact massique",
    "8.2": "Modélisation des émissions d'Hydrocarbures (HC) : La prédominance de la chimie sur la physique",
    "8.3": "Modélisation des émissions d'Oxydes d'Azote (NOx) : L'empreinte du Diesel et le coût du post-traitement",
    "8.4": "Analyse de Frontière Stochastique (SFA) : Mesure de l'efficience technologique",
    "8.4.1": "Efficacité technique CO2 des motorisations Essence : La preuve de la maturité technologique",
    "8.4.2": "Efficacité technique CO2 des motorisations Diesel : Un diagnostic de saturation technologique identique",
    "8.4.3": "Efficacité technique CO2 des motorisations Hybrides Rechargeables : L'hétérogénéité des choix architecturaux",
    "8.4.4": "Efficacité technique CO2 des motorisations Hybrides Non-Rechargeables : La fracture technologique masquée par la nomenclature",
    "8.5": "Efficacité technique relative aux Hydrocarbures (HC) : L'homogénéité du post-traitement",
    "8.5.1": "Efficacité technique HC des motorisations Essence : L'universalité du traitement catalytique",
    "8.5.2": "Efficacité technique HC des motorisations Hybrides : La neutralisation des architectures par la post-combustion",
    "8.6": "Efficacité technique relative aux Oxydes d'Azote (NOx) : Le véritable juge de paix technologique",
    "8.6.1": "Efficacité technique NOx des motorisations Essence : Le grand écart technologique et financier",
    "8.6.2": "Efficacité technique NOx des motorisations Diesel : La fracture des systèmes de post-traitement",
    "8.6.3": "Efficacité technique NOx des motorisations Hybrides Rechargeables : Le biais du cycle d'homologation",
    "8.6.4": "Efficacité technique NOx des motorisations Hybrides Non-Rechargeables : La polarisation extrême des architectures",
    "8.7": "Efficacité technique combinée (HC+NOx) : La confirmation de l'hégémonie des oxydes d'azote",
    "8.8": "Analyse des Corrélations Partielles : Synergies et Compromis Technologiques (Trade-offs)",
    "8.8.1": "Méthodologie : Le recours aux résidus de régression",
    "8.8.2": "Les Synergies : L'efficacité systémique de la post-combustion et de l'hybridation",
    "8.8.3": "Le compromis fatal : Le mur technologique des Particules Fines (PM)",
    "8.9": "Palmarès d'efficience globale : L'optimisation technologique face à la réalité physique",
    "8.10": "Analyse des contre-performances : Les limites des architectures de compromis",
    "8.11": "Classement des constructeurs : L'efficience technologique au prisme des stratégies de gamme",
}

fig_map = {
    "8.1": [("0.78\\textwidth", "résultats/OLS_CO2.png", "Modèle OLS des émissions de CO2 : effets de la masse, de la puissance, de la motorisation et de la carrosserie.", "fig:ols_co2")],
    "8.2": [("0.78\\textwidth", "résultats/OLS_HC.png", "Modèle OLS des émissions d'hydrocarbures imbrûlés (HC).", "fig:ols_hc")],
    "8.3": [("0.78\\textwidth", "résultats/OLS_Nox.png", "Modèle OLS des émissions de NOx.", "fig:ols_nox")],
    "8.4.1": [("0.74\\textwidth", "résultats/SFA_CO2_Essence.png", "Distribution SFA de l'efficacité CO2 -- motorisation Essence.", "fig:sfa_co2_essence")],
    "8.4.2": [("0.74\\textwidth", "résultats/SFA_CO2_Diesel.png", "Distribution SFA de l'efficacité CO2 -- motorisation Diesel.", "fig:sfa_co2_diesel")],
    "8.4.3": [("0.74\\textwidth", "résultats/SFA_CO2_Hybrides_Rechargeables.png", "Distribution SFA de l'efficacité CO2 -- Hybrides Rechargeables.", "fig:sfa_co2_phev")],
    "8.4.4": [("0.74\\textwidth", "résultats/SFA_CO2_Hybrides_non_Rechargeables.png", "Distribution SFA de l'efficacité CO2 -- Hybrides Non-Rechargeables.", "fig:sfa_co2_hev")],
    "8.5.1": [("0.74\\textwidth", "résultats/SFA_HC_Essence.png", "Distribution SFA de l'efficacité HC -- motorisation Essence.", "fig:sfa_hc_essence")],
    "8.5.2": [
        ("0.74\\textwidth", "résultats/SFA_HC_Hybrides_Rechargeables.png", "Distribution SFA de l'efficacité HC -- Hybrides Rechargeables.", "fig:sfa_hc_phev"),
        ("0.74\\textwidth", "résultats/SFA_HC_Hybrides_non_Rechargeables.png", "Distribution SFA de l'efficacité HC -- Hybrides Non-Rechargeables.", "fig:sfa_hc_hev"),
    ],
    "8.6.1": [("0.74\\textwidth", "résultats/SFA_Nox_Essence.png", "Distribution SFA de l'efficacité NOx -- motorisation Essence.", "fig:sfa_nox_essence")],
    "8.6.2": [("0.74\\textwidth", "résultats/SFA_Nox_Diesel.png", "Distribution SFA de l'efficacité NOx -- motorisation Diesel.", "fig:sfa_nox_diesel")],
    "8.6.3": [("0.74\\textwidth", "résultats/SFA_Nox_Hybrides_Rechargeables.png", "Distribution SFA de l'efficacité NOx -- Hybrides Rechargeables.", "fig:sfa_nox_phev")],
    "8.6.4": [("0.74\\textwidth", "résultats/SFA_Nox_Hybrides_non_Rechargeables.png", "Distribution SFA de l'efficacité NOx -- Hybrides Non-Rechargeables.", "fig:sfa_nox_hev")],
    "8.7": [
        ("0.74\\textwidth", "résultats/SFA_HCNox_Diesel.png", "Distribution SFA de l'efficacité combinée (HC + NOx) -- Diesel.", "fig:sfa_hcnox_diesel"),
        ("0.74\\textwidth", "résultats/SFA_HCNox_Hybrides_non_Rechargeables.png", "Distribution SFA de l'efficacité combinée (HC + NOx) -- Hybrides Non-Rechargeables.", "fig:sfa_hcnox_hev"),
    ],
    "8.8": [("0.80\\textwidth", "résultats/Corrélations_partielles.png", "Matrice de corrélations partielles entre résidus d'émissions : synergies et compromis technologiques.", "fig:correlations_partielles")],
    "8.9": [("0.80\\textwidth", "résultats/Classement_meilleurs_véhicules.png", "Classement des véhicules les plus efficients selon l'indicateur global SFA multi-polluants.", "fig:classement_meilleurs")],
    "8.10": [("0.80\\textwidth", "résultats/Classement_pires_véhicules.png", "Classement des véhicules les moins efficients selon l'indicateur global SFA multi-polluants.", "fig:classement_pires")],
    "8.11": [("0.80\\textwidth", "résultats/Classement_Constructeurs.png", "Classement des constructeurs selon la moyenne des scores d'efficience globale.", "fig:classement_constructeurs")],
}


def esc(t: str) -> str:
    t = t.replace("&", r"\&").replace("%", r"\%").replace("$", r"\$").replace("#", r"\#").replace("_", r"\_")
    t = t.replace("{", r"\{").replace("}", r"\}")
    return t


def format_block(block: str):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", block) if p.strip()]
    out = []
    for p in paragraphs:
        lines = [ln.strip() for ln in p.splitlines() if ln.strip()]

        # Keep bullet blocks as itemize.
        if any(re.match(r"^[•\-]", ln) for ln in lines):
            items = []
            cur = ""
            for ln in lines:
                if re.match(r"^[•\-]", ln):
                    if cur:
                        items.append(cur.strip())
                    cur = re.sub(r"^[•\-]\s*", "", ln).strip()
                else:
                    cur += " " + ln
            if cur:
                items.append(cur.strip())

            out.append(r"\begin{itemize}")
            for item in items:
                item = re.sub(r"\s+", " ", item).strip()
                item = item.replace(" +1", "").replace(" +2", "")
                item = re.sub(r"\\+_", "_", item)
                item = re.sub(r"\\+%", "%", item)
                out.append("    " + r"\item " + esc(item))
            out.append(r"\end{itemize}")
            out.append("")
            continue

        txt = re.sub(r"\s+", " ", " ".join(lines)).strip()
        txt = txt.replace(" +1", "").replace(" +2", "")
        txt = re.sub(r"\\+_", "_", txt)
        txt = re.sub(r"\\+%", "%", txt)
        if txt:
            out.append(esc(txt))
            out.append("")
    return out


final = []
final.extend([
    "% ============================================================",
    r"\section{Analyse Empirique des Données ADEME : Résultats et Interprétation}",
    "% ============================================================",
    "",
])
final.extend(format_block(intro))

for key in order:
    level = "subsubsection" if key.count(".") == 2 else "subsection"
    final.append(f"\\{level}" + "{" + esc(headings[key]) + "}")
    final.append("")

    for width, path, cap, label in fig_map.get(key, []):
        final.extend([
            r"\begin{figure}[H]",
            r"    \centering",
            f"    \\includegraphics[width={width}]" + "{" + path + "}",
            "    " + r"\caption{" + esc(cap) + "}",
            "    " + r"\label{" + label + "}",
            r"\end{figure}",
            "",
        ])

    final.extend(format_block(segments[key]))

final.extend([
    "% ============================================================",
    r"\section{Conclusion Générale : Dépasser la Vision Tunnel pour une Régulation Holistique}",
    "% ============================================================",
    "",
])
final.extend(format_block(conclusion_body))
final.extend([r"\subsection{Perspectives}", ""])
final.extend(format_block(perspectives_body))

content = "\n".join(final)
content = re.sub(r"\n{3,}", "\n\n", content).strip() + "\n"
OUT.write_text(content, encoding="utf-8")
print("written", OUT)
