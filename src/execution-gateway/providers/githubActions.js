const { requestJson } = require('../lib/http');
const { GatewayError } = require('../lib/errors');

class GitHubActionsClient {
  constructor(config, logger, globalTimeoutMs = 15000) {
    this.config = config || {};
    this.logger = logger;
    this.timeoutMs = globalTimeoutMs;
  }

  headers() {
    if (!this.config.token) throw new GatewayError(500, 'GitHub token is not configured');
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/vnd.github+json',
      'Authorization': `Bearer ${this.config.token}`,
      'X-GitHub-Api-Version': '2022-11-28',
    };
  }

  url(pathname, params = {}) {
    const base = (this.config.api_base || 'https://api.github.com').replace(/\/$/, '');
    const u = new URL(base + pathname);
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null) u.searchParams.set(k, String(v));
    }
    return u.toString();
  }

  repoPath(suffix) {
    if (!this.config.owner || !this.config.repo) {
      throw new GatewayError(500, 'GitHub owner/repo not configured');
    }
    return `/repos/${this.config.owner}/${this.config.repo}${suffix}`;
  }

  async submit(task = {}) {
    const workflow = task.workflow_id || task.workflow;
    const ref = task.ref || 'main';

    if (!workflow) throw new GatewayError(400, 'workflow_id is required for GitHub Actions');

    await requestJson(
      this.url(this.repoPath(`/actions/workflows/${workflow}/dispatches`)),
      {
        method: 'POST',
        headers: this.headers(),
        body: JSON.stringify({ ref, inputs: task.inputs || {} }),
      },
      this.timeoutMs,
    );

    let externalId = task.run_id || null;
    if (!externalId) {
      const { payload } = await requestJson(
        this.url(this.repoPath(`/actions/workflows/${workflow}/runs`), {
          per_page: 1,
          event: 'workflow_dispatch',
        }),
        { method: 'GET', headers: this.headers() },
        this.timeoutMs,
      );
      externalId = payload?.workflow_runs?.[0]?.id || null;
    }

    return {
      external_id: externalId,
      status: 'submitted',
    };
  }

  async getStatus(externalId) {
    if (!externalId) return { status: 'submitted', provider_status: 'unknown' };

    const { payload } = await requestJson(
      this.url(this.repoPath(`/actions/runs/${externalId}`)),
      { method: 'GET', headers: this.headers() },
      this.timeoutMs,
    );

    let status = 'running';
    if (payload?.status === 'completed') {
      status = payload.conclusion === 'success' ? 'completed' : 'failed';
    }

    return {
      status,
      provider_status: payload?.status,
      conclusion: payload?.conclusion,
      details: payload,
    };
  }

  async getLogs(externalId) {
    if (!externalId) throw new GatewayError(400, 'GitHub run id is required for logs');

    const resp = await fetch(this.url(this.repoPath(`/actions/runs/${externalId}/logs`)), {
      method: 'GET',
      headers: this.headers(),
      redirect: 'manual',
    });

    // GitHub 常见返回 302，并在 location 中给出 zip 下载链接。
    if (resp.status === 302 || resp.status === 301) {
      return {
        logs: 'GitHub logs are a zip archive. Use log_download_url to download.',
        log_download_url: resp.headers.get('location'),
      };
    }

    if (!resp.ok) {
      const text = await resp.text();
      throw new GatewayError(resp.status, `GitHub logs request failed: ${resp.status}`, text.slice(0, 1000));
    }

    const text = await resp.text();
    return {
      logs: text,
      log_download_url: null,
    };
  }

  async cancel(externalId) {
    if (!externalId) throw new GatewayError(400, 'GitHub run id is required for cancel');

    const { payload } = await requestJson(
      this.url(this.repoPath(`/actions/runs/${externalId}/cancel`)),
      { method: 'POST', headers: this.headers() },
      this.timeoutMs,
    );

    return { status: 'cancelled', details: payload };
  }
}

module.exports = { GitHubActionsClient };
