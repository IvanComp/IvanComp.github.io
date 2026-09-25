/**
 * Configurazione una tantum dopo aver importato il file XLSX in Google Sheets:
 * 1. Apri Estensioni > Apps Script.
 * 2. Incolla questo file, salva e avvia configuraCheckbox.
 * 3. Autorizza lo script quando Google lo richiede.
 *
 * Dopo la configurazione, onEdit sincronizza automaticamente la selezione
 * tra "Tutti i giocatori" e il relativo foglio per ruolo.
 */

const FOGLI_GIOCATORI = [
  'Tutti i giocatori',
  'Portieri',
  'Difensori',
  'Centrocampisti',
  'Attaccanti',
];

const PRIMA_RIGA_DATI = 5;
const COLONNA_CHECKBOX = 3;
const COLONNA_NOME = 5;
const COLONNA_SQUADRA = 6;

function configuraCheckbox() {
  const file = SpreadsheetApp.getActiveSpreadsheet();

  FOGLI_GIOCATORI.forEach((nomeFoglio) => {
    const foglio = file.getSheetByName(nomeFoglio);
    if (!foglio || foglio.getLastRow() < PRIMA_RIGA_DATI) return;

    const numeroRighe = foglio.getLastRow() - PRIMA_RIGA_DATI + 1;
    const intervallo = foglio.getRange(PRIMA_RIGA_DATI, COLONNA_CHECKBOX, numeroRighe, 1);
    const valori = intervallo.getValues();
    const testi = intervallo.getDisplayValues();
    const selezioni = valori.map((riga, indice) => {
      const testo = String(testi[indice][0] || '').trim().toLowerCase();
      return [riga[0] === true || testo === '☑' || testo === 'true'];
    });

    intervallo.clearDataValidations();
    intervallo.insertCheckboxes();
    intervallo.setValues(selezioni);
  });

  sincronizzaTutteLeSelezioni_();
}

function onEdit(evento) {
  if (!evento || !evento.range) return;

  const cella = evento.range;
  const foglio = cella.getSheet();
  if (!FOGLI_GIOCATORI.includes(foglio.getName())) return;
  if (cella.getRow() < PRIMA_RIGA_DATI || cella.getColumn() !== COLONNA_CHECKBOX) return;
  if (cella.getNumRows() !== 1 || cella.getNumColumns() !== 1) return;

  const selezionato = cella.isChecked();
  if (selezionato === null) return;

  const nome = String(foglio.getRange(cella.getRow(), COLONNA_NOME).getDisplayValue()).trim();
  const squadra = String(foglio.getRange(cella.getRow(), COLONNA_SQUADRA).getDisplayValue()).trim();
  if (!nome) return;

  sincronizzaGiocatore_(evento.source, nome, squadra, selezionato);
}

function sincronizzaGiocatore_(file, nome, squadra, selezionato) {
  FOGLI_GIOCATORI.forEach((nomeFoglio) => {
    const foglio = file.getSheetByName(nomeFoglio);
    if (!foglio || foglio.getLastRow() < PRIMA_RIGA_DATI) return;

    const numeroRighe = foglio.getLastRow() - PRIMA_RIGA_DATI + 1;
    const anagrafica = foglio
      .getRange(PRIMA_RIGA_DATI, COLONNA_NOME, numeroRighe, 2)
      .getDisplayValues();

    anagrafica.forEach((riga, indice) => {
      if (String(riga[0]).trim() === nome && String(riga[1]).trim() === squadra) {
        const checkbox = foglio.getRange(PRIMA_RIGA_DATI + indice, COLONNA_CHECKBOX);
        if (checkbox.isChecked() !== selezionato) checkbox.setValue(selezionato);
      }
    });
  });
}

function sincronizzaTutteLeSelezioni_() {
  const file = SpreadsheetApp.getActiveSpreadsheet();
  const selezionati = new Set();

  FOGLI_GIOCATORI.forEach((nomeFoglio) => {
    const foglio = file.getSheetByName(nomeFoglio);
    if (!foglio || foglio.getLastRow() < PRIMA_RIGA_DATI) return;
    const numeroRighe = foglio.getLastRow() - PRIMA_RIGA_DATI + 1;
    const dati = foglio.getRange(PRIMA_RIGA_DATI, COLONNA_CHECKBOX, numeroRighe, 4).getValues();
    dati.forEach((riga) => {
      if (riga[0] === true) selezionati.add(`${String(riga[2]).trim()}\u0000${String(riga[3]).trim()}`);
    });
  });

  FOGLI_GIOCATORI.forEach((nomeFoglio) => {
    const foglio = file.getSheetByName(nomeFoglio);
    if (!foglio || foglio.getLastRow() < PRIMA_RIGA_DATI) return;
    const numeroRighe = foglio.getLastRow() - PRIMA_RIGA_DATI + 1;
    const anagrafica = foglio.getRange(PRIMA_RIGA_DATI, COLONNA_NOME, numeroRighe, 2).getValues();
    const valori = anagrafica.map((riga) => [
      selezionati.has(`${String(riga[0]).trim()}\u0000${String(riga[1]).trim()}`),
    ]);
    foglio.getRange(PRIMA_RIGA_DATI, COLONNA_CHECKBOX, numeroRighe, 1).setValues(valori);
  });
}
