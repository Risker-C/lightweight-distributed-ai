class GatewayError extends Error {
  constructor(statusCode, message, details = null) {
    super(message);
    this.name = 'GatewayError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

module.exports = { GatewayError };
