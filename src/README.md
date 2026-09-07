---
type: project
date: 2026-09-07
project: Impaginatore-Storie-ABF
department: Marketing
status: active
priority: high
tags: [stories, instagram, tool, automazione, asia-baldoni]
---

Tool web per [[Asia Baldoni]]: incolla il copy delle stories, il testo viene spezzato per frasi e impaginato in automatico sulle foto della sua libreria, in riquadri bianchi stile Instagram (lo stesso look che oggi fa a mano, riga per riga, con parole evidenziate in rosa). Sposta il testo trascinandolo, cambia foto da una griglia, scarica le immagini 1080×1920 pronte da pubblicare.

**Link per Asia (sito pubblico con PIN):** https://giulioat.github.io/storie-abf/ · codice di accesso `398876` (repo GitHub `Giulioat/storie-abf`, GitHub Pages).
**Link Claude (artifact privato, stesso file):** https://claude.ai/code/artifact/6c898fb3-ec70-4fcd-ab5b-45bd8ddbc3f7
**Sorgente unico:** `impaginatore-storie-abf.html` in questa cartella (vanilla JS + Canvas, nessuna libreria). Dopo ogni modifica: `./build-site.sh` rigenera `~/Documents/storie-abf-site/index.html` e pusha sul repo; l'artifact si ripubblica dallo stesso path.

> [!info] PIN
> Barriera leggera lato client (hash SHA-256 nel sorgente), sufficiente per tenere fuori i curiosi. Nessun dato passa dal sito: foto e storico restano nel browser del dispositivo. Per cambiare PIN: nuovo hash SHA-256 nella costante `HASH` del blocco gate.

## Origine

Replica per ABF del tool mostrato da Leonardo Distaso nel reel https://www.instagram.com/p/Db5FQuutYDG/ (11/08/2026, "impaginatore per le storie costruito in un paio d'ore, risparmia 5-7 ore a settimana"). Il suo flusso: textarea del copy → "Impagina" spezza in frasi (1-2 per storia, riga vuota = storia nuova) → card 9:16 con testo trascinabile → "cambia foto" su galleria locale → "Scarica tutte". Il vantaggio dichiarato: il 100% dell'energia va sul copy, la parte operativa sparisce. Richiesta di [[Giulio Andrea Tartufoli]] il 07/09/2026: stessa cosa, ma per Asia, che oggi scrive il testo a mano su ogni storia dal telefono.

## Come funziona

1. **Foto**: caricate una volta (drag & drop, file picker, o incolla), ridimensionate a 1920px e salvate in IndexedDB del browser. Restano su quel dispositivo, non vanno online. Rotazione automatica: foto meno usate prima, contatore "usata N volte".
2. **Copy**: riga vuota = nuova storia; dentro un paragrafo split per frasi (`.!?…`), N frasi per storia (1/2/3/tutto). `*parola*` diventa rosa, come le evidenziazioni di Asia. Shortcut ⌘↵.
3. **Storie**: ogni card è un canvas con la stessa funzione di disegno usata per l'export, quindi anteprima = file finale. Ogni storia contiene **più blocchi di testo** (richiesta di Giulio 07/09), ognuno con testo, dimensione, stile, font e posizione propri, trascinabile da solo (il drag prende il blocco sotto il dito, altrimenti il più vicino). "+ Blocco di testo" ne aggiunge uno; nel copy una riga che inizia con `+` crea un blocco in più nella stessa storia (tipico: la CTA sotto la frase). **Colore su singole parole**: selezioni le parole nel testo del blocco e tocchi un cerchietto colore (10 swatch, ✕ toglie); nel testo compare `[c=#hex]parola[/c]`, `*parola*` resta la scorciatoia per il rosa. **"Spezza qui"** divide un blocco in due blocchi separati nel punto del cursore (come andare a capo su Instagram); l'invio dentro un blocco manda a capo la riga. Cambia foto, sposta, duplica, elimina, salva singola.
4. **Export**: 1080×1920 JPEG. "Scarica tutte" usa la capability `downloads` (una conferma per file). Da telefono compare "Condividi" (Web Share API con file) per mandarle dritte a Instagram.
5. **Storico e persistenza**: foto in IndexedDB e impaginazioni in localStorage (ultime 40), riapribili e modificabili, autosave della sessione corrente. Le foto si caricano una volta sola per dispositivo e restano lì; la pagina chiede `navigator.storage.persist()` per evitare che Safari le cancelli dopo giorni di inutilizzo (consigliato comunque aggiungere il sito alla schermata Home). Vecchi salvataggi con un solo testo per storia vengono migrati automaticamente al modello a blocchi.

6. **Reference (richiesta di Giulio 07/09)**: sezione con le **5 sequenze di stories con più risposte**, dai dati Instagram Graph API già raccolti dalla routine [[abf-stories-daily-routine]] (`Intelligence/market/abf-stories/data/*.json`). Lo script `build-top-stories.py` unisce tutte le catture (per ogni story id tiene la cattura con più risposte), raggruppa in sequenze (stesso giorno locale, gap ≤ 3h tra una storia e la successiva), ordina per risposte totali e scrive `~/Documents/storie-abf-site/top/top-stories.json` + thumbnail (frame a 1s per i video). Il tool legge quel JSON dallo stesso sito: per ogni sequenza mostra data, orario, numero storie, risposte totali, reach max e la striscia di thumbnail con risposte e orario, cliccabili a schermo intero. **Aggiornamento automatico**: step 7 del task schedulato `abf-stories-daily-pull` (12:00, fallback 17:00) rilancia script + `build-site.sh` ogni giorno. Il token Meta non entra mai nella pagina: gira solo nella routine locale. Sull'artifact Claude la sezione non ha dati (fetch relativo non disponibile) e lo dice; sul sito GitHub Pages funziona.

## Font e stile

**UI = stile del CRM ABF** (sales.metodoabf.app, screenshot forniti da Giulio il 07/09/2026): sidebar bianca a sinistra con wordmark Didone "Asia Baldoni / fitness" (Bodoni Moda) e badge STORIE, nav con stato attivo menta, toggle tema sole/luna/monitor, intestazioni con tile menta + titolo + sottotitolo grigio, card bianche bordo `#d5e3df` raggio 10px, bottoni verde `#217257`, callout `#f0f9f6`, traccia rosa `#faeced`, font Inter. Colori campionati direttamente dagli screenshot, non dalla palette caroselli. Su mobile la sidebar diventa barra in alto.

**Testo storia**: il font "Classic" delle stories Instagram è proprietario e non pubblicamente identificato (verificato 07/09/2026 su typography.guru, FontsArena, Kapwing: nessuna fonte lo nomina). Confronto pixel-per-pixel su "Vi ricordo una cosa" / "Percorsi" contro 27 candidati (Google Fonts + font di sistema iPhone): il più vicino per terminali a goccia, contrasto e peso è **Georgia**, che però ha i numeri "antichi" (1 basso, 9 discendente) mentre Instagram li ha allineati. Default quindi **Gelasio 400** (clone metrico di Georgia su Google Fonts, numeri allineati). Non è identico al 100%: Asia può cambiare font per singola storia o globalmente (Gelasio, Georgia di sistema, Literata, Domine, Source Serif, Lora) e scegliere quello che sul suo telefono le sembra più fedele. Riquadro per riga con angoli arrotondati, padding proporzionale al corpo. Corpo default 52 su base 1080.

## Limiti noti e prossimi passi

- Le foto vivono nel browser del dispositivo: la capability per asset condivisi non è disponibile su questo account. Se Asia usa telefono e Mac deve caricare le foto su entrambi.
- Nessun video: solo immagini statiche.
- Da validare con Asia sul telefono: drag del testo a dito, "Condividi" verso Instagram, dimensione default.
- Fatto 07/09: sezione Reference con le 5 sequenze top per risposte (punto 6) e bottone **"Usa come base"**: crea una sequenza nuova con lo stesso numero di storie (foto dalla libreria, testo segnaposto), e su ogni card resta la miniatura della storia originale in alto a destra, cliccabile a schermo intero, per copiarne foto, quantità di testo e posizione. Il riferimento viene salvato nello Storico insieme alla sequenza.

Collegato a [[abf-stories-daily-routine]] e al target stories della media company (vedi [[strategy]]).
