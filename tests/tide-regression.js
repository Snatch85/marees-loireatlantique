const fs = require('fs');
const vm = require('vm');

process.env.TZ = 'Europe/Paris';

const source = fs.readFileSync('assets/script.js', 'utf8');
const start = source.indexOf('const J2000_MS');
const end = source.indexOf('// ── Rendu aujourd\'hui');
if (start < 0 || end < 0) throw new Error('Moteur de marée introuvable');

const sandbox = { console, Date, Math, fetch: async () => ({ ok: false, status: 503 }) };
vm.createContext(sandbox);
vm.runInContext(source.slice(start, end) + '\nthis.__tide = { apiEventsForDate, eventCoefficients };', sandbox);

const date = new Date('2026-09-16T12:00:00+02:00');
const days = [{
  date: '2026-09-16',
  extrema: [
    { type: 'BM', time: '02:46', height: 1.57 },
    { type: 'PM', time: '07:55', height: 5.41, coef: 70 },
    { type: 'BM', time: '15:01', height: 1.73 },
    { type: 'PM', time: '20:08', height: 5.19, coef: 63 }
  ]
}];

const events = sandbox.__tide.apiEventsForDate(days, date);
const actual = events.map((event) => [event.type, event.t.getHours() + ':' + String(event.t.getMinutes()).padStart(2, '0'), event.h, event.coef]);
const expected = [
  ['BM', '2:46', 1.57, null],
  ['PM', '7:55', 5.41, 70],
  ['BM', '15:01', 1.73, null],
  ['PM', '20:08', 5.19, 63]
];

if (JSON.stringify(actual) !== JSON.stringify(expected)) {
  throw new Error('Régression des horaires: ' + JSON.stringify(actual));
}
const coefficients = sandbox.__tide.eventCoefficients(events, 0);
if (JSON.stringify(coefficients) !== JSON.stringify([70, 63])) {
  throw new Error('Régression des coefficients: ' + JSON.stringify(coefficients));
}
console.log('OK — horaires et coefficients distincts par pleine mer');
