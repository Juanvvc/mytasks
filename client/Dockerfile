# build stage
FROM node:10.11.0-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# production stage
FROM nginx:1.14.0-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html/mytasks
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
