import discord
import asyncio
import random
from discord.ext import commands


class Moderation(commands.Cog):
    """Commands to help you better manage your server"""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation module is ready')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member from the server"""
        await member.kick(reason=reason)
        await ctx.send(f"<a:a_check:742966013930373151> Successfully kicked ``{member}``")
        await member.send(f"You have been kicked from **{ctx.guild.name}** for the following reason:"
                          f"\n```py\n{reason}```")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member from the server"""
        await member.ban(reason=reason)
        await ctx.send(f"<a:a_check:742966013930373151> Successfully banned ``{member}``")
        await member.send(f"You have been banned from **{ctx.guild.name}** for the following reason:"
                          f"\n```py\n{reason}```")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """Unban a member"""
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"<a:a_check:742966013930373151> Successfully unbanned ``{user}``")
                await user.send(f'<a:a_check:742966013930373151> You have been unbanned from **{ctx.guild.name}**')
                return

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 5):
        """Purge any amount of messages with a default of 5"""
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'<a:a_check:742966013930373151>  ``{amount}`` messages have been cleared',
                       delete_after=3.0)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 10):
        """Set the slowmode for a channel"""
        if 0 < seconds < 21601:
            await ctx.channel.edit(slowmode_delay=seconds)
            return await ctx.send(f"<a:a_check:742966013930373151> "
                                  f"Slowmode for <#{ctx.channel.id}> has been set to ``{seconds}`` seconds."
                                  f"\nDo ``n.slowmode 0`` to remove slowmode!")
        if seconds == 0:
            await ctx.channel.edit(slowmode_delay=0)
            return await ctx.send(f"<a:a_check:742966013930373151> "
                                  f"Slowmode for <#{ctx.channel.id}> has been removed.")
        if seconds > 21600:
            return await ctx.send(f"<:redx:732660210132451369> That is not a valid option for slowmode. Please choose a"
                                  f"number between ``0`` and ``21,600`` to enable slowmode.")

    @commands.command(aliases=['suggest', 'vote'])
    async def poll(self, ctx, *, msg):
        """Use NOVA to hold an organized vote"""
        embed = discord.Embed(title=f'New Poll', color=0x5643fd, description=msg, timestamp=ctx.message.created_at)
        embed.set_thumbnail(url='https://imgur.com/ES5SD0L.png')
        embed.set_footer(icon_url=ctx.message.author.avatar_url, text=ctx.message.author)
        message = await ctx.send(embed=embed)
        for i in ["⬆️", "⬇️"]:
            await message.add_reaction(i)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True)
    async def mute(self, ctx, user: discord.Member = None, *, reason):
        guild = ctx.guild
        muted = await ctx.guild.create_role(name="Muted", reason="To use for muting")
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        mute = discord.utils.get(ctx.guild.text_channels,
                                 name="muted")
        if not role:
            try:
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted, send_messages=False,
                                                  read_message_history=False,
                                                  read_messages=False)
            except discord.Forbidden:
                return await ctx.send("<:redx:732660210132451369> I have no permissions to make a muted role")
            await user.remove_roles(atomic=True)
            await user.add_roles(muted)
            await ctx.send(f"<a:a_check:742966013930373151> {user.mention} has been sent to #muted for ``{reason}``")
        else:
            await user.add_roles(role)
            await ctx.send(f"<a:a_check:742966013930373151> {user.mention} has been sent to #muted for ``{reason}``")

        if not mute:
            overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_message_history=False),
                          ctx.guild.me: discord.PermissionOverwrite(send_messages=True),
                          muted: discord.PermissionOverwrite(read_message_history=True)}
            try:
                channel = await guild.create_text_channel('muted', overwrites=overwrites)
                await channel.send(
                    f"Welcome to #muted... You will spend your time here until you get unmuted. "
                    f"Enjoy the silence.")
            except discord.Forbidden:
                return await ctx.send("<:redx:732660210132451369> I have no permissions to make #muted")

    @commands.group(invoke_without_command=True, aliases=['config'])
    async def configure(self, ctx):
        """Configure your server to use some of NOVA's more complex moderation features."""
        embed = discord.Embed(color=0x5643fd, title='🛠️ Configuration Options 🛠️', timestamp=ctx.message.created_at)
        embed.add_field(name='``n.configure mute``', value='Adds a #muted channel and a muted role to your '
                                                           'server. Do n.mute [member] [reason] in order to mute '
                                                           'someone and remove '
                                                           'their permissions to send messages.', inline=False)
        embed.add_field(name='``n.configure modmail``', value='Adds a #modmail channel and allows users to '
                                                              'have interactions with the server staff in a private '
                                                              'area.',
                        inline=False)
        embed.set_thumbnail(url='https://imgur.com/uMhz173.png')
        await ctx.send(embed=embed)

    @configure.command()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def modmail(self, ctx):
        """Use this command to set up modmail for your server."""
        await ctx.send('Work in progress, stay tuned.')

    @configure.command()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True)
    async def mute(self, ctx):
        """Use this command to set up the mute command for your server."""
        await ctx.send('Work in progress, stay tuned.')


def setup(client):
    client.add_cog(Moderation(client))
