# discord webhook template

from discord_webhook import DiscordWebhook

webhook = DiscordWebhook(
    "https://discord.com/api/webhooks/1125887774105546784/STe-n0tBjYLvXaZW9RjIGgxj6R91IOwrmr3pZgBNg-XWGgDFqh2CMBbZNKODoxb6Gnwz",
    embeds=[
    {
      "author": {
        "name": "AC"
      },
      "title": "FLIP FOUND",
      "url": "https://producturl.com",
      "color": 15258703,
      "fields": [
        {
          "name": "Price",
          "value": "product price",
          "inline": True
        },
        {
          "name": "Last sale on StockX",
          "value": "sale £",
          "inline": True
        },
        {
          "name": "Date of sale:",
          "value": "date",
        }
      ]
    }
  ]).execute()
