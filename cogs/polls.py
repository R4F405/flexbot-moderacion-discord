import discord
from discord.ext import commands

class Polls(commands.Cog):
    """
    Cog for creating and managing polls.
    """
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {} # Stores active polls: {message_id: {"question": "...", "options": [...], "author_id": ...}}

    @commands.command(name="createpoll")
    @commands.has_permissions(manage_messages=True) # Only users who can manage messages can create polls
    async def create_poll(self, ctx, question: str, *options: str):
        """
        Creates a new poll.
        Usage: !flex createpoll "Your question here" "Option 1" "Option 2" ... "Option N"
        Maximum of 10 options.
        """
        if not options:
            await ctx.send("Please provide at least one option for the poll.")
            return
        if len(options) > 10:
            await ctx.send("You can only have a maximum of 10 options.")
            return

        # Emojis for reactions (up to 10)
        reaction_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        description = []
        for i, option in enumerate(options):
            description.append(f"{reaction_emojis[i]} {option}")

        embed = discord.Embed(
            title=f"📊 Poll: {question}",
            description="\n".join(description),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Poll created by {ctx.author.display_name}")

        try:
            poll_message = await ctx.send(embed=embed)
            for i in range(len(options)):
                await poll_message.add_reaction(reaction_emojis[i])

            # Store the poll information
            self.active_polls[poll_message.id] = {
                "question": question,
                "options": list(options),
                "author_id": ctx.author.id,
                "channel_id": ctx.channel.id
            }
            # We could also save this to a file if persistence across bot restarts is needed.
            # For now, it's in-memory.

        except discord.Forbidden:
            await ctx.send("I don't have permissions to add reactions or send embeds here.")
        except Exception as e:
            await ctx.send(f"An error occurred while creating the poll: {e}")

    @commands.command(name="closepoll")
    @commands.has_permissions(manage_messages=True)
    async def close_poll(self, ctx, message_id: int):
        """
        Closes an active poll and shows the results.
        Usage: !flex closepoll <message_id_of_the_poll>
        """
        if message_id not in self.active_polls:
            await ctx.send("This poll is not active or does not exist. Make sure you provided the correct message ID.")
            return

        poll_data = self.active_polls[message_id]

        # Check if the command issuer is the original author of the poll or has higher permissions
        # For simplicity, we'll just check for manage_messages which is already done by the decorator.
        # A more robust check could be:
        # if ctx.author.id != poll_data["author_id"] and not ctx.author.guild_permissions.administrator:
        #     await ctx.send("You can only close polls you created, unless you are an administrator.")
        #     return

        try:
            channel = self.bot.get_channel(poll_data["channel_id"])
            if not channel:
                await ctx.send("Could not find the channel where the poll was created. It might have been deleted.")
                del self.active_polls[message_id] # Clean up
                return

            poll_message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("The poll message could not be found. It might have been deleted.")
            del self.active_polls[message_id] # Clean up
            return
        except discord.Forbidden:
            await ctx.send("I don't have permissions to fetch messages in the poll channel.")
            return
        except Exception as e:
            await ctx.send(f"An error occurred while fetching the poll message: {e}")
            return

        reaction_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        results = []
        total_votes = 0

        for i, option_text in enumerate(poll_data["options"]):
            # Find the reaction corresponding to the option
            reaction = discord.utils.get(poll_message.reactions, emoji=reaction_emojis[i])
            vote_count = reaction.count - 1 if reaction else 0 # -1 to exclude the bot's own reaction
            results.append((option_text, vote_count))
            total_votes += vote_count

        # Sort results by vote count in descending order
        results.sort(key=lambda x: x[1], reverse=True)

        result_description = [f"**Question: {poll_data['question']}**\n"]
        if total_votes == 0:
            result_description.append("No votes were cast.")
        else:
            for option_text, vote_count in results:
                percentage = (vote_count / total_votes) * 100 if total_votes > 0 else 0
                result_description.append(f"- **{option_text}**: {vote_count} vote(s) ({percentage:.1f}%)")

        result_description.append(f"\nTotal Votes: {total_votes}")

        embed = discord.Embed(
            title="📊 Poll Closed - Results",
            description="\n".join(result_description),
            color=discord.Color.dark_gold()
        )
        original_author = await self.bot.fetch_user(poll_data["author_id"])
        embed.set_footer(text=f"Poll originally created by {original_author.name if original_author else 'Unknown User'}. Closed by {ctx.author.display_name}.")

        await ctx.send(embed=embed)

        # Remove the poll from active polls
        del self.active_polls[message_id]

        try:
            await poll_message.edit(embed=embed) # Update the original poll message with results
            await poll_message.clear_reactions() # Remove reactions from the original message
        except discord.Forbidden:
            await ctx.send("Note: I couldn't update the original poll message or clear its reactions due to missing permissions.")
        except discord.NotFound:
            pass # Message was already deleted, or we couldn't find it.
        except Exception as e:
            print(f"Error updating original poll message: {e}")


async def setup(bot):
    """Sets up the Polls cog."""
    await bot.add_cog(Polls(bot))
