#!/usr/bin/env node
/**
 * nomad-plugin.js
 *
 * Lightweight Nomad API integration helper for Kestra-related automation.
 * - Submit Nomad jobs
 * - Query job / allocation status
 * - Monitor until running/complete
 * - Stop jobs
 */

class NomadPlugin {
  constructor(options = {}) {
    this.nomadAddr = options.nomadAddr || process.env.NOMAD_ADDR || 'http://localhost:4646';
    this.nomadToken = options.nomadToken || process.env.NOMAD_TOKEN || '';
    this.defaultRetries = Number(options.retries ?? 3);
    this.defaultRetryDelayMs = Number(options.retryDelayMs ?? 2000);
  }

  async request(path, { method = 'GET', body, retries, retryDelayMs } = {}) {
    const maxRetries = retries ?? this.defaultRetries;
    const delay = retryDelayMs ?? this.defaultRetryDelayMs;

    const headers = {
      'Content-Type': 'application/json'
    };

    if (this.nomadToken) {
      headers['X-Nomad-Token'] = this.nomadToken;
    }

    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const response = await fetch(`${this.nomadAddr}${path}`, {
          method,
          headers,
          body: body ? JSON.stringify(body) : undefined
        });

        if (!response.ok) {
          const text = await response.text();
          throw new Error(`Nomad API error ${response.status}: ${text}`);
        }

        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
          return await response.json();
        }

        return await response.text();
      } catch (error) {
        lastError = error;
        if (attempt < maxRetries) {
          await new Promise((resolve) => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError;
  }

  buildBatchJob({
    id,
    datacenter = 'dc1',
    command = '/bin/sh',
    args = ['-c', `echo running ${id}; sleep 3; echo done`],
    cpu = 100,
    memoryMb = 128
  }) {
    return {
      Job: {
        ID: id,
        Name: id,
        Type: 'batch',
        Datacenters: [datacenter],
        TaskGroups: [
          {
            Name: 'main',
            Count: 1,
            Tasks: [
              {
                Name: 'main-task',
                Driver: 'raw_exec',
                Config: {
                  command,
                  args
                },
                Resources: {
                  CPU: cpu,
                  MemoryMB: memoryMb
                }
              }
            ]
          }
        ]
      }
    };
  }

  async submitJob(jobPayload) {
    return this.request('/v1/jobs', {
      method: 'POST',
      body: jobPayload
    });
  }

  async getJob(jobId) {
    return this.request(`/v1/job/${jobId}`);
  }

  async getJobSummary(jobId) {
    return this.request(`/v1/job/${jobId}/summary`);
  }

  async getAllocations(jobId) {
    return this.request(`/v1/job/${jobId}/allocations`);
  }

  async stopJob(jobId, purge = true) {
    return this.request(`/v1/job/${jobId}?purge=${purge}`, {
      method: 'DELETE'
    });
  }

  async monitorJob(jobId, options = {}) {
    const timeoutMs = Number(options.timeoutMs ?? 180000);
    const pollMs = Number(options.pollMs ?? 5000);
    const startedAt = Date.now();

    while (Date.now() - startedAt < timeoutMs) {
      const allocations = await this.getAllocations(jobId);

      const statuses = allocations.map((a) => a.ClientStatus);
      if (statuses.some((s) => s === 'failed' || s === 'lost')) {
        return {
          success: false,
          state: 'failed',
          allocations
        };
      }

      if (statuses.some((s) => s === 'running' || s === 'complete')) {
        return {
          success: true,
          state: statuses.includes('running') ? 'running' : 'complete',
          allocations
        };
      }

      await new Promise((resolve) => setTimeout(resolve, pollMs));
    }

    return {
      success: false,
      state: 'timeout'
    };
  }
}

async function main() {
  const [command, ...args] = process.argv.slice(2);
  const plugin = new NomadPlugin();

  if (!command || ['-h', '--help', 'help'].includes(command)) {
    console.log(`Usage:
  node nomad-plugin.js submit <job-id>
  node nomad-plugin.js monitor <job-id>
  node nomad-plugin.js summary <job-id>
  node nomad-plugin.js stop <job-id>
`);
    process.exit(0);
  }

  if (command === 'submit') {
    const jobId = args[0] || `demo-${Date.now()}`;
    const payload = plugin.buildBatchJob({ id: jobId });
    const result = await plugin.submitJob(payload);
    console.log(JSON.stringify({ action: 'submit', jobId, result }, null, 2));
    return;
  }

  if (command === 'monitor') {
    const jobId = args[0];
    if (!jobId) throw new Error('monitor requires <job-id>');

    const result = await plugin.monitorJob(jobId);
    console.log(JSON.stringify({ action: 'monitor', jobId, result }, null, 2));
    process.exit(result.success ? 0 : 1);
  }

  if (command === 'summary') {
    const jobId = args[0];
    if (!jobId) throw new Error('summary requires <job-id>');

    const result = await plugin.getJobSummary(jobId);
    console.log(JSON.stringify({ action: 'summary', jobId, result }, null, 2));
    return;
  }

  if (command === 'stop') {
    const jobId = args[0];
    if (!jobId) throw new Error('stop requires <job-id>');

    const result = await plugin.stopJob(jobId, true);
    console.log(JSON.stringify({ action: 'stop', jobId, result }, null, 2));
    return;
  }

  throw new Error(`Unsupported command: ${command}`);
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err.message || err);
    process.exit(1);
  });
}

module.exports = { NomadPlugin };
