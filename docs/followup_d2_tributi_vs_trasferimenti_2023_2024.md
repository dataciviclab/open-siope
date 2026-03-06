# Follow-up D2 - tributi vs trasferimenti nei grandi comuni

## Perimetro

- fonte: `siope_entrate_comuni_agg_labeled`
- annualita': `2023`, `2024`
- taglio: grandi comuni
- filtro analitico di partenza: `is_titolo_9 = false`
- unita' di misura: euro (`importo_totale_eur`)

## Classificazione usata

Per questo follow-up e' stata usata una classificazione minima delle voci:

- `tributi`: `codice_voce like '1.%'`
- `trasferimenti_correnti`: `codice_voce like '2.01.%'`
- `contributi_investimenti`: `codice_voce like '4.02.%'`
- `anticipazioni`: `codice_voce like '7.%'`
- `altro`: tutto il resto

La misura di "dipendenza esterna" usata qui e' data da:

- `trasferimenti_correnti + contributi_investimenti`

E' una proxy utile per la discussion, non una tassonomia definitiva del progetto.

## Quote 2024 nei grandi comuni

| Comune | Tributi % | Dipendenza esterna % | Altro % | Anticipazioni % |
| --- | ---: | ---: | ---: | ---: |
| Roma Capitale | 51,36% | 23,84% | 24,80% | 0,00% |
| Comune di Milano | 38,56% | 17,97% | 43,47% | 0,00% |
| Comune di Napoli | 50,89% | 32,25% | 16,86% | 0,00% |
| Comune di Torino | 48,73% | 27,43% | 23,84% | 0,00% |
| Comune di Genova | 48,27% | 31,13% | 20,60% | 0,00% |
| Comune di Firenze | 43,09% | 23,27% | 33,63% | 0,00% |
| Comune di Venezia | 48,06% | 31,29% | 20,65% | 0,00% |
| Comune di Bologna | 42,96% | 34,33% | 22,71% | 0,00% |
| Comune di Palermo | 47,71% | 42,43% | 9,87% | 0,00% |
| Comune di Catania | 52,72% | 34,41% | 9,55% | 3,32% |

## Segnali principali

- Roma resta sopra il 50% di tributi, con una dipendenza esterna piu contenuta (`23,84%`).
- Napoli mostra un profilo piu sbilanciato verso risorse esterne: `32,25%` tra trasferimenti correnti e contributi agli investimenti.
- Palermo e' il caso piu esposto nel 2024: `42,43%` di dipendenza esterna, molto vicina al peso dei tributi (`47,71%`).
- Bologna e Catania superano il `34%` di dipendenza esterna, ma con assetti diversi: Bologna ha anche una quota alta di `altro`, Catania nel 2024 torna sopra il `52%` di tributi.
- Milano va letta con cautela: la quota di tributi e' relativamente bassa (`38,56%`), ma non perche sia fortemente dipendente dai trasferimenti. Ha invece un peso molto alto della componente `altro` (`43,47%`), che include proventi e altre entrate diverse da tributi e trasferimenti.

## Cambiamenti 2023 -> 2024

- Catania passa da `37,10%` a `52,72%` di tributi, mentre la dipendenza esterna scende da `55,44%` a `34,41%`.
- Bologna scende da `51,78%` a `42,96%` di tributi e sale da `21,76%` a `34,33%` di dipendenza esterna.
- Palermo sale leggermente come quota di tributi (`46,52%` -> `47,71%`), ma anche la dipendenza esterna cresce (`37,90%` -> `42,43%`) per effetto del calo del resto delle entrate.
- Roma resta molto stabile nel rapporto tra tributi e risorse esterne.
- Milano cresce sul lato dei tributi (`34,20%` -> `38,56%`), ma continua a essere un caso peculiare per il peso della componente `altro`.

## Lettura operativa

La domanda "chi dipende di piu dai trasferimenti?" non va letta come un ranking secco.

Ci sono almeno tre profili diversi:

- comuni con tributi sopra il 50% e dipendenza esterna piu contenuta
- comuni con equilibrio piu misto tra tributi e risorse esterne
- comuni in cui la componente `altro` pesa molto e rende il confronto piu complesso

Per questo la follow-up discussion va impostata non solo come confronto tra tributi e trasferimenti, ma come confronto tra:

- tributi propri
- trasferimenti correnti
- contributi agli investimenti
- altre entrate non tecniche
