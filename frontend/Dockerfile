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

# vite preview with TanStack Start needs src/ for router resolution
COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/src /app/src
COPY --from=builder /app/package.json /app/
COPY --from=builder /app/node_modules /app/node_modules
COPY --from=builder /app/vite.config.ts /app/
COPY --from=builder /app/tsconfig.json /app/

EXPOSE 3000

CMD ["pnpm", "preview", "--port", "3000", "--host", "0.0.0.0"]
