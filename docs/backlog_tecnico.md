# Backlog tecnico

## F2 - Path anagrafici hardcodati a 2024

I `mart` leggono ancora i seed anagrafici tramite path `read_parquet(...)` fissati allo snapshot `2024`.

Effetto:

- il progetto funziona sulla baseline attuale
- un refresh futuro delle anagrafiche richiedera' aggiornamento esplicito dei path

## F5 - Validita' temporale con pivot al 31 dicembre

I join anagrafici usano:

```sql
make_date(anno, 12, 31)
```

come data di validita' per l'anno.

Effetto:

- scelta metodologica semplice e stabile per la v1
- da rivalutare se emergono enti con transizioni infra-annuali rilevanti

## F6 - Semantica incompleta di codice_col6/codice_col7/codice_col8

Nel seed `anag-enti` queste colonne restano propagate con naming prudenziale.

Effetto:

- non bloccano la pipeline v1
- non vanno usate come campi interpretativi pubblici finche' la semantica non e' chiarita
