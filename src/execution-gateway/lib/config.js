const fs = require('node:fs');
const path = require('node:path');

function parseScalar(value) {
  const v = value.trim();
  if (v === 'true') return true;
  if (v === 'false') return false;
  if (v === 'null') return null;
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    return v.slice(1, -1);
  }
  if (!Number.isNaN(Number(v)) && v !== '') return Number(v);
  return v;
}

function parseSimpleYaml(content) {
  const lines = content.split(/\r?\n/);
  const root = {};
  const stack = [{ indent: -1, node: root }];

  for (const rawLine of lines) {
    if (!rawLine.trim() || rawLine.trim().startsWith('#')) continue;

    const indent = rawLine.match(/^\s*/)[0].length;
    const line = rawLine.trim();
    const separatorIndex = line.indexOf(':');
    if (separatorIndex === -1) continue;

    const key = line.slice(0, separatorIndex).trim();
    const rest = line.slice(separatorIndex + 1).trim();

    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) {
      stack.pop();
    }

    const parent = stack[stack.length - 1].node;

    if (rest === '') {
      parent[key] = {};
      stack.push({ indent, node: parent[key] });
    } else {
      parent[key] = parseScalar(rest);
    }
  }

  return root;
}

function mergeDeep(target, source) {
  const output = { ...target };
  for (const [key, value] of Object.entries(source || {})) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      output[key] = mergeDeep(output[key] || {}, value);
    } else {
      output[key] = value;
    }
  }
  return output;
}

function loadConfig(configPath = path.join(process.cwd(), 'config.yaml')) {
  const defaults = {
    server: {
      host: '0.0.0.0',
      port: 8080,
      request_timeout_ms: 15000,
    },
    tls: {
      enabled: false,
      cert_file: './certs/server.crt',
      key_file: './certs/server.key',
    },
    auth: {
      bearer_tokens: '',
      allow_unauthenticated: false,
    },
    retry: {
      attempts: 3,
      base_delay_ms: 200,
      max_delay_ms: 2000,
    },
    logging: {
      level: 'info',
      file: '',
    },
    providers: {
      nomad: {
        enabled: true,
        endpoint: 'http://localhost:4646',
        token: '',
        namespace: 'default',
      },
      github_actions: {
        enabled: false,
        api_base: 'https://api.github.com',
        owner: '',
        repo: '',
        token: '',
      },
      cloud_run: {
        enabled: false,
        api_base: 'https://run.googleapis.com',
        project: '',
        region: '',
        token: '',
        job: '',
      },
    },
  };

  if (!fs.existsSync(configPath)) {
    return defaults;
  }

  const raw = fs.readFileSync(configPath, 'utf8');
  let parsed;
  if (raw.trim().startsWith('{')) {
    parsed = JSON.parse(raw);
  } else {
    parsed = parseSimpleYaml(raw);
  }

  return mergeDeep(defaults, parsed);
}

module.exports = { loadConfig };
