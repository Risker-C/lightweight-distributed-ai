const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');

const { createRouter } = require('../api/router');
const { createAuth } = require('../lib/auth');

function logger() {
  return { info() {}, warn() {}, error() {} };
}

test('API requires bearer token', async () => {
  const taskService = {
    async submitTask() { return { id: '1', status: 'submitted' }; },
    async getStatus() { return { id: '1', status: 'running' }; },
    async getLogs() { return { id: '1', logs: 'ok' }; },
    async cancelTask() { return { id: '1', status: 'cancelled' }; },
  };

  const router = createRouter({
    taskService,
    auth: createAuth({ bearer_tokens: 'test-token' }),
    logger: logger(),
  });

  const server = http.createServer(router);
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();

  const noAuthResp = await fetch(`http://127.0.0.1:${port}/v1/tasks/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider: 'nomad', task: {} }),
  });
  assert.equal(noAuthResp.status, 401);

  const authResp = await fetch(`http://127.0.0.1:${port}/v1/tasks/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer test-token',
    },
    body: JSON.stringify({ provider: 'nomad', task: {} }),
  });

  assert.equal(authResp.status, 202);
  const body = await authResp.json();
  assert.equal(body.id, '1');

  await new Promise((resolve) => server.close(resolve));
});
