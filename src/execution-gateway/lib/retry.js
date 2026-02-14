function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function shouldRetry(err) {
  if (!err) return false;
  if (err.retryable === true) return true;
  if (typeof err.statusCode === 'number' && err.statusCode >= 500) return true;
  if (typeof err.status === 'number' && err.status >= 500) return true;
  return Boolean(err.code);
}

async function withRetry(operation, options = {}, logger) {
  const attempts = Number(options.attempts || 3);
  const baseDelayMs = Number(options.base_delay_ms || 200);
  const maxDelayMs = Number(options.max_delay_ms || 2000);

  let lastError = null;
  for (let i = 1; i <= attempts; i += 1) {
    try {
      return await operation();
    } catch (err) {
      lastError = err;
      const retry = i < attempts && shouldRetry(err);
      if (!retry) break;

      const delay = Math.min(baseDelayMs * (2 ** (i - 1)), maxDelayMs);
      if (logger) {
        logger.warn('Operation failed, retrying', {
          attempt: i,
          attempts,
          delay_ms: delay,
          error: err.message,
        });
      }
      await sleep(delay);
    }
  }

  throw lastError;
}

module.exports = { withRetry };
