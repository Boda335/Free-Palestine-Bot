# Free Palestine Bot

Free Palestine Bot is a multifunctional Discord bot designed to enhance your server with various features, including sending daily reminders, changing role colors, and updating the status of specified bots. This bot also allows users to frame their avatars with pre-defined images.

## Features

- **Daily Reminders**: Sends a daily message to a specific channel.
- **Role Color Changing**: Automatically changes the color of specified roles every 5 minutes.
- **Bot Status Updates**: Monitors and updates the status of specified bots in a dedicated channel.
- **Avatar Framing**: Allows users to frame their avatars with different images.
- **Auto Image Posting**: Posts an image to specific channels automatically.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/free-palestine-bot.git
    cd free-palestine-bot
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Setup configuration files**:
    - Create a `config.json` file with the following structure:
      ```json
      {
      "FRAME_URLS": [
        "https://e.top4top.io/p_3102rocca0.png",
        "https://a.top4top.io/p_3102gyw921.png",
        "https://l.top4top.io/p_3102sd2h20.png",
        "https://g.top4top.io/p_3102qq8yp2.png",
        "https://h.top4top.io/p_3102nejqm3.png"
        //you can add more
       ],
      "color_role_ids": [
      "ROLE_ID 1",
      "ROLE_ID 2",
      "ROLE_ID 3"
      //you can add more
      ],
      "BOT_IDS": [
      BOT_IDS 1,
      BOT_IDS 2 ,
      BOT_IDS 3
      //you can add more
      ],
      "UPDATE_CHANNEL_ID": UPDATE_CHANNEL_ID,
      "Ziker_ROLE_ID" : Ziker_ROLE_ID,
      "Ziker_channel_ID" : Ziker_channel_ID,
      "token":"token",
      "imageUrl": "auto_line_url"
      }
      ```

    - Create a `channels.json` file with an empty list:
      ```json
      []
      ```

## Usage

1. **Run the bot**:
    ```sh
    python bot.py
    ```

2. **Bot Commands**:
    - `!setbtn`: Sends an embed with buttons to frame user avatars.
    - `!line`: Toggles automatic image posting in the current channel (requires admin permissions).
    - `!stu`: Manually updates the bot status message in the current channel.

## Bot Permissions

Ensure the bot has the following permissions in your Discord server:
- Read Messages
- Send Messages
- Embed Links
- Attach Files
- Manage Roles

## Contributing

Feel free to open issues or submit pull requests if you have any suggestions or improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [discord.py](https://github.com/Rapptz/discord.py)
- [Pillow](https://python-pillow.org/)
