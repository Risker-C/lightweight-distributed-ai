const fs = require('node:fs');

const LEVELS = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
};

class Logger {
  constructor({ level = 'info', file = '' } = {}) {
    this.level = LEVELS[level] ? level : 'info';
    this.file = file;
    this.stream = file ? fs.createWriteStream(file, { flags: 'a' }) : null;
  }

  shouldLog(level) {
    return LEVELS[level] >= LEVELS[this.level];
  }

  write(level, message, meta = {}) {
    if (!this.shouldLog(level)) return;
    const line = JSON.stringify({
      ts: new Date().toISOString(),
      level,
      message,
      ...meta,
    });

    if (level === 'error') {
      console.error(line);
    } else {
      console.log(line);
    }

    if (this.stream) {
      this.stream.write(`${line}\n`);
    }
  }

  debug(message, meta) { this.write('debug', message, meta); }
  info(message, meta) { this.write('info', message, meta); }
  warn(message, meta) { this.write('warn', message, meta); }
  error(message, meta) { this.write('error', message, meta); }
}

module.exports = { Logger };
