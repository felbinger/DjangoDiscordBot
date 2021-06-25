## Productive Setup
1. Install [docker](https://docs.docker.com/engine/install/)
2. Install [docker-compose](https://docs.docker.com/compose/install/)  
3. Adjust the environment variables in [`docker-compose.yml`](./docker-compose.yml)  
   Checkout the development setup for detailed explanation on how to generate these values. 
4. Start the services 
   ```shell
   docker-compose up -d
   ```
5. Collect static files (to be served using nginx):
   ```shell
   # collect static files
   docker-compose exec -u0 django /bin/sh -c 'python manage.py collectstatic --no-input'
   ```
6. Create Superuser:
   You can make your discord user, superuser. Afterwards you can delete the created user in the django admin.
   ```shell
   # create superuser
   docker-compose exec django /bin/sh -c 'python manage.py createsuperuser --username=admin'
   ```

Afterwards you can access the application: [http://localhost:8080](http://localhost:8080)  
You can change the port inside the [`docker-compose.yml`](./docker-compose.yml#L29)
