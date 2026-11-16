"""Génère les images du README en thèmes sombre et clair : bannière et cartes de statistiques.

Usage : python scripts/generer_images.py
La police Sorcelle et l'avatar sont récupérés sur danaedev.fr puis intégrés en base64.
Les statistiques viennent de l'API GraphQL de GitHub : jeton lu dans GITHUB_TOKEN, sinon via `gh auth token`.
"""

import base64
import json
import os
import random
import subprocess
import urllib.request
from datetime import date
from pathlib import Path

SITE = "https://danaedev.fr"
UTILISATRICE = "dalbrechtmartin"
# Langages générés (documentation, build) qui fausseraient la répartition
LANGAGES_EXCLUS = {"HTML", "Makefile"}
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
SORTIE = Path(__file__).resolve().parent.parent / "assets"

# Couleurs du design system Grimoire (danaedev.fr)
THEMES = {
    "sombre": {
        "fond": "#17141c",
        "encre": "#ece4d8",
        "or": "#e3b04b",
        "violet": "#4b3570",
        "surface": "#221d29",
        "attenue": "#b3a9b8",
    },
    "clair": {
        "fond": "#f1e9d8",
        "encre": "#1d1822",
        "or": "#8a5a00",
        "violet": "#4b3570",
        "surface": "#fbf6ea",
        "attenue": "#5a4f5f",
    },
}

LARGEUR, HAUTEUR = 1200, 420
CENTRE_X, CENTRE_Y = 980, 210


def telecharger_base64(chemin: str) -> str:
    with urllib.request.urlopen(f"{SITE}{chemin}") as reponse:
        return base64.b64encode(reponse.read()).decode("ascii")


def etoile(x: float, y: float, r: float) -> str:
    """Étoile à quatre branches, le motif ✦ du portfolio."""
    p = r * 0.3
    return (
        f"M{x},{y - r} L{x + p},{y - p} L{x + r},{y} L{x + p},{y + p} "
        f"L{x},{y + r} L{x - p},{y + p} L{x - r},{y} L{x - p},{y - p} Z"
    )


def ciel_etoile(couleur: str) -> str:
    alea = random.Random(7)
    points = []
    while len(points) < 26:
        x, y = alea.uniform(50, 1150), alea.uniform(45, 375)
        if 40 < x < 760 and 90 < y < 350:
            continue  # garder le texte lisible
        if (x - CENTRE_X) ** 2 + (y - CENTRE_Y) ** 2 < 185**2:
            continue
        points.append((x, y, alea.uniform(2, 4.5), alea.uniform(0.25, 0.6)))
    return "".join(
        f'<path d="{etoile(round(x, 1), round(y, 1), round(r, 1))}" fill="{couleur}" opacity="{o:.2f}"/>'
        for x, y, r, o in points
    )


def cadre(couleur: str) -> str:
    """Double filet et coins de couverture de grimoire."""
    coins = []
    for cx, cy, sx, sy in [(30, 30, 1, 1), (1170, 30, -1, 1), (30, 390, 1, -1), (1170, 390, -1, -1)]:
        coins.append(
            f'<path d="M{cx},{cy + 34 * sy} V{cy} H{cx + 34 * sx} M{cx + 8 * sx},{cy + 22 * sy} '
            f'V{cy + 8 * sy} H{cx + 22 * sx}" fill="none" stroke="{couleur}" stroke-width="1.5"/>'
        )
    return (
        f'<rect x="14" y="14" width="1172" height="392" fill="none" stroke="{couleur}" stroke-width="2"/>'
        f'<rect x="22" y="22" width="1156" height="376" fill="none" stroke="{couleur}" stroke-width="1" opacity=".5"/>'
        + "".join(coins)
    )


def medaillon(t: dict, avatar: str) -> str:
    """Roue dorée et portrait en arche, comme l'accueil du portfolio."""
    graduations = []
    for i in range(24):
        angle = i * 15
        longueur = 14 if i % 2 == 0 else 7
        graduations.append(
            f'<line x1="0" y1="-178" x2="0" y2="{-178 + longueur}" stroke="{t["or"]}" '
            f'stroke-width="2" transform="rotate({angle})"/>'
        )
    losanges = "".join(
        f'<path d="M0,-188 L5,-182 L0,-176 L-5,-182 Z" fill="{t["or"]}" transform="rotate({a})"/>'
        for a in (45, 135, 225, 315)
    )
    arche = "M-100,130 V-30 A100,100 0 0 1 100,-30 V130 Z"
    return f"""
<g transform="translate({CENTRE_X},{CENTRE_Y})">
  <circle r="178" fill="none" stroke="{t["or"]}" stroke-width="3"/>
  <circle r="164" fill="none" stroke="{t["or"]}" stroke-width="1" opacity=".55"/>
  {"".join(graduations)}{losanges}
  <clipPath id="arche"><path d="{arche}"/></clipPath>
  <path d="{arche}" fill="{t["violet"]}"/>
  <g clip-path="url(#arche)">
    <circle cx="14" cy="-95" r="17" fill="#e3b04b"/>
    <circle cx="23" cy="-101" r="15" fill="{t["violet"]}"/>
    <path d="{etoile(-42, -88, 9)}" fill="#e3b04b"/>
    <path d="{etoile(56, -70, 6)}" fill="#e3b04b"/>
    <path d="{etoile(-62, -48, 4)}" fill="#e3b04b" opacity=".7"/>
    <svg x="-96" y="-62" width="192" height="192" viewBox="0 0 48 48">
      <image href="data:image/png;base64,{avatar}" width="192" height="48" style="image-rendering:pixelated"/>
    </svg>
  </g>
  <path d="{arche}" fill="none" stroke="{t["or"]}" stroke-width="4"/>
</g>"""


def banniere(t: dict, police: str, avatar: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGEUR} {HAUTEUR}" width="{LARGEUR}" height="{HAUTEUR}" role="img" aria-labelledby="titre">
<title id="titre">Danaé Albrecht--Martin, apprentie ingénieure en systèmes d’information</title>
<style>
  @font-face {{ font-family: "Sorcelle"; font-weight: 700; src: url(data:font/woff2;base64,{police}) format("woff2"); }}
  .nom {{ font-family: Sorcelle, Georgia, serif; font-weight: 700; font-size: 66px; fill: {t["encre"]}; }}
  .surtitre {{ font-family: Georgia, serif; font-size: 17px; letter-spacing: 3.5px; fill: {t["or"]}; }}
</style>
<rect width="{LARGEUR}" height="{HAUTEUR}" fill="{t["fond"]}"/>
{ciel_etoile(t["or"])}
{cadre(t["or"])}
<text class="surtitre" x="80" y="150">APPRENTIE INGÉNIEURE EN SYSTÈMES D’INFORMATION</text>
<text class="nom" x="76" y="232">Danaé</text>
<text class="nom" x="76" y="308">Albrecht--Martin</text>
{medaillon(t, avatar)}
</svg>
"""


REQUETE_STATS = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar { totalContributions }
    }
  }
}"""


def jeton_github() -> str:
    return os.environ.get("GITHUB_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True, check=True
    ).stdout.strip()


def lire_stats() -> dict:
    requete = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": REQUETE_STATS, "variables": {"login": UTILISATRICE}}).encode(),
        headers={"Authorization": f"bearer {jeton_github()}", "User-Agent": "generer-images"},
    )
    with urllib.request.urlopen(requete) as reponse:
        utilisatrice = json.load(reponse)["data"]["user"]
    depots = utilisatrice["repositories"]
    contributions = utilisatrice["contributionsCollection"]
    langages: dict[str, dict] = {}
    for depot in depots["nodes"]:
        for arete in depot["languages"]["edges"]:
            nom = arete["node"]["name"]
            if nom in LANGAGES_EXCLUS:
                continue
            entree = langages.setdefault(nom, {"couleur": arete["node"]["color"] or "#888888", "taille": 0})
            entree["taille"] += arete["size"]
    return {
        "contributions": contributions["contributionCalendar"]["totalContributions"],
        "commits": contributions["totalCommitContributions"],
        "pull_requests": contributions["totalPullRequestContributions"],
        "depots": depots["totalCount"],
        "etoiles": sum(depot["stargazerCount"] for depot in depots["nodes"]),
        "langages": sorted(langages.items(), key=lambda item: -item[1]["taille"]),
    }


def date_du_jour() -> str:
    jour = date.today()
    return f"{jour.day} {MOIS[jour.month - 1]} {jour.year}"


def nombre(valeur: float, decimales: int = 0) -> str:
    """Format français : espace fine insécable pour les milliers, virgule décimale."""
    return f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")


def carte(t: dict, police: str, titre: str, contenu: str) -> str:
    """Carte 500 × 240 au cadre de grimoire, commune aux statistiques et aux langages."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 240" width="500" height="240" role="img" aria-labelledby="titre">
<title id="titre">{titre}</title>
<style>
  @font-face {{ font-family: "Sorcelle"; font-weight: 700; src: url(data:font/woff2;base64,{police}) format("woff2"); }}
  .titre {{ font-family: Sorcelle, Georgia, serif; font-weight: 700; font-size: 24px; fill: {t["encre"]}; }}
  .libelle {{ font-family: Georgia, serif; font-size: 16px; fill: {t["attenue"]}; }}
  .valeur {{ font-family: Georgia, serif; font-size: 17px; font-weight: 700; fill: {t["encre"]}; }}
  .note {{ font-family: Georgia, serif; font-size: 12px; font-style: italic; fill: {t["attenue"]}; }}
</style>
<rect x="1" y="1" width="498" height="238" rx="6" fill="{t["surface"]}" stroke="{t["or"]}" stroke-width="2"/>
<rect x="8" y="8" width="484" height="224" rx="3" fill="none" stroke="{t["or"]}" stroke-width="1" opacity=".45"/>
<path d="{etoile(36, 40, 9)}" fill="{t["or"]}"/>
<text class="titre" x="54" y="49">{titre}</text>
{contenu}
<text class="note" x="464" y="218" text-anchor="end">Mis à jour le {date_du_jour()}</text>
</svg>
"""


def carte_stats(t: dict, police: str, stats: dict) -> str:
    lignes = [
        ("Contributions sur 12 mois", stats["contributions"]),
        ("Commits sur 12 mois", stats["commits"]),
        ("Pull requests sur 12 mois", stats["pull_requests"]),
        ("Dépôts publics", stats["depots"]),
        ("Étoiles reçues", stats["etoiles"]),
    ]
    contenu = "".join(
        f'<path d="{etoile(40, 81 + i * 26, 4)}" fill="{t["or"]}" opacity=".8"/>'
        f'<text class="libelle" x="54" y="{86 + i * 26}">{libelle}</text>'
        f'<text class="valeur" x="464" y="{86 + i * 26}" text-anchor="end">{nombre(valeur)}</text>'
        for i, (libelle, valeur) in enumerate(lignes)
    )
    return carte(t, police, "Mes statistiques GitHub", contenu)


def carte_langages(t: dict, police: str, stats: dict) -> str:
    principaux = stats["langages"][:6]
    total = sum(info["taille"] for _, info in stats["langages"])
    barre, x = [], 36.0
    for _, info in principaux:
        largeur = 428 * info["taille"] / total
        barre.append(f'<rect x="{x:.1f}" y="72" width="{largeur:.1f}" height="12" fill="{info["couleur"]}"/>')
        x += largeur
    legende = []
    for i, (nom, info) in enumerate(principaux):
        colonne, rang = divmod(i, 3)
        lx, ly = 36 + colonne * 226, 122 + rang * 30
        legende.append(
            f'<circle cx="{lx + 6}" cy="{ly - 5}" r="6" fill="{info["couleur"]}"/>'
            f'<text class="libelle" x="{lx + 20}" y="{ly}">{nom}</text>'
            f'<text class="valeur" x="{lx + 202}" y="{ly}" text-anchor="end">'
            f'{nombre(100 * info["taille"] / total, 1)} %</text>'
        )
    contenu = (
        '<clipPath id="arrondi"><rect x="36" y="72" width="428" height="12" rx="6"/></clipPath>'
        f'<rect x="36" y="72" width="428" height="12" rx="6" fill="{t["attenue"]}" opacity=".3"/>'
        f'<g clip-path="url(#arrondi)">{"".join(barre)}</g>' + "".join(legende)
    )
    return carte(t, police, "Langages les plus utilisés", contenu)


def main() -> None:
    police = telecharger_base64("/fonts/Sorcelle-Bold.woff2")
    avatar = telecharger_base64("/sprites/avatar-crypte.png")
    stats = lire_stats()
    SORTIE.mkdir(exist_ok=True)
    for nom, theme in THEMES.items():
        (SORTIE / f"banniere-{nom}.svg").write_text(banniere(theme, police, avatar), encoding="utf-8")
        (SORTIE / f"stats-{nom}.svg").write_text(carte_stats(theme, police, stats), encoding="utf-8")
        (SORTIE / f"langages-{nom}.svg").write_text(carte_langages(theme, police, stats), encoding="utf-8")
    print(f"Images écrites dans {SORTIE}")


if __name__ == "__main__":
    main()
