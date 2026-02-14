const crypto = require('node:crypto');
const { withRetry } = require('../lib/retry');
const { GatewayError } = require('../lib/errors');

class TaskService {
  constructor({ providers, store, retry, logger }) {
    this.providers = providers;
    this.store = store;
    this.retry = retry || {};
    this.logger = logger;
  }

  getProvider(name) {
    const provider = this.providers[name];
    if (!provider) throw new GatewayError(400, `Unsupported provider: ${name}`);
    return provider;
  }

  async submitTask(payload = {}) {
    const providerName = payload.provider;
    const taskPayload = payload.task || {};
    const metadata = payload.metadata || {};

    if (!providerName) throw new GatewayError(400, 'provider is required');

    const provider = this.getProvider(providerName);
    const id = payload.id || crypto.randomUUID();

    this.store.create({
      id,
      provider: providerName,
      status: 'queued',
      external_id: null,
      task: taskPayload,
      metadata,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });

    try {
      const result = await withRetry(() => provider.submit(taskPayload), this.retry, this.logger);
      const updated = this.store.update(id, {
        status: result.status || 'submitted',
        external_id: result.external_id || null,
        details: result.details || null,
      });
      return updated;
    } catch (err) {
      this.store.update(id, { status: 'failed', error: err.message });
      throw err;
    }
  }

  async getStatus(id) {
    const task = this.store.get(id);
    if (!task) throw new GatewayError(404, 'Task not found');

    const provider = this.getProvider(task.provider);
    if (!provider.getStatus) return task;

    try {
      const status = await withRetry(() => provider.getStatus(task.external_id, task.task), this.retry, this.logger);
      return this.store.update(id, {
        status: status.status || task.status,
        provider_status: status.provider_status,
        details: status.details || task.details,
      });
    } catch (err) {
      this.logger.warn('Failed to refresh status; returning last known state', {
        task_id: id,
        error: err.message,
      });
      return task;
    }
  }

  async getLogs(id) {
    const task = this.store.get(id);
    if (!task) throw new GatewayError(404, 'Task not found');

    const provider = this.getProvider(task.provider);
    if (!provider.getLogs) {
      return { id, provider: task.provider, logs: 'Log retrieval is not supported by provider' };
    }

    const logs = await withRetry(() => provider.getLogs(task.external_id, task.task), this.retry, this.logger);
    return {
      id,
      provider: task.provider,
      ...logs,
    };
  }

  async cancelTask(id) {
    const task = this.store.get(id);
    if (!task) throw new GatewayError(404, 'Task not found');

    const provider = this.getProvider(task.provider);
    if (provider.cancel) {
      await withRetry(() => provider.cancel(task.external_id, task.task), this.retry, this.logger);
    }

    return this.store.update(id, {
      status: 'cancelled',
    });
  }
}

module.exports = { TaskService };
