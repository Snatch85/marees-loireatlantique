const assert = require('assert');
const { handler } = require('../netlify/functions/tides');

(async () => {
  delete process.env.API_MAREE_KEY;
  const missingKey = await handler({
    httpMethod: 'GET',
    queryStringParameters: { site: 'saint-nazaire', from: '2026-09-16', to: '2026-09-22' }
  });
  assert.strictEqual(missingKey.statusCode, 503);

  process.env.API_MAREE_KEY = 'test-key';
  const invalidSite = await handler({
    httpMethod: 'GET',
    queryStringParameters: { site: 'not-allowed', from: '2026-09-16', to: '2026-09-22' }
  });
  assert.strictEqual(invalidSite.statusCode, 400);

  const invalidRange = await handler({
    httpMethod: 'GET',
    queryStringParameters: { site: 'saint-nazaire', from: '2026-09-16', to: '2026-09-30' }
  });
  assert.strictEqual(invalidRange.statusCode, 400);

  const requestedUrls = [];
  global.fetch = async (url) => {
    requestedUrls.push(url);
    const isExtrema = url.includes('/tide-extrema?');
    return {
      ok: true,
      status: 200,
      json: async () => isExtrema ? {
        site_id: 'saint-nazaire',
        timezone: 'Europe/Paris',
        source: { attribution: 'Attribution CC BY', status_notice: 'Valeurs indicatives' },
        data: [{ date: '2026-09-16', extrema: [{ type: 'PM', time: '07:40', height: 5.141, coef: 70 }] }]
      } : {
        data: [{ time: '2026-09-16T07:40:00+02:00', height: 5.141 }]
      }
    };
  };
  const success = await handler({
    httpMethod: 'GET',
    queryStringParameters: { site: 'saint-nazaire', from: '2026-09-16', to: '2026-09-22' }
  });
  const payload = JSON.parse(success.body);
  assert.strictEqual(success.statusCode, 200);
  assert.strictEqual(payload.days[0].extrema[0].coef, 70);
  assert.strictEqual(payload.attribution, 'Attribution CC BY');
  assert.strictEqual(payload.status_notice, 'Valeurs indicatives');
  assert.strictEqual(requestedUrls.length, 2);
  assert.ok(requestedUrls.every((url) => url.includes('key=test-key')));
  delete global.fetch;
  console.log('OK — fonction Netlify protégée et paramètres validés');
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
