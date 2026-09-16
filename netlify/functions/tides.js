const ALLOWED_SITES = new Set([
  'saint-nazaire', 'le-croisic', 'le-pouliguen', 'pornic',
  'pointe-de-saint-gildas', 'saint-malo', 'brest', 'lorient',
  'concarneau', 'quiberon-port-haliguen', 'vannes', 'cherbourg',
  'le-havre', 'ouistreham', 'granville', 'calais', 'dunkerque',
  'la-rochelle-pallice', 'royan', 'pauillac', 'arcachon-jetee-d-eyrac'
]);

const ATTRIBUTION = 'Données de marée fournies par api-maree.fr sous licence CC BY, calculées à partir de composantes harmoniques Ifremer / PREVIMER, elles-mêmes sous licence CC BY.';

function reply(statusCode, body, cacheControl) {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': cacheControl || 'no-store'
    },
    body: JSON.stringify(body)
  };
}

function isDate(value) {
  return /^\d{4}-\d{2}-\d{2}$/.test(value || '') && !Number.isNaN(Date.parse(value + 'T12:00:00Z'));
}

exports.handler = async function handler(event) {
  if (event.httpMethod !== 'GET') return reply(405, { error: 'method_not_allowed' });

  const key = process.env.API_MAREE_KEY;
  if (!key) return reply(503, { error: 'api_key_not_configured' });

  const site = event.queryStringParameters && event.queryStringParameters.site;
  const from = event.queryStringParameters && event.queryStringParameters.from;
  const to = event.queryStringParameters && event.queryStringParameters.to;

  if (!ALLOWED_SITES.has(site) || !isDate(from) || !isDate(to)) {
    return reply(400, { error: 'invalid_parameters' });
  }

  const fromDate = new Date(from + 'T12:00:00Z');
  const toDate = new Date(to + 'T12:00:00Z');
  const durationDays = Math.round((toDate - fromDate) / 86400000);
  if (durationDays < 0 || durationDays > 6) return reply(400, { error: 'invalid_range' });

  const dayAfter = new Date(toDate);
  dayAfter.setUTCDate(dayAfter.getUTCDate() + 1);
  const dayAfterKey = dayAfter.toISOString().slice(0, 10);
  const base = 'https://api-maree.fr';
  const common = 'site=' + encodeURIComponent(site) + '&tz=Europe%2FParis&key=' + encodeURIComponent(key);
  const extremaUrl = base + '/tide-extrema?' + common + '&from=' + from + '&to=' + to;
  const levelsUrl = base + '/water-levels?' + common + '&from=' + from + 'T00%3A00&to=' + dayAfterKey + 'T00%3A00&step=10';

  try {
    const responses = await Promise.all([
      fetch(extremaUrl, { headers: { Accept: 'application/json' } }),
      fetch(levelsUrl, { headers: { Accept: 'application/json' } })
    ]);
    if (!responses[0].ok || !responses[1].ok) {
      return reply(502, { error: 'upstream_error', status: [responses[0].status, responses[1].status] });
    }

    const payloads = await Promise.all(responses.map((response) => response.json()));
    return reply(200, {
      site: payloads[0].site_id,
      timezone: payloads[0].timezone,
      days: payloads[0].data || [],
      levels: payloads[1].data || [],
      attribution: (payloads[0].source && payloads[0].source.attribution) || ATTRIBUTION,
      status_notice: (payloads[0].source && payloads[0].source.status_notice) || 'Valeurs indicatives, impropres à la navigation.'
    }, 'public, max-age=900, s-maxage=3600, stale-while-revalidate=86400');
  } catch (error) {
    console.error('api-maree.fr:', error.message);
    return reply(502, { error: 'upstream_unavailable' });
  }
};
