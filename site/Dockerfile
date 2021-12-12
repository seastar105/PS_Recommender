FROM node:12

WORKDIR /app

COPY package*.json ./

RUN npm install -g live-server

COPY . .

CMD ["live-server", "--host=0.0.0.0"]