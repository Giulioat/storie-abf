# Impaginatore Storie ABF · passaggio di consegne

Tool web per Asia Baldoni: incolla il copy delle stories, il testo viene impaginato sulle foto dell'archivio in riquadri stile Instagram, si sposta a dito, si scarica in 1080×1920. Foto e storico sono condivisi tra chi entra col codice (archivio Supabase). In fondo alla pagina, le 5 sequenze di stories con più risposte (dati Instagram Graph API) come riferimento.

Questo repository contiene TUTTO quello che serve per farlo girare altrove. Nessuna dipendenza da chi lo ha costruito.

## Cosa c'è nel repository

| Percorso | Cosa è |
|---|---|
| `index.html` | Il sito pubblicato (GitHub Pages). È generato: non modificarlo a mano. |
| `top/top-stories.json` + `top/*.jpg` | Dati e thumbnail della sezione "Reference" (5 sequenze top). Rigenerati ogni giorno. |
| `src/impaginatore-storie-abf.html` | **Il sorgente del tool.** Un solo file: HTML + CSS + JS, nessun framework, nessun build step. Si modifica questo. |
| `src/build-site.sh` | Avvolge il sorgente in `index.html` (doctype, viewport, icona) e fa commit + push. |
| `src/build-top-stories.py` | Costruisce `top/` dai dati Instagram raccolti (vedi sotto). |
| `src/supabase-schema.sql` | Schema del database condiviso: tabelle `photos`, `layouts`, bucket `photos`, regole di accesso. |
| `src/README.md` | Storia del progetto, decisioni prese (font, stile CRM, PIN, ecc.). |

## I tre pezzi che fanno funzionare il tool

1. **Hosting statico**: GitHub Pages su questo repo, branch `main`, cartella root. Qualsiasi altro hosting statico va bene (Netlify, Vercel, Cloudflare Pages, o una cartella sul server del dominio): basta servire `index.html` e `top/`.
2. **Archivio condiviso**: progetto Supabase `mtcauaazprruxngbcspu` (URL e chiave pubblica `anon` sono nel sorgente, sezione `CFG` in fondo al file, dentro il secondo `<script>`). L'accesso è un **unico account condiviso** (email in `CFG.email`, password = "il codice"). Chi ha la password vede foto e storico di tutti. Per cambiare progetto Supabase: nuovo progetto → esegui `src/supabase-schema.sql` nel SQL Editor → crea l'utente in Authentication → Users (con "auto confirm") → aggiorna `CFG.url`, `CFG.key`, `CFG.email` nel sorgente → `build-site.sh`.
3. **Dati Instagram per la sezione Reference**: prodotti da una routine giornaliera che gira nel vault "Second Brain" di Giulio (task `abf-stories-daily-pull`, ore 12:00, fallback 17:00). Legge le stories attive via Instagram Graph API (token nel suo ambiente, mai nella pagina), salva `Intelligence/market/abf-stories/data/YYYY-MM-DD.json` + media, poi lancia `build-top-stories.py` e `build-site.sh`. Se il progetto passa di mano, questa routine va replicata dove sta il token Meta: lo script legge cartelle `data/` e `media/` con quel formato (esempio di record in fondo a questo file).

## Accessi da concedere a chi prende in carico

- **GitHub**: Settings → Collaborators di `Giulioat/storie-abf` (o trasferimento del repo: Settings → Danger Zone → Transfer). Dopo il trasferimento, riattivare Pages (Settings → Pages → Deploy from branch `main` / root) e aggiornare la riga `git push` in `build-site.sh` se cambia il remote.
- **Supabase**: Organization → Team → Invite (email del nuovo responsabile). Oppure ricreare il progetto come al punto 2.
- **Dominio**: per usare `storie.metodoabf.app` (o altro) su GitHub Pages: record DNS `CNAME storie → giulioat.github.io` (o `<nuovo-utente>.github.io` dopo il trasferimento), poi Settings → Pages → Custom domain → `storie.metodoabf.app` → Enforce HTTPS. GitHub crea il file `CNAME` nel repo: non cancellarlo con i build successivi (build-site.sh usa `git add -A`, quindi lo conserva).
- **Codice di accesso**: è la password dell'utente condiviso in Supabase (Authentication → Users → reset password). Il PIN `HASH` nel sorgente vale solo come ripiego locale quando il cloud non è raggiungibile.

## Come si modifica il tool

1. Clona il repo, apri `src/impaginatore-storie-abf.html`.
2. Prova in locale: `python3 -m http.server 8000` nella root del repo e apri `http://localhost:8000/index.html` dopo aver eseguito `bash src/build-site.sh` (oppure incolla il sorgente in un file con doctype). Il login cloud funziona anche da localhost.
3. Modifica, poi `bash src/build-site.sh`: rigenera `index.html` e pusha. Pages aggiorna in 1-2 minuti.

Struttura interna del sorgente, per orientarsi: token CSS (`:root`, tema chiaro/scuro), shell con sidebar stile CRM ABF, pannelli Copy / Foto / Storie / Storico / Reference, poi tre script: (1) tema e navigazione, (2) il tool (stato, libreria foto con layer `cloud`/locale, split del copy in storie e blocchi, `draw()` condiviso tra anteprima ed export, card con drag dei blocchi, swatch colore, "Spezza qui", export/download/share, storico, reference, `window.__abfStart`), (3) il gate di accesso (login Supabase con ripiego PIN).

## Modello dati

- `photos`: `id` (text), `path` (file nel bucket `photos`, `<id>.jpg`), `added` (ms epoch), `used` (contatore di utilizzo, per la rotazione "meno usate prima").
- `layouts`: `id`, `date`, `copy` (testo incollato), `stories` (JSON: `[{id, photoId, ref?, blocks:[{id, text, x, y, size, style, font}]}]`, con `x`/`y` frazioni 0-1 del centro del blocco su 1080×1920), `updated`.
- Sintassi nel testo dei blocchi: `*parola*` = colore evidenziazione dello stile; `[c=#hex]parole[/c]` = colore scelto; `\n` = a capo forzato.

## Formato dei dati Instagram letti da build-top-stories.py

```json
{"date": "2026-09-05", "captured_at": "...", "stories": [
  {"id": "18164024452466862", "media_type": "IMAGE", "permalink": "https://www.instagram.com/stories/asiabaldoni/...",
   "timestamp": "2026-09-05T05:57:01+0000", "reach": 2967, "replies": 14, "navigation": 2868}
]}
```
Alcune catture hanno `reach/replies/navigation` dentro un sottocampo `insights`: lo script gestisce entrambi. I media stanno in `media/YYYY-MM-DD/<story_id>.jpg|mp4`. Sequenza = stesso giorno locale (Europe/Rome), gap ≤ 3h tra storie consecutive; classifica per risposte totali.

## Cose note da sapere

- Il font "Classic" di Instagram è proprietario: Gelasio (Georgia con numeri allineati) è la scelta più vicina, con selettore per chi vuole altro.
- Le insights delle stories esistono solo mentre la storia è attiva (24-48h): lo storico Reference parte dal 24/08/2026 e cresce solo se la routine gira.
- L'artifact su claude.ai è una copia di comodo: lì il cloud non è raggiungibile (CSP) e la pagina ripiega su archivio locale + PIN. La versione buona è il sito.
