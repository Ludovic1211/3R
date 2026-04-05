import re
from pathlib import Path

SRC = Path("3R_Matheo_extracted.txt")
OUT = Path("section_empirique_matheo_full.tex")

raw = SRC.read_text(encoding="utf-8")

# Normalize OCR ligatures but keep wording
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

lines = raw.splitlines()
clean_lines = []
for ln in lines:
    s = ln.strip()
    if re.match(r"^=+\s*PAGE\s+\d+\s*=+$", s):
        clean_lines.append("")
        continue
    if re.match(r"^\+\d+$", s):
        continue
    clean_lines.append(ln)

text = "\n".join(clean_lines)
text = re.sub(r"\n{3,}", "\n\n", text)

order = [
    "8.1", "8.2", "8.3", "8.4", "8.4.1", "8.4.2", "8.4.3", "8.4.4",
    "8.5", "8.5.1", "8.5.2", "8.6", "8.6.1", "8.6.2", "8.6.3", "8.6.4",
    "8.7", "8.8", "8.8.1", "8.8.2", "8.8.3", "8.9", "8.10", "8.11",
]

line_anchors = []
for i, ln in enumerate(clean_lines):
    s = ln.strip()
    m = re.match(r"^(8\.\d+(?:\.\d+)?)\.\s*", s)
    if m and m.group(1) in order:
        if not any(a[1] == m.group(1) for a in line_anchors):
            line_anchors.append((i, m.group(1)))

line_anchors.sort(key=lambda x: x[0])
if len(line_anchors) != len(order):
    found = [k for _, k in line_anchors]
    missing = [k for k in order if k not in found]
    raise RuntimeError(f"missing numeric headings: {missing}")

concl = re.search(r"Conclusion\s+Générale\s*:\s*Dépasser la \"Vision Tunnel\" pour une\s*Régulation Holistique", text)
if not concl:
    raise RuntimeError("conclusion heading not found")

persp = re.search(r"\nPerspectives\b", text)
if not persp:
    raise RuntimeError("perspectives heading not found")

intro = "\n".join(clean_lines[:line_anchors[0][0]]).strip()

segments = {}
for i, (line_no, key) in enumerate(line_anchors):
    next_line = line_anchors[i + 1][0] if i + 1 < len(line_anchors) else None
    block_lines = clean_lines[line_no + 1: next_line]

    # Remove OCR heading-tail line fragments when heading wrapped on next line
    while block_lines and block_lines[0].strip():
        first = block_lines[0].strip()
        wc = len(first.split())
        if wc <= 8 and not re.search(r"[\.:;!?]$", first):
            block_lines = block_lines[1:]
            continue
        break

    segments[key] = "\n".join(block_lines).strip()

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
    t = t.replace("\\", r"\textbackslash{}")
    t = t.replace("&", r"\&").replace("%", r"\%").replace("$", r"\$").replace("#", r"\#").replace("_", r"\_")
    t = t.replace("{", r"\{").replace("}", r"\}")
    return t


def format_block(block: str):
    paras = [p.strip() for p in re.split(r"\n\s*\n", block) if p.strip()]
    out = []
    for p in paras:
        lines = [ln.strip() for ln in p.splitlines() if ln.strip()]

        # bullet groups from extraction
        if any(ln.startswith("•") for ln in lines):
            bullets = []
            cur = ""
            for ln in lines:
                if ln.startswith("•"):
                    if cur:
                        bullets.append(cur.strip())
                    cur = ln.lstrip("•").strip()
                else:
                    cur += " " + ln
            if cur:
                bullets.append(cur.strip())

            out.append(r"\begin{itemize}")
            for b in bullets:
                b = re.sub(r"\s+", " ", b).strip().replace(" +2 ", " ")
                out.append("    " + r"\item " + esc(b))
            out.append(r"\end{itemize}")
            out.append("")
            continue

        txt = re.sub(r"\s+", " ", " ".join(lines)).strip()
        txt = txt.replace(" +1 ", " ").replace(" +2 ", " ").replace("1.Le", "1. Le")
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
