# Implementazione Zero-Shot Classifier

Questa documentazione riassume il funzionamento del frontend per il sistema di classificazione Zero-Shot dei ticket.

## Struttura e Tecnologie
- **Framework:** Vue 3 (Composition API) + Vite.
- **Componente Principale:** Tutto il codice è racchiuso in `src/App.vue`.
- **Stile:** CSS Vanilla. Utilizzo esteso di CSS Variables (`var(--primary)`), Glassmorphism (sfocatura dello sfondo), Flexbox e CSS Grid per il layout responsivo.

## Logica di Classificazione (`classifyMessage`)

Il sistema è progettato per interfacciarsi con un'IA reale, ma possiede una modalità dimostrativa integrata.

1. **Chiamata API (Ideale):**
   - Invia il testo inserito dall'utente tramite una richiesta `POST` all'endpoint `/api/classify`.
   - Si aspetta un JSON di risposta contenente il dominio identificato (es. `{ "category": "bug" }`).

2. **Modalità Fallback Demo (Attuale):**
   - Poiché il backend non è ancora collegato, la chiamata `fetch` fallisce ed entra nel blocco `catch`.
   - **Simulazione:** Viene inserito un ritardo artificiale di 1,8 secondi per simulare i tempi di pensiero di un LLM (Large Language Model).
   - **Regole Euristiche:** Il testo viene analizzato tramite *espressioni regolari*. Se contiene specifiche parole chiave (es. "errore", "crash", "design", "deploy"), viene assegnato localmente alla categoria corretta.
   - **Risultato:** L'interfaccia si aggiorna in modo reattivo, evidenziando il dominio identificato e mostrando una barra di confidenza.

## Categorie Supportate
Il sistema monitora 8 domini principali, ognuno con un'icona e un colore distintivo:
- Task (Generico)
- Bug (Difetti)
- Enhancement (Nuove funzionalità)
- Research (Ricerca/Fattibilità)
- Design (Interfaccia/UX)
- Testing (Validazione)
- Deployment (Rilasci o Infrastruttura)
- Documentation (Guide e manuali)
