FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Next.js telemetry
ENV NEXT_TELEMETRY_DISABLED 1

# Start as development (or override for prod)
CMD ["npm", "run", "dev"]
