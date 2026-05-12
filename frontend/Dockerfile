FROM node:22-alpine 

WORKDIR /app
RUN chown node:node /app

USER node

# Copy package files
COPY --chown=node:node package*.json ./

# Install dependencies
RUN yarn install

# Copy the application code
COPY --chown=node:node . .

EXPOSE 3000

CMD ["yarn", "run", "start"]
