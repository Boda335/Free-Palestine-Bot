# Free-Palestine-Bot
Free Palestine Bot is a multifunctional Discord bot designed to enhance your server with various features, including sending daily reminders, changing role colors, and updating the status of specified bots. This bot also allows users to frame their avatars with pre-defined images.

# Features
  - Daily Reminders: Sends a daily message to a specific channel.
  - Role Color Changing: Automatically changes the color of specified roles every 5 minutes.
  - Bot Status Updates: Monitors and updates the status of specified bots in a dedicated channel.
  - Avatar Framing: Allows users to frame their avatars with different images.
  - Auto Image Posting: Posts an image to specific channels automatically.

# Installation

`git clone https://github.com/Boda335/Free-Palestine-Bot.git`\n\n
`cd free-palestine-bot`

# Install dependencies: 
`pip install -r requirements.txt`

# Setup configuration files:
`
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
`
