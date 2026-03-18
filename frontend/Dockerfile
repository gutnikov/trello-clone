FROM node:20-slim AS builder

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@10 --activate

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM node:20-slim

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@10 --activate

COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/package.json /app/
COPY --from=builder /app/node_modules /app/node_modules

EXPOSE 3000

CMD ["node", "dist/server/server.js"]
