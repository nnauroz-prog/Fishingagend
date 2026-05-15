"""Sim-Vorlagen — fertige Szenarien zum Klick-Start.

Jede Vorlage definiert: Name, Beschreibung, ein Set an Personas
(werden bei Bedarf als Agenten angelegt) und eine Sim-Konfig
(Schritte, Variable, Modus).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.modelle.persona import Persona


@dataclass
class Vorlage:
    schluessel: str
    titel: str
    beschreibung: str
    kategorie: str
    personas: list[Persona]
    schritte: int = 8
    variable: dict = None  # type: ignore[assignment]
    dual_modus: bool = True
    plattform_modus: bool = False

    def __post_init__(self) -> None:
        if self.variable is None:
            self.variable = {}


VORLAGEN: list[Vorlage] = [
    Vorlage(
        schluessel="klima_kommune",
        titel="Klimakrise in der Kommune",
        beschreibung=(
            "Eine Mittelstadt diskutiert ein verbindliches CO2-Reduktionsziel. "
            "Wissenschaft, Politik und Aktivismus stoßen aufeinander."
        ),
        kategorie="Politik",
        schritte=10,
        variable={"zielwert_co2_minus_prozent": 50, "frist_jahr": 2030},
        dual_modus=True,
        personas=[
            Persona(
                name="Dr. Lisa Weber",
                alter=44,
                beruf="Klimawissenschaftlerin",
                hintergrund="Promotion in Hamburg, jetzt am IPCC tätig.",
                werte=["Wahrheit", "Wirkung", "Geduld"],
                charakterzuege=["analytisch", "ruhig"],
                sprachstil="fachlich",
            ),
            Persona(
                name="Markus König",
                alter=52,
                beruf="Bürgermeister",
                hintergrund="Drei Amtsperioden, will pragmatische Lösungen.",
                werte=["Pragmatismus", "Loyalität"],
                charakterzuege=["entscheidungsfreudig", "vorsichtig"],
                sprachstil="verbindlich",
            ),
            Persona(
                name="Yuki Tanaka",
                alter=27,
                beruf="Klima-Aktivistin",
                hintergrund="Sprecherin eines lokalen Bündnisses.",
                werte=["Gerechtigkeit", "Mut"],
                charakterzuege=["leidenschaftlich", "spontan"],
                sprachstil="salopp",
            ),
            Persona(
                name="Heiko Steiner",
                alter=58,
                beruf="Industrievertreter",
                hintergrund="Vorstand des regionalen Verbands.",
                werte=["Stabilität", "Arbeitsplätze"],
                charakterzuege=["skeptisch", "geschäftstüchtig"],
                sprachstil="förmlich",
            ),
        ],
    ),
    Vorlage(
        schluessel="krankenhaus_krise",
        titel="Krankenhaus-Personalkrise",
        beschreibung=(
            "Pflegekräftemangel führt zu Notdienst-Reduktion. "
            "Direktion, Pflegerat und Politik suchen Lösungen."
        ),
        kategorie="Gesundheit",
        schritte=8,
        variable={"freie_stellen_anteil": 0.22},
        dual_modus=True,
        personas=[
            Persona(
                name="Dr. Halil Demir",
                alter=46,
                beruf="Krankenhausdirektor",
                hintergrund="Internist, jetzt Verwaltungsverantwortung für 600 Betten.",
                werte=["Patientenwohl", "Effizienz"],
                charakterzuege=["nüchtern", "diplomatisch"],
                sprachstil="formell",
            ),
            Persona(
                name="Petra Hoffmann",
                alter=39,
                beruf="Pflegerats-Vorsitzende",
                hintergrund="Examinierte Krankenschwester seit 18 Jahren.",
                werte=["Solidarität", "Anerkennung"],
                charakterzuege=["bestimmt", "empathisch"],
                sprachstil="direkt",
            ),
            Persona(
                name="Janine Pfeiffer",
                alter=51,
                beruf="Gesundheitspolitikerin",
                hintergrund="Bundestagsmitglied im Gesundheitsausschuss.",
                werte=["Pragmatismus", "Kompromiss"],
                charakterzuege=["abwägend", "kommunikativ"],
                sprachstil="verbindlich",
            ),
        ],
    ),
    Vorlage(
        schluessel="plattform_streit",
        titel="Social-Media-Plattform-Streit",
        beschreibung=(
            "Eine Eilmeldung verbreitet sich auf einer Plattform. "
            "Nutzer kommentieren, liken, folgen — Stimmung kippt."
        ),
        kategorie="Medien",
        schritte=6,
        variable={"eilmeldung": "Politiker zurückgetreten wegen Skandal"},
        dual_modus=False,
        plattform_modus=True,
        personas=[
            Persona(
                name="Anna Bürger",
                alter=34,
                beruf="Lehrerin",
                hintergrund="Politisch interessiert, vorsichtig im Netz.",
                werte=["Faktenlage", "Höflichkeit"],
                charakterzuege=["überlegt"],
                sprachstil="sachlich",
            ),
            Persona(
                name="Felix Wittmann",
                alter=23,
                beruf="Student",
                hintergrund="Aktiv auf mehreren Plattformen.",
                werte=["Schnelligkeit"],
                charakterzuege=["impulsiv"],
                sprachstil="salopp",
            ),
            Persona(
                name="Frau Hessler",
                alter=66,
                beruf="Rentnerin",
                hintergrund="Skeptisch gegenüber Eilmeldungen.",
                werte=["Sicherheit"],
                charakterzuege=["misstrauisch"],
                sprachstil="förmlich",
            ),
            Persona(
                name="Sven Kahl",
                alter=41,
                beruf="Journalist",
                hintergrund="Fact-Checker bei einer Tageszeitung.",
                werte=["Genauigkeit"],
                charakterzuege=["analytisch"],
                sprachstil="fachlich",
            ),
        ],
    ),
    Vorlage(
        schluessel="produkt_launch",
        titel="Produkt-Launch im Mittelstand",
        beschreibung=(
            "Ein Mittelständler bringt ein neues Produkt heraus. "
            "Geschäftsführung, Vertrieb, Entwicklung und Marketing stimmen sich ab."
        ),
        kategorie="Wirtschaft",
        schritte=8,
        variable={"launch_termin_wochen": 12},
        dual_modus=True,
        personas=[
            Persona(
                name="Sophie Laurent",
                alter=39,
                beruf="Marketingleiterin",
                hintergrund="Berät seit 10 Jahren Mittelstand.",
                werte=["Klarheit", "Kundenorientierung"],
                charakterzuege=["strukturiert"],
                sprachstil="fachlich",
            ),
            Persona(
                name="Klaus Reuter",
                alter=58,
                beruf="Geschäftsführer",
                hintergrund="Eigentümer des Unternehmens.",
                werte=["Stabilität"],
                charakterzuege=["bedacht"],
                sprachstil="verbindlich",
            ),
            Persona(
                name="Mira Nguyen",
                alter=32,
                beruf="Entwicklungsleiterin",
                hintergrund="Verantwortet die Technik des Produkts.",
                werte=["Qualität"],
                charakterzuege=["perfektionistisch"],
                sprachstil="knapp",
            ),
        ],
    ),
    Vorlage(
        schluessel="schule_streit",
        titel="Schulkonferenz: Handyverbot",
        beschreibung=(
            "Eltern, Lehrer und Schülerinnen diskutieren ein striktes "
            "Handyverbot auf dem Schulhof."
        ),
        kategorie="Bildung",
        schritte=6,
        variable={"verbots_strenge": "vollstaendig"},
        dual_modus=True,
        personas=[
            Persona(
                name="Frau Bauer",
                alter=47,
                beruf="Schulleiterin",
                hintergrund="Gymnasium mit 800 Schülerinnen.",
                werte=["Lernumgebung"],
                charakterzuege=["organisiert"],
                sprachstil="förmlich",
            ),
            Persona(
                name="Herr Albrecht",
                alter=42,
                beruf="Elternsprecher",
                hintergrund="Zwei Kinder am Gymnasium.",
                werte=["Kommunikation"],
                charakterzuege=["abwägend"],
                sprachstil="sachlich",
            ),
            Persona(
                name="Lena (Schülersprecherin)",
                alter=16,
                beruf="Schülerin",
                hintergrund="Klasse 10, im Schülerrat aktiv.",
                werte=["Selbstbestimmung"],
                charakterzuege=["selbstbewusst"],
                sprachstil="locker",
            ),
        ],
    ),
]


def liste_vorlagen() -> list[dict]:
    return [
        {
            "schluessel": v.schluessel,
            "titel": v.titel,
            "beschreibung": v.beschreibung,
            "kategorie": v.kategorie,
            "schritte": v.schritte,
            "dual_modus": v.dual_modus,
            "plattform_modus": v.plattform_modus,
            "anzahl_personas": len(v.personas),
        }
        for v in VORLAGEN
    ]


def hole_vorlage(schluessel: str) -> Vorlage | None:
    return next((v for v in VORLAGEN if v.schluessel == schluessel), None)
