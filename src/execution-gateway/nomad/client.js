const { requestJson } = require('../lib/http');
const { GatewayError } = require('../lib/errors');

function encodePath(pathPart) {
  return encodeURIComponent(pathPart).replace(/%2F/g, '/');
}

class NomadClient {
  constructor(config, logger, globalTimeoutMs = 15000) {
    this.config = config || {};
    this.logger = logger;
    this.timeoutMs = globalTimeoutMs;
  }

  buildHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (this.config.token) {
      headers['X-Nomad-Token'] = this.config.token;
    }
    return headers;
  }

  buildUrl(pathname, params = {}) {
    const base = (this.config.endpoint || 'http://localhost:4646').replace(/\/$/, '');
    const url = new URL(base + pathname);

    if (this.config.namespace) {
      url.searchParams.set('namespace', this.config.namespace);
    }

    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null) {
        url.searchParams.set(k, String(v));
      }
    }

    return url.toString();
  }

  buildJobPayload(task = {}) {
    if (task.job && typeof task.job === 'object') return task.job;

    const jobId = task.job_id || task.name || `gateway-${Date.now()}`;
    const image = task.image || 'busybox:latest';
    const command = task.command || 'echo';
    const args = Array.isArray(task.args) ? task.args : ['hello-from-execution-gateway'];

    return {
      Job: {
        ID: jobId,
        Name: task.name || jobId,
        Type: task.type || 'batch',
        Datacenters: ['dc1'],
        TaskGroups: [
          {
            Name: task.group_name || 'group1',
            Tasks: [
              {
                Name: task.task_name || 'task1',
                Driver: 'docker',
                Config: {
                  image,
                  command,
                  args,
                },
                Resources: {
                  CPU: Number(task.cpu || 100),
                  MemoryMB: Number(task.memory_mb || 128),
                },
              },
            ],
          },
        ],
      },
    };
  }

  async submit(task) {
    const payload = this.buildJobPayload(task);
    const url = this.buildUrl('/v1/jobs');
    const { payload: data } = await requestJson(
      url,
      {
        method: 'POST',
        headers: this.buildHeaders(),
        body: JSON.stringify(payload),
      },
      this.timeoutMs,
    );

    const externalId = task.job_id || payload.Job?.ID || data?.JobID || data?.EvalID;
    return {
      external_id: externalId,
      status: 'submitted',
      details: data,
    };
  }

  async getStatus(externalId) {
    if (!externalId) throw new GatewayError(400, 'Nomad external id is required');

    const url = this.buildUrl(`/v1/job/${encodePath(externalId)}`);
    const { payload: data } = await requestJson(url, { method: 'GET', headers: this.buildHeaders() }, this.timeoutMs);

    let status = 'unknown';
    const nomadStatus = String(data?.Status || '').toLowerCase();
    if (['pending', 'running'].includes(nomadStatus)) status = 'running';
    else if (['dead', 'complete', 'successful'].includes(nomadStatus)) status = 'completed';

    return {
      status,
      provider_status: data?.Status || 'unknown',
      details: data,
    };
  }

  async getLogs(externalId, task = {}) {
    if (!externalId) throw new GatewayError(400, 'Nomad external id is required');

    const allocUrl = this.buildUrl(`/v1/job/${encodePath(externalId)}/allocations`);
    const { payload: allocs } = await requestJson(allocUrl, { method: 'GET', headers: this.buildHeaders() }, this.timeoutMs);

    if (!Array.isArray(allocs) || allocs.length === 0) {
      return { logs: 'No allocations found yet', details: [] };
    }

    const alloc = allocs[0];
    const taskName = task.task_name || Object.keys(alloc.TaskStates || {})[0] || 'task1';
    const logUrl = this.buildUrl(`/v1/client/fs/logs/${encodePath(alloc.ID)}`, {
      task: taskName,
      type: 'stdout',
      origin: 'start',
      offset: 0,
      plain: true,
    });

    const { payload: logs } = await requestJson(logUrl, { method: 'GET', headers: this.buildHeaders() }, this.timeoutMs);
    return {
      logs: typeof logs === 'string' ? logs : JSON.stringify(logs),
      allocation_id: alloc.ID,
      task_name: taskName,
    };
  }

  async cancel(externalId) {
    if (!externalId) throw new GatewayError(400, 'Nomad external id is required');

    const url = this.buildUrl(`/v1/job/${encodePath(externalId)}`);
    const { payload } = await requestJson(
      url,
      {
        method: 'DELETE',
        headers: this.buildHeaders(),
        body: JSON.stringify({ Purge: false }),
      },
      this.timeoutMs,
    );

    return { status: 'cancelled', details: payload };
  }
}

module.exports = { NomadClient };
