const { GatewayError } = require('./errors');

async function requestJson(url, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    const contentType = response.headers.get('content-type') || '';

    let payload;
    if (contentType.includes('application/json')) {
      payload = await response.json();
    } else {
      payload = await response.text();
    }

    if (!response.ok) {
      const details = typeof payload === 'string' ? payload.slice(0, 1000) : payload;
      const err = new GatewayError(response.status, `Upstream request failed: ${response.status}`, details);
      err.status = response.status;
      throw err;
    }

    return { response, payload };
  } catch (err) {
    if (err.name === 'AbortError') {
      const timeoutError = new GatewayError(504, `Upstream timeout after ${timeoutMs}ms`);
      timeoutError.retryable = true;
      throw timeoutError;
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

module.exports = { requestJson };
