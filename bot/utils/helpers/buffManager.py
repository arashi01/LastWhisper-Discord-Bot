from discord import Embed, Colour
from objects.buffManager import Day, Week
from datetime import datetime

_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def buff_embed(day: Day, date: datetime) -> Embed:
    embed: Embed = Embed(title="Today's Buff Shall Be:", description=day.buff, colour=Colour.random())

    embed.set_thumbnail(url=day.image_url)
    embed.set_footer(text=date.strftime("%A %d %B %Y"))

    return embed


def week_buff_embed(week: Week, days: list[Day], date: datetime) -> Embed:
    embed: Embed = Embed(title="The buffs for the week are:", description=week.message, colour=Colour.random())
    days: dict = dict([(x.uuid, x) for x in days])

    for i in range(0, max(len(week.days), 7)):
        day: str = week.days[i]
        embed.add_field(name=_days[i], value=days[day].buff if day in days else "Missing Data")

    embed.set_footer(text=f"Week {date.isocalendar().week} of the year.")

    return embed

