import discord
from discord.ext import commands
import asyncio, random, re

class interactive_dice_roller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    
    ############DICE ROLLING########

    @commands.command(aliases=["r"])
    async def roll(self, ctx):
        def check_roll_auth(m):
            return m.author == ctx.author and m.channel == ctx.channel

        dice = 0
        dice = await self.roll_get_dice(ctx, checker=check_roll_auth)
        #could be changed to a while loop to force a correct roll to occur. 
        if not dice:
            print("No dice")
            return
        side = 0
        side = await self.roll_get_sides(ctx, checker=check_roll_auth)
        if not side:
            print("No sides")
            return
        modifier = None
        modifier = await self.roll_get_modifier(ctx, checker=check_roll_auth)
        if not modifier and modifier != 0:
            print("No modifer")
            return
        list_of_rolls = []
        list_of_rolls = await self.roll_get_list_of_rolls(ctx, dice, side, checker=check_roll_auth)
        if not list_of_rolls:
            print("Not list of rolls.")
            return
        recursive = False
        recursive = await self.roll_get_recursive(ctx, checker=check_roll_auth)
        if not recursive:
            print("Not recursive")
            recursive = False
        while recursive:
            dice = await self.roll_get_dice(ctx, checker=check_roll_auth)
            if not dice:
                print("No dice")
                break
            side = await self.roll_get_sides(ctx, checker=check_roll_auth)
            if not side:
                print("No sides")
                break
            r_mod = None
            r_mod = await self.roll_get_modifier(ctx, checker=check_roll_auth)
            if not r_mod and r_mod != 0:
                print("No r_modifer")
                break
            modifier += r_mod
            r_list = []
            r_list = await self.roll_get_list_of_rolls(ctx, dice, side, checker=check_roll_auth)
            if not r_list:
                print("Not r list of rolls")
                modifier -= r_mod
                break
            list_of_rolls += r_list 
            recursive = await self.roll_get_recursive(ctx, checker=check_roll_auth)
            if not recursive:
                break
        await ctx.send('<@{0}> rolled: {1} + {2}\nFor a total of: {3}'.format(str(ctx.message.author.id), str(list_of_rolls), str(modifier), str(sum(list_of_rolls) + modifier)))
    
    async def roll_get_dice(self, ctx, checker):
        await ctx.send('How many dice do you want to roll? (Between 1 and 200)')
        try:
            answer = await self.bot.wait_for('message', check=checker, timeout=25.0)
        except asyncio.TimeoutError:
            await ctx.send('You took too long to answer.')
            return False
        answer = answer.content.replace(' ', '')
        if answer.isdecimal() and int(answer) >= 1 and int(answer) <= 200:
            dice = int(answer)
        else:
            await self.broken_roll(ctx)
            return False
        return dice

    async def roll_get_sides(self, ctx, checker):
        await ctx.send('How many sides to the dice? Max. 1000000. (F for Fate Dice)')
        try:
            answer = await self.bot.wait_for('message', check=checker, timeout=25.0)
        except asyncio.TimeoutError:
            await ctx.send('You took too long to answer.')
            return False
        answer = answer.content.replace(' ', '')
        if answer == 'F' or answer == 'f':
            side = 'f'
        elif answer.isdecimal() and int(answer) >= 2 and int(answer) <= 1000000:
            side = int(answer)
        else:
            await self.broken_roll(ctx)
            return False
        return side

    async def roll_get_modifier(self, ctx, checker):
        await ctx.send('Modifier? (0 for None)')
        try:
            answer = await self.bot.wait_for('message', check=checker, timeout=25.0)
        except asyncio.TimeoutError:
            await ctx.send('You took too long to answer.')
            return False
        answer = re.split('-', answer.content.replace(' ', ''))
        if answer[0].isdecimal():
            modifier = int(answer[0])
        elif answer[0] != '':
            try:
                modifier = int(answer[0])
            except ValueError:
                await self.broken_roll(ctx)
                return False
        elif answer[1].isdecimal():
            modifier = -int(answer[1])
        else:
            await self.broken_roll(ctx)
            return False
        return modifier

    async def roll_get_list_of_rolls(self, ctx, dice, side, checker):
        await ctx.send('Any special modifications to the roll? (No | dl NUMBER for drop lowest | dh NUMBER for drop highest | tl NUMBER for take lowest | th NUMBER for take highest)')
        try:
            answer = await self.bot.wait_for('message', check=checker, timeout=25.0)
        except asyncio.TimeoutError:
            await ctx.send('You took too long to answer.')
            return False
        answer = re.split('\s', answer.content)
        list_of_rolls = []
        while dice > 0:
            if side == 'f':
                fate_rolls = [-1,-1, 0, 0, 1, 1]
                rand = random.choice(fate_rolls)
            else:
                rand = random.randint(1, side)
            list_of_rolls.append(rand)
            dice -= 1
        if not answer[0].lower().__contains__('n'):
            if len(answer) > 1 and answer[1].isdecimal():
                answer[1] = int(answer[1])
                if answer[0] == 'dl':
                    list_of_rolls = sorted(list_of_rolls)[answer[1]:]
                elif answer[0] == 'tl':
                    list_of_rolls = sorted(list_of_rolls)[:answer[1]]
                elif answer[0] == 'th':
                    list_of_rolls = sorted(list_of_rolls)[-answer[1]:]
                elif answer[0] == 'dh':
                    list_of_rolls = sorted(list_of_rolls)[:-answer[1]]
                else:
                    await self.broken_roll(ctx)
                    return False
            else:
                await self.broken_roll(ctx)
                return False
        return list_of_rolls 

    async def roll_get_recursive(self, ctx, checker):
        await ctx.send('Would you like to add more dice to this roll?')
        try:
            answer = await self.bot.wait_for('message', check=checker, timeout=25.0)
        except asyncio.TimeoutError:
            await ctx.send('You took too long to answer.')
            return False
        answer = str(answer.content)
        if answer.lower().__contains__('y'):
            return True
        else:
            return False


    async def broken_roll(self, ctx):
        broken_text = 'Please follow the instructions.'
        await ctx.send(broken_text)

def setup(bot):
    bot.add_cog(interactive_dice_roller(bot))
        
