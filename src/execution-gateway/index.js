const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const https = require('node:https');

const { loadConfig } = require('./lib/config');
const { Logger } = require('./lib/logger');
const { createAuth } = require('./lib/auth');
const { TaskStore } = require('./lib/taskStore');
const { TaskService } = require('./services/taskService');
const { createRouter } = require('./api/router');
const { NomadClient } = require('./nomad/client');
const { GitHubActionsClient } = require('./providers/githubActions');
const { CloudRunClient } = require('./providers/cloudRun');

function buildProviders(config, logger) {
  const timeoutMs = config.server?.request_timeout_ms || 15000;
  const providers = {};

  if (config.providers?.nomad?.enabled) {
    providers.nomad = new NomadClient(config.providers.nomad, logger, timeoutMs);
  }

  if (config.providers?.github_actions?.enabled) {
    providers.github_actions = new GitHubActionsClient(config.providers.github_actions, logger, timeoutMs);
  }

  if (config.providers?.cloud_run?.enabled) {
    providers.cloud_run = new CloudRunClient(config.providers.cloud_run, logger, timeoutMs);
  }

  return providers;
}

function createServer(config) {
  const logger = new Logger(config.logging || {});
  const auth = createAuth(config.auth || {}, logger);
  const store = new TaskStore();
  const providers = buildProviders(config, logger);

  const taskService = new TaskService({
    providers,
    store,
    retry: config.retry || {},
    logger,
  });

  const handler = createRouter({ taskService, auth, logger });

  if (config.tls?.enabled) {
    const certPath = path.resolve(process.cwd(), config.tls.cert_file);
    const keyPath = path.resolve(process.cwd(), config.tls.key_file);

    const tlsOptions = {
      cert: fs.readFileSync(certPath),
      key: fs.readFileSync(keyPath),
    };

    return {
      logger,
      server: https.createServer(tlsOptions, handler),
    };
  }

  return {
    logger,
    server: http.createServer(handler),
  };
}

function main() {
  const configPath = process.env.CONFIG_PATH || path.join(process.cwd(), 'config.yaml');
  const config = loadConfig(configPath);
  const { server, logger } = createServer(config);

  const host = config.server?.host || '0.0.0.0';
  const port = Number(process.env.PORT || config.server?.port || 8080);

  server.listen(port, host, () => {
    logger.info('Execution Gateway started', {
      host,
      port,
      tls: Boolean(config.tls?.enabled),
      providers: Object.keys(config.providers || {}).filter((k) => config.providers[k]?.enabled),
    });
  });

  const shutdown = () => {
    logger.info('Shutting down Execution Gateway');
    server.close(() => process.exit(0));
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

if (require.main === module) {
  main();
}

module.exports = { createServer, buildProviders };
