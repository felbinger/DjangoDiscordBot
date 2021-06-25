## Development Setup
1. Create the sqlite3 database and load the fixture (default settings for the discord bot):
    ```
    python3 app/manage.py migrate
    python3 app/manage.py createsuperuser --username=user --email=
    python3 app/manage.py loaddata settings.yaml
    ```
2. Open the [Discord Developer Portal](https://discord.com/developers)
3. Create a 'New Application':  
   ![](../img/discord_new_application.png)
4. Now open the Bot settings:  
   ![](../img/discord_create_bot.png)
5. Copy your bot token and export it as `DISCORD_BOT_TOKEN` environment variable:  
   ![](../img/discord_get_bot_token.png)
6. Don't forget to enable `Privileged Gateway Intents` (right below the `Authorization Flows` in the bot settings):  
   ![](../img/discord_intents.png)
7. Add the bot to your discord server
   ![](../img/discord_oauth2.png)
8. Copy client id (environment variable `OAUTH_CLIENT_ID`) and client secret (environment variable `OAUTH_CLIENT_SECRET`)  
   ![](../img/discord_oauth2_id_and_secret.png)
9. Create a OAuth2 redirect (if you would like to deploy the bot, you need to change 127.0.0.1:8000 to the public url).
   Export the generated url (don't forget to enable identify scope) as environment variable `OAUTH_URL`.  
   ![](../img/discord_oauth2_redirect_url.png)
10. Start the application:
    ```
    gunicorn app.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --log-level DEBUG
    ```