const { GatewayError } = require('../lib/errors');

async function readJsonBody(req, limitBytes = 1024 * 1024) {
  const chunks = [];
  let total = 0;

  for await (const chunk of req) {
    total += chunk.length;
    if (total > limitBytes) {
      throw new GatewayError(413, 'Request body too large');
    }
    chunks.push(chunk);
  }

  if (chunks.length === 0) return {};

  const raw = Buffer.concat(chunks).toString('utf8');
  try {
    return JSON.parse(raw);
  } catch {
    throw new GatewayError(400, 'Invalid JSON payload');
  }
}

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

function sendError(res, err, logger) {
  const status = err.statusCode || err.status || 500;
  if (status >= 500 && logger) {
    logger.error('Unhandled error', { error: err.message, stack: err.stack });
  }

  sendJson(res, status, {
    error: {
      message: err.message || 'Internal Server Error',
      details: err.details || null,
    },
  });
}

module.exports = {
  readJsonBody,
  sendJson,
  sendError,
};
