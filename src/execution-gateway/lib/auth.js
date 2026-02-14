function normalizeTokens(raw) {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw.map((t) => String(t).trim()).filter(Boolean);
  return String(raw)
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean);
}

function createAuth(config = {}, logger) {
  const tokens = new Set(normalizeTokens(config.bearer_tokens));
  const allowUnauthenticated = Boolean(config.allow_unauthenticated);

  if (!allowUnauthenticated && tokens.size === 0 && logger) {
    logger.warn('No bearer tokens configured; all requests will be rejected');
  }

  return {
    authenticate(req) {
      if (allowUnauthenticated) return { ok: true, principal: 'anonymous' };

      const authHeader = req.headers.authorization || '';
      const [scheme, token] = authHeader.split(' ');
      if (scheme !== 'Bearer' || !token) {
        return { ok: false, reason: 'Missing or invalid Authorization header' };
      }

      if (!tokens.has(token)) {
        return { ok: false, reason: 'Invalid bearer token' };
      }

      return { ok: true, principal: token.slice(0, 6) + '***' };
    },
  };
}

module.exports = { createAuth };
