export interface Persona {
  name: string;
  alter?: number | null;
  beruf?: string | null;
  hintergrund: string;
  werte: string[];
  charakterzuege: string[];
  beziehungen: Record<string, string>;
  sprachstil: string;
}

export interface Agent {
  id: string;
  persona: Persona;
  notizen?: string | null;
  erstellt_am: string;
  aktualisiert_am: string;
  gedaechtnis_id?: string | null;
}

export interface AgentErstellen {
  persona: Persona;
  notizen?: string | null;
}

export type SimulationStatus = 'geplant' | 'laeuft' | 'abgeschlossen' | 'fehlgeschlagen';

export interface SimulationSchritt {
  nummer: number;
  welt: 'kontrolle' | 'variante';
  ereignisse: string[];
  agent_zustaende: Record<string, string>;
}

export interface Simulation {
  id: string;
  name: string;
  beschreibung: string;
  agent_ids: string[];
  schritte: number;
  variable: Record<string, unknown>;
  dual_modus: boolean;
  status: SimulationStatus;
  erstellt_am: string;
  verlauf: SimulationSchritt[];
}

export interface SimulationErstellen {
  name: string;
  beschreibung?: string;
  agent_ids: string[];
  schritte: number;
  variable: Record<string, unknown>;
  dual_modus: boolean;
}

export interface Nachricht {
  rolle: 'nutzer' | 'agent' | 'system';
  inhalt: string;
  zeitstempel: string;
}

export interface ChatAntwort {
  agent_id: string;
  antwort: string;
  nachricht: Nachricht;
  eingangs_token: number;
  ausgangs_token: number;
}
