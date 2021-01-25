import random
from datetime import date as date_object  # I have to do this to keep my ide from complaining.

from discord import Embed, Color

from objects import Week, Buff


def get_date_suffix(d: int) -> str:
    """
    Returns the ending of a number.

    :param d: An integer.
    :return: The suffix of the integer.
    """
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def calculate_index(date: date_object, week_length: int) -> (int, int):
    """
    Calculates the day of the week and the week number and returns them.

    :param date: A object representing the date.
    :param week_length: The number of weeks.
    :returns: A tuple of the week index and weekday number.
    """
    return date.isocalendar()[1] % week_length, date.weekday()


def get_date_buff_embed(title: str, date: date_object, buff: Buff) -> Embed:
    """
    Helper to create a buff embed.

    :param title: The title of the embed.
    :param date: The date to be used for additional calculations.
    :param buff: The buff being shown.
    :return: The resulting embed.
    """
    embed = Embed(
        title=title,
        description=str(date.strftime("%A %d" + get_date_suffix(date.day) + " %B %Y")),
        colour=get_random_color(),
    )

    embed.set_thumbnail(url=buff.image_url)
    embed.add_field(name="Buff", value=f"```ini\n{buff.name}```", inline=True)
    return embed


days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_weeks_buff_embed(week: Week, buffs: dict) -> Embed:
    """
    Helper to create a week embed.

    :param week: The week object used.
    :param buffs: A collection of all the buffs.
    :return: The resulting embed.
    """
    embed = Embed(
        title=f"{week.name} Buffs Are:",
        colour=get_random_color()
    )

    for i in range(0, 7):
        embed.add_field(name=days[i], value=f"```\n{buffs[list(buffs.keys())[week.get_value(i)]].name}```")

    return embed


def get_random_color() -> Color:
    """
    Returns a randomly generated color.

    :return: A Discord color that can be used for embeds.
    """
    return Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
