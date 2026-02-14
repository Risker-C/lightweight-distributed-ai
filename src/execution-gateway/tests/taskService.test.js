const test = require('node:test');
const assert = require('node:assert/strict');

const { TaskService } = require('../services/taskService');
const { TaskStore } = require('../lib/taskStore');

function createMockLogger() {
  return {
    info() {},
    warn() {},
    error() {},
  };
}

test('TaskService submit/status/logs/cancel lifecycle', async () => {
  const provider = {
    async submit(task) {
      return { external_id: `ext-${task.name}`, status: 'submitted', details: { accepted: true } };
    },
    async getStatus() {
      return { status: 'running', provider_status: 'running' };
    },
    async getLogs() {
      return { logs: 'hello world' };
    },
    async cancel() {
      return { status: 'cancelled' };
    },
  };

  const service = new TaskService({
    providers: { nomad: provider },
    store: new TaskStore(),
    retry: { attempts: 1 },
    logger: createMockLogger(),
  });

  const submitted = await service.submitTask({ provider: 'nomad', task: { name: 'demo' } });
  assert.equal(submitted.provider, 'nomad');
  assert.equal(submitted.external_id, 'ext-demo');

  const status = await service.getStatus(submitted.id);
  assert.equal(status.status, 'running');

  const logs = await service.getLogs(submitted.id);
  assert.equal(logs.logs, 'hello world');

  const canceled = await service.cancelTask(submitted.id);
  assert.equal(canceled.status, 'cancelled');
});
