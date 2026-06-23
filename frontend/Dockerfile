FROM node:18-alpine AS build

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY index.html .
COPY public ./public
COPY src ./src
RUN npm run build

FROM httpd:2.4
COPY apache/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY --from=build /app/dist /usr/local/apache2/htdocs/
EXPOSE 80

