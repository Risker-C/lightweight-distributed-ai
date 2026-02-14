const { requestJson } = require('../lib/http');
const { GatewayError } = require('../lib/errors');

class CloudRunClient {
  constructor(config, logger, globalTimeoutMs = 15000) {
    this.config = config || {};
    this.logger = logger;
    this.timeoutMs = globalTimeoutMs;
  }

  headers() {
    if (!this.config.token) throw new GatewayError(500, 'Cloud Run OAuth token is not configured');
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.config.token}`,
    };
  }

  url(pathname) {
    const base = (this.config.api_base || 'https://run.googleapis.com').replace(/\/$/, '');
    return `${base}${pathname}`;
  }

  async submit(task = {}) {
    const project = task.project || this.config.project;
    const region = task.region || this.config.region;
    const job = task.job || this.config.job;

    if (!project || !region || !job) {
      throw new GatewayError(400, 'Cloud Run project/region/job are required');
    }

    const { payload } = await requestJson(
      this.url(`/v2/projects/${project}/locations/${region}/jobs/${job}:run`),
      {
        method: 'POST',
        headers: this.headers(),
        body: JSON.stringify({ overrides: task.overrides || {} }),
      },
      this.timeoutMs,
    );

    return {
      external_id: payload?.name,
      status: 'submitted',
      details: payload,
    };
  }

  async getStatus(externalId) {
    if (!externalId) throw new GatewayError(400, 'Cloud Run operation name is required');

    const opPath = externalId.startsWith('projects/') ? `/v2/${externalId}` : externalId;
    const { payload } = await requestJson(this.url(opPath), { method: 'GET', headers: this.headers() }, this.timeoutMs);

    let status = 'running';
    if (payload?.done === true) {
      status = payload.error ? 'failed' : 'completed';
    }

    return {
      status,
      provider_status: payload?.done ? 'done' : 'running',
      details: payload,
    };
  }

  async getLogs(externalId) {
    return {
      logs: 'Cloud Run logs are available in Cloud Logging. Query by operation name / execution id.',
      operation: externalId,
    };
  }

  async cancel(externalId) {
    if (!externalId) throw new GatewayError(400, 'Cloud Run operation name is required');

    const opPath = externalId.startsWith('projects/') ? `/v2/${externalId}:cancel` : `${externalId}:cancel`;
    const { payload } = await requestJson(
      this.url(opPath),
      { method: 'POST', headers: this.headers(), body: '{}' },
      this.timeoutMs,
    );

    return { status: 'cancelled', details: payload };
  }
}

module.exports = { CloudRunClient };
