FROM node:22-alpine 

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN yarn install

# Copy the application code
COPY . .

EXPOSE 3000

CMD ["yarn", "run", "start"]
