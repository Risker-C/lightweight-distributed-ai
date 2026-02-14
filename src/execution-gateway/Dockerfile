FROM node:20-alpine

WORKDIR /app

COPY package.json ./
COPY index.js ./
COPY api ./api
COPY lib ./lib
COPY nomad ./nomad
COPY providers ./providers
COPY services ./services
COPY config.yaml ./config.yaml

EXPOSE 8080

ENV NODE_ENV=production
ENV CONFIG_PATH=/app/config.yaml

CMD ["node", "index.js"]
