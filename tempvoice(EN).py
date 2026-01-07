import discord
from discord.ext import commands
from discord.ui import View, Modal, TextInput, Select, UserSelect
import asyncio

# ================= CONFIG =================

INVITE_LINK = "INVITE_LINK_HERE"
THUMBNAIL_URL = "THUMBNAIL_IMAGE_URL_HERE"

ALLOWED_GUILD_ID = 000000000000000000  # Replace with your guild ID
SETUP_ROLE_ID = 000000000000000  # Replace with your setup role ID

# =====================================================
# MODALS
# =====================================================

class LimitModal(Modal, title="Set User Limit"):
    limit = TextInput(label="New limit (0–99)", max_length=2)

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction):
        try:
            value = int(self.limit.value)
            if 0 <= value <= 99:
                await self.channel.edit(user_limit=value)
                await interaction.response.send_message(
                    f"✅ Limit set to `{value}`.",
                    ephemeral=True
                )
            else:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid number.",
                ephemeral=True
            )


class RenameModal(Modal, title="Rename Voice Channel"):
    name = TextInput(
        label="New name",
        max_length=32,
        placeholder="e.g. Chill Room"
    )

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction):
        await self.channel.edit(name=self.name.value)
        await interaction.response.send_message(
            f"✏️ Channel renamed to **{self.name.value}**",
            ephemeral=True
        )

# =====================================================
# DROPDOWNS
# =====================================================

class DisconnectSelect(Select):
    def __init__(self, members):
        super().__init__(
            placeholder="Select a user",
            options=[
                discord.SelectOption(label=m.display_name, value=str(m.id))
                for m in members
            ]
        )

    async def callback(self, interaction):
        member = interaction.guild.get_member(int(self.values[0]))
        if member:
            await member.move_to(None)
        await interaction.response.send_message("🔌 User disconnected.", ephemeral=True)

class DisconnectView(View):
    def __init__(self, members):
        super().__init__(timeout=30)
        self.add_item(DisconnectSelect(members))


class DragSelect(UserSelect):
    def __init__(self, channel):
        super().__init__(placeholder="Search & move a user")
        self.channel = channel

    async def callback(self, interaction):
        user = self.values[0]
        if user.voice:
            try:
                await user.move_to(self.channel)
            except:
                pass
        await interaction.response.send_message("➡️ Action completed.", ephemeral=True)

class DragView(View):
    def __init__(self, channel):
        super().__init__(timeout=30)
        self.add_item(DragSelect(channel))


class BlockSelect(UserSelect):
    def __init__(self, channel):
        super().__init__(placeholder="Block a user")
        self.channel = channel

    async def callback(self, interaction):
        user = self.values[0]
        await self.channel.set_permissions(user, connect=False)
        await interaction.response.send_message(
            f"🚫 `{user.display_name}` blocked.",
            ephemeral=True
        )

class BlockView(View):
    def __init__(self, channel):
        super().__init__(timeout=30)
        self.add_item(BlockSelect(channel))

# =====================================================
# TEMPVOICE COG
# =====================================================

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_channels: dict[int, int] = {}
        asyncio.create_task(self.cleanup_loop())

    async def cleanup_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for cid in list(self.voice_channels):
                ch = self.bot.get_channel(cid)
                if ch and len(ch.members) == 0:
                    try:
                        await ch.delete()
                    except:
                        pass
                    self.voice_channels.pop(cid, None)
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != ALLOWED_GUILD_ID:
            return

        category = discord.utils.get(
            member.guild.categories, name="Private Channels"
        )
        if not category:
            category = await member.guild.create_category("Private Channels")

        if after.channel and after.channel.name == "Join to Create":
            vc = await member.guild.create_voice_channel(
                f"{member.name}'s Channel",
                category=category
            )
            self.voice_channels[vc.id] = member.id
            await member.move_to(vc)

        if before.channel and before.channel.id in self.voice_channels:
            if len(before.channel.members) == 0:
                await before.channel.delete()
                self.voice_channels.pop(before.channel.id, None)

    # =================================================
    # SETUP COMMAND
    # =================================================

    @commands.command()
    async def setup_tempvoice(self, ctx):
        if ctx.guild.id != ALLOWED_GUILD_ID:
            return await ctx.send("❌ Unauthorized server.")

        if not any(r.id == SETUP_ROLE_ID for r in ctx.author.roles):
            return await ctx.send("❌ No permission.")

        guild = ctx.guild

        category = discord.utils.get(guild.categories, name="Private Channels")
        if not category:
            category = await guild.create_category("Private Channels")

        if not discord.utils.get(guild.voice_channels, name="Join to Create"):
            await guild.create_voice_channel("Join to Create", category=category)

        text = discord.utils.get(guild.text_channels, name="voice-control")
        if not text:
            text = await guild.create_text_channel("voice-control")

        embed = discord.Embed(
            title="TempVoice Interface",
            description=(
                "Control your **voice channel** using the buttons below:\n\n"

                "<:claim:1455945955697496095> — [`Claim`](" + INVITE_LINK + ") the voice channel\n"
                "<:lock:1455946053663850536> — [`Lock`](" + INVITE_LINK + ") the voice channel\n"
                "<:unlock:1455946041059836048> — [`Unlock`](" + INVITE_LINK + ") the voice channel\n"
                "<:ghost:1455946028875383035> — [`Ghost`](" + INVITE_LINK + ") the voice channel\n"
                "<:reveal:1455946017102106662> — [`Reveal`](" + INVITE_LINK + ") the voice channel\n"
                "<:disconnect:1455946001633513482> — [`Disconnect`](" + INVITE_LINK + ") a user\n"
                "<:drag:1455954907793326203> — [`Drag`](" + INVITE_LINK + ") move a user into your channel\n"
                "<:block:1455952452628123738> — [`Block`](" + INVITE_LINK + ") prevent a user from joining\n"
                "<:limit_up:1455945977511940161> — [`Limit`](" + INVITE_LINK + ") set user limit\n"
                "<:rename:1456051294560321810> — [`Rename`](" + INVITE_LINK + ") rename the voice channel"
            ),
            color=discord.Color.from_rgb(255, 255, 255)
        )

        embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text="TempVoice System • jobcenter")

        await text.send(embed=embed, view=VoiceChannelView(self.bot))
        await ctx.send("✅ TempVoice setup completed.")

# =====================================================
# BUTTON VIEW
# =====================================================

class VoiceChannelView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    def get_channel(self, user):
        cog = self.bot.get_cog("TempVoice")
        for cid, uid in cog.voice_channels.items():
            if uid == user.id:
                return self.bot.get_channel(cid)
        return None

    async def no_channel(self, interaction):
        await interaction.response.send_message(
            "❌ You do not own a private voice channel.",
            ephemeral=True
        )

    @discord.ui.button(emoji="<:claim:1455945955697496095>", style=discord.ButtonStyle.secondary)
    async def claim(self, interaction, _):
        cog = self.bot.get_cog("TempVoice")
        if interaction.user.voice:
            ch = interaction.user.voice.channel
            owner = cog.voice_channels.get(ch.id)
            if owner not in [m.id for m in ch.members]:
                cog.voice_channels[ch.id] = interaction.user.id
                return await interaction.response.send_message("👑 Channel claimed.", ephemeral=True)
        await interaction.response.send_message("❌ Channel cannot be claimed.", ephemeral=True)

    @discord.ui.button(emoji="<:drag:1455954907793326203>", style=discord.ButtonStyle.secondary)
    async def drag(self, interaction, _):
        ch = self.get_channel(interaction.user)
        if not ch:
            return await self.no_channel(interaction)
        await interaction.response.send_message(
            "Select a user:",
            view=DragView(ch),
            ephemeral=True
        )

    @discord.ui.button(emoji="<:block:1455952452628123738>", style=discord.ButtonStyle.secondary)
    async def block(self, interaction, _):
        ch = self.get_channel(interaction.user)
        if not ch:
            return await self.no_channel(interaction)
        await interaction.response.send_message(
            "Block a user:",
            view=BlockView(ch),
            ephemeral=True
        )

    @discord.ui.button(emoji="<:lock:1455946053663850536>", style=discord.ButtonStyle.secondary)
    async def lock(self, interaction, _):
        ch = self.get_channel(interaction.user)
        if not ch:
            return await self.no_channel(interaction)
        await ch.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("🔒 Locked.", ephemeral=True)

    @discord.ui.button(emoji="<:unlock:1455946041059836048>", style=discord.ButtonStyle.secondary)
    async def unlock(self, interaction, _):
        ch = self.get_channel(interaction.user)
        if not ch:
            return await self.no_channel(interaction)
        await ch.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message("🔓 Unlocked.", ephemeral=True)

    @discord.ui.button(emoji="<:ghost:1455946028875383035>", style=discord.ButtonStyle.secondary)
    async def ghost(self, interaction, _):
        ch = self.get_channel(interaction.user)
        if not ch:
            return await self.no_channel(interaction)
        await ch.set_permissions(interaction.guild.default_role, view_channel=False)
        await interaction.response.send_message("👻 Hidden.", ephemeral=True)

    @discord.ui.button(emoji="<:reveal:1455946017102106662>", style=discord.ButtonStyle.secondary)
    async def reveal(self, interaction, _):
        ch = self.get_channel(interaction.user)
        if not ch:
            return await self.no_channel(interaction)
        await ch.set_permissions(interaction.guild.default_role, view_channel=True)
        await interaction.response.send_message("👁 Visible.", ephemeral=True)

    @discord.ui.button(emoji="<:disconnect:1455946001633513482>", style=discord.ButtonStyle.secondary)
    async def disconnect(self, interaction, _):
        ch = self.get_channel(interaction.user)
        if not ch:
            return await self.no_channel(interaction)
        members = [m for m in ch.members if not m.bot]
        await interaction.response.send_message(
            "Select a user:",
            view=DisconnectView(members),
            ephemeral=True
        )

    @discord.ui.button(emoji="<:limit_up:1455945977511940161>", style=discord.ButtonStyle.secondary)
    async def limit(self, interaction, _):
        ch = self.get_channel(interaction.user)
        if not ch:
            return await self.no_channel(interaction)
        await interaction.response.send_modal(LimitModal(ch))

    @discord.ui.button(emoji="<:rename:1456051294560321810>", style=discord.ButtonStyle.secondary)
    async def rename(self, interaction, _):
        ch = self.get_channel(interaction.user)
        if not ch:
            return await self.no_channel(interaction)
        await interaction.response.send_modal(RenameModal(ch))

# =====================================================
# SETUP
# =====================================================

async def setup(bot):
    await bot.add_cog(TempVoice(bot))
