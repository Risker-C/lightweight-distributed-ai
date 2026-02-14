const { readJsonBody, sendJson, sendError } = require('./handlers');
const { GatewayError } = require('../lib/errors');

function extractTaskId(pathname, suffix) {
  const pattern = new RegExp(`^/v1/tasks/([^/]+)/${suffix}$`);
  const match = pathname.match(pattern);
  if (!match) return null;
  return decodeURIComponent(match[1]);
}

function createRouter({ taskService, auth, logger }) {
  return async function route(req, res) {
    try {
      const authResult = auth.authenticate(req);
      if (!authResult.ok) {
        throw new GatewayError(401, authResult.reason || 'Unauthorized');
      }

      const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
      const { pathname } = url;
      const method = req.method;

      if (method === 'GET' && pathname === '/healthz') {
        return sendJson(res, 200, { status: 'ok', time: new Date().toISOString() });
      }

      if (method === 'POST' && pathname === '/v1/tasks/submit') {
        const body = await readJsonBody(req);
        const task = await taskService.submitTask(body);
        logger.info('Task submitted', { task_id: task.id, provider: task.provider });
        return sendJson(res, 202, task);
      }

      const statusId = extractTaskId(pathname, 'status');
      if (method === 'GET' && statusId) {
        const status = await taskService.getStatus(statusId);
        return sendJson(res, 200, status);
      }

      const logsId = extractTaskId(pathname, 'logs');
      if (method === 'GET' && logsId) {
        const logs = await taskService.getLogs(logsId);
        return sendJson(res, 200, logs);
      }

      const cancelId = pathname.match(/^\/v1\/tasks\/([^/]+)$/);
      if (method === 'DELETE' && cancelId) {
        const id = decodeURIComponent(cancelId[1]);
        const canceled = await taskService.cancelTask(id);
        logger.info('Task cancelled', { task_id: id, provider: canceled.provider });
        return sendJson(res, 200, canceled);
      }

      throw new GatewayError(404, 'Route not found');
    } catch (err) {
      return sendError(res, err, logger);
    }
  };
}

module.exports = { createRouter };
