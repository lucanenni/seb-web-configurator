# seb-web-configurator

[English](README.md) · **Italiano**

Pagina web che crea e modifica i **file di configurazione `.seb` di Safe Exam Browser (SEB)**, interamente nel browser. Nulla viene inviato a un server. Funziona allo stesso modo su macOS, Windows e browser mobili, quindi non serve aprire SEB per preparare un file.

Funziona con qualunque test online ed è nata per un caso frequente: far svolgere un **Google Modulo** in SEB (link, schermo intero, nessuna altra finestra o scheda, controllo WiFi disattivato, password di uscita), con una **modalità avanzata** che mostra le impostazioni di SEB.

> Progetto non ufficiale, non affiliato a ETH Zurich né al progetto SEB. Impostazioni, valori predefiniti, etichette e suggerimenti derivano dai repository open source di SEB (configuratore Windows e preferenze macOS).

## Funzioni

- **Modalità semplice**: link del test (un Google Modulo o qualunque altro indirizzo web), avvio a schermo intero (attivo di default), password d'esame facoltativa (cifra il file), password di uscita facoltativa. Il file blocca sempre nuove finestre e schede e disattiva il controllo del WiFi.
- **Correzione del link di modifica**: un link `…/edit` viene convertito in `…/viewform`.
- **Modalità avanzata** (interruttore nella barra in alto, accanto a quello della lingua): 343 impostazioni in 13 schede, con etichette e suggerimenti di SEB, ricerca e pulsante di ripristino per ogni impostazione. Nel file finiscono solo quelle che modifichi.
  - 99 impostazioni comuni a Windows e macOS, 67 segnate **Windows**, 139 segnate **Mac**, 38 segnate **iOS**.
  - Editor per le impostazioni complesse: processi permessi e vietati (con gli elenchi predefiniti di SEB e i campi solo Mac), regole del filtro URL, proxy, **risorse aggiuntive** (con file incorporati e regole URL per risorsa), **certificati incorporati** (`.cer`, `.crt`, `.der`, `.pem`, `.p12`), versioni di SEB ammesse, elenco di esclusione del filtro URL, configurazione SEB Server e tipi di file iOS.
- **Apertura di un `.seb` esistente** (in chiaro o cifrato con password) per modificarlo. Gli hash delle password salvate si mantengono; le impostazioni che lo strumento non conosce restano intatte.
- Interfaccia **italiano / inglese**. Segue la lingua del browser (italiano per i browser in italiano, inglese per tutti gli altri); la scelta fatta con il selettore in alto a destra viene ricordata.
- La cifratura usa lo schema atteso da SEB (RNCryptor v3, prefisso `pswd`), realizzato con la Web Crypto API.

## Uso

Aprilo online su **https://lucanenni.github.io/seb-web-configurator/**, oppure apri [`docs/index.html`](docs/index.html) in un browser recente, oppure pubblica la cartella `docs/` su un qualsiasi server statico. Per usarlo non serve compilare nulla.

1. Incolla il link del test, scegli le opzioni e premi **Crea il file .seb** (i pulsanti **Apri un .seb esistente…** e **Crea** sono nella barra in alto).
2. Invia `esame.seb` agli studenti (con la password, se l'hai impostata).
3. Gli studenti aprono il file con un doppio clic: parte SEB e si apre il modulo.

## Compilazione dai sorgenti

Servono Python 3 e Node 20 o successivo. La pagina compilata è già in `docs/`: il passaggio dello schema serve solo per aggiornare le impostazioni da sorgenti SEB più recenti.

```bash
# 1. (facoltativo) rigenera data/schema.json da cloni dei repository di SEB
git clone --depth 1 https://github.com/SafeExamBrowser/seb-win-refactoring.git ../seb-win-refactoring
git clone --depth 1 https://github.com/SafeExamBrowser/seb-mac.git ../seb-mac
npm run schema

# 2. compila docs/index.html da src/ e data/
npm run build

# 3. esegui i test
npm test
```

| Percorso | Contenuto |
| --- | --- |
| `src/index.template.html` | L'intera app (HTML, CSS, JS, entrambe le lingue) |
| `data/schema.json` | Impostazioni, valori predefiniti, etichette, suggerimenti, scelte |
| `tools/extract_schema.py` | Costruisce lo schema dai sorgenti di SEB |
| `tools/build.py` | Inserisce lo schema nel modello |
| `docs/index.html` | Il risultato in un solo file |
| `tests/` | Giro completo del formato del file, controlli sullo schema |

## Limiti

- I file cifrati con un certificato non si possono aprire. Icone delle risorse e sotto-risorse annidate non sono modificabili: quando apri un file restano così come sono.
- Le risorse aggiuntive le legge SEB per macOS; il codice attuale di SEB per Windows non le legge.
- Etichette e suggerimenti sono in inglese, come in SEB.
- Le impostazioni solo Windows o solo Mac vengono ignorate dall'altro sistema.
- I file generati sono stati controllati nella struttura e con un giro completo. Prova sempre un file su entrambi i sistemi prima di un esame.
- SEB non può attivare la **modalità blocco** di Google Moduli, che richiede un Chromebook gestito: SEB usa il proprio blocco. Non impedisce un secondo monitor fisico o un altro dispositivo.

## Licenza

[Mozilla Public License 2.0](LICENSE), la stessa licenza di SEB. `data/schema.json` contiene etichette, suggerimenti e valori predefiniti derivati dal codice sorgente di SEB (© ETH Zurich, IT Services, MPL-2.0); vedi [NOTICE](NOTICE). Il progetto non è affiliato né approvato da ETH Zurich o dal progetto SEB.
