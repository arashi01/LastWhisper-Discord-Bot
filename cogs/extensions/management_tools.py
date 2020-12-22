from discord.ext import commands

import utils
from objects import ManagementToolsConfig
from configuration import ConfigurationDictionary, Configuration
from utils.cog_class import CogClass


class ManagementTools(CogClass, name=utils.CogNames.ManagementTools.value):
    def __init__(self, client: commands.bot):
        super().__init__(client, "./config/management_tools", ManagementToolsConfig)

    @commands.command()
    async def clear(self, ctx: commands.Context, number: str = "3"):
        guild: ManagementToolsConfig = self.guildDict[ctx.guild.id]

        if guild.clear_channel_id_blacklist.__contains__(ctx.channel.id):
            await ctx.send("Sorry this channel has been blacklisted from this command.", delete_after=5)
            return

        if str.isnumeric(number):
            if int(number) == 0:
                await ctx.send("Really... what were you expecting to be cleared with 0.", delete_after=5)
            else:
                await ctx.channel.purge(limit=int(number))
        elif str(number).lower() == "all":
            await ctx.channel.purge(limit=len(await ctx.channel.history(limit=None).flatten()))
        else:
            await ctx.send(f"Cannot remove {number} as it is not a valid command.", delete_after=5)

        await ctx.send("Finished clearing.", delete_after=5)

    @property
    def get_configs(self) -> ConfigurationDictionary:
        config: ConfigurationDictionary = ConfigurationDictionary()

        config.add_configuration(Configuration("clear_allowed_role_ids", "clear_allowed_role_ids", add=self.add, remove=self.remove))
        config.add_configuration(Configuration("clear_channel_id_blacklist", "clear_channel_id_blacklist", add=self.add, remove=self.remove))

        return config

    @property
    def get_function_roles_reference(self) -> dict:
        return {
            self.clear.name: None
        }


def setup(client: commands.bot):
    client.add_cog(ManagementTools(client))
