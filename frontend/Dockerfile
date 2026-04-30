FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm config set registry https://registry.npmmirror.com && npm install

# Copy source
COPY . .

EXPOSE 3001

ENV NEXT_TELEMETRY_DISABLED=1

CMD ["npm", "run", "dev"]
