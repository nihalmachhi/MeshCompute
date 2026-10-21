FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_COORDINATOR_URL=http://localhost:8000/api/v1
ENV VITE_COORDINATOR_URL=$VITE_COORDINATOR_URL
RUN npm run build

FROM nginx:stable-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
