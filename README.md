# 🤖 Discord Moderation Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-green.svg)](https://github.com/R4F405/Bot_Discord_Moderacion_comandos.git)

A powerful and user-friendly Discord bot designed to assist in server moderation with multiple functionalities.

## ✨ Features

### 📋 Reporting System
- Allows users to report inappropriate behavior
- Dedicated channel for report management
- Report tracking and status system
- Quick actions via reactions

### 🛡️ Moderation Commands
- Mute users
- Kick members
- Ban users
- Automatic anti-spam system
- Role and permission management

### 📊 Information Commands
- Detailed user information
- Server statistics
- Help system divided by access levels

### ❌ Prerequisites
Before you begin, ensure you have the following:

- Python 3.8 or higher installed.
- A Discord account.
- A Discord server where you have permissions to add bots.

## 🚀 Available Commands

### User Commands
```
!flex info     - Displays available commands for users
!flex report   - Reports a user for inappropriate behavior
```

### Moderator Commands
```
!flex info2      - Displays moderation commands
!flex kick       - Kicks a user
!flex ban        - Bans a user
!flex unban      - Unbans a user
!flex mute       - Mutes a user
!flex unmute     - Unmutes a user
!flex userinfo   - Displays detailed information about a user
!flex serverinfo - Displays server information
!flex reports    - Manages reports
```

## 📥 Installation

1. Clone the repository:
```bash
git clonehttps://github.com/R4F405/Bot_Discord_Moderacion_comandos.git
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

## 🔑 Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click on "New Application" and give your application a name.
3. In the side menu, select "Bot".
4. Click "Add Bot" and confirm.
5. Under the bot's name, you will find the "Reset Token" button - click it and copy the token.
6. In the "Privileged Gateway Intents" section, enable:
    - Presence Intent
    - Server Members Intent
    - Message Content Intent
7. To invite the bot to your server:
    - Go to the "OAuth2" > "URL Generator" section.
    - Select the scopes: `bot` and `applications.commands`.
    - Select the necessary permissions listed in the "🔐 Required Permissions" section.
    - Use the generated URL to invite the bot to your server.

## ⚙️ .env File Configuration

1. Modify the `.env.example` file in the project root and rename it to `.env`.
2. Add your token:
```env
DISCORD_TOKEN=your_token_here
```

3. Run the bot:
```bash
python main.py
```

## 🔧 Configuration

The bot will automatically create:
- Reports channel
- Muted role
- Moderation category

## 🛡️ Reporting System

### How to Report
1. Use the command `!flex report @user reason`.
2. The report will be sent to the moderation channel.
3. Moderators can:
    - ✅ Mark as resolved
    - ❌ Discard report
    - 🔨 Take moderation actions

### Anti-Spam
- Automatically detects spam (5 messages in 3 seconds).
- Temporarily mutes users who spam.
- Moderators are exempt from this system.

## 📝 Report Management

Moderators can view reports using:
```
!flex reports          - Displays pending reports
!flex reports resolved - Displays resolved reports
!flex reports all      - Displays all reports
```

## 🔐 Required Permissions

The bot requires the following permissions:
- Manage Messages
- Manage Roles
- Kick Members
- Ban Members
- View Channels
- Send Messages
- Manage Channels
- Add Reactions

## 🤝 Contributing

Contributions are welcome. Please:
1. Fork the project.
2. Create a branch for your feature.
3. Commit your changes.
4. Push to the branch.
5. Open a Pull Request.

## 📄 License

This project is under the MIT License - see the [LICENSE](LICENSE) file for more details.

## 🙋‍♂️ Support

If you have questions or need help:
1. Open an issue on GitHub.
2. Review the documentation.
3. Contact the maintainers.

## 🌟 Credits

Developed by R4F405

---
⭐ If you like this project, don't forget to give it a star on GitHub!
