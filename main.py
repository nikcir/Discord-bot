import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random

from discord.ui import View, Button
from discord import ButtonStyle
from discord import Embed


import jsonPython

# jsonPython.add_image("TEST_URL", 123)

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log",encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

testGeneralID = 1458489167620079699

abamiddag = 1418297877654143127

channel_ID = testGeneralID

# abacord_ID = bot.get_guild(1404930417215148032)



class GuessView(View):
    def __init__(self, options, correct_index):
        super().__init__()
        self.correct_index = correct_index #rett svar
        self.guessed_users = set()  #brukere som har gjettet
        self.options = options  # alle brukere som kan gjettes
        self.score_dict = {}


        # lager en knapp for hvert alternativ
        for idx, label in enumerate(options):
            button = Button(label=label, style=ButtonStyle.primary, custom_id=str(idx))

            #Kobler knappen til callback slik at den kan finne den
            button.callback = self.button_click
            self.add_item(button)

    async def interaction_check(self, interaction):
        # Tilatter bare gjette en gang
        if interaction.user.id in self.guessed_users:
            await interaction.response.send_message("You already guessed!", ephemeral=True)
            return False
        idx = int(interaction.data["custom_id"])
        if idx == self.correct_index:
            self.guessed_users.add(interaction.user.id)

        # self.guessed_users.add(interaction.user.id)

        return True 
        #om return True så tillater den og går videre, om false så ignorerer den
    
    async def button_click(self,interaction):
        try:
            idx = int(interaction.data["custom_id"])
            if idx == self.correct_index:
                await interaction.response.send_message(f"{interaction.user.mention} guessed correctly! \n The right answer was: {self.options[self.correct_index]}", ephemeral=True)



                # Disabler knapper etter rett gjett
                for child in self.children: #Knappene laget i innit er children
                    child.disabled = True #Endrer protertien til knappen til disabled
                await interaction.message.edit(view=self) #Discord oppdaterer knappene ved å redigere siden den ikke gjør det ved deafult
            else:
                await interaction.response.send_message("Wrong guess!", ephemeral=True) #Sender melding som bare spiller ser pga ephemeral=True

            if interaction.user.id not in self.score_dict:
                self.score_dict[interaction.user.id] = 1

            else:
                self.score_dict[interaction.user.id] += 1

            guild = interaction.guild
            
            #veldig lesbar oneliner som lager en streng med nicknames og anntall gjett som rader med \n 
            scores = "\n".join("Number of guesses: \n" + f"{(member.nick or member.name) if member else bot.get_user(uid).name}: {value}" for uid, value in self.score_dict.items() if (member := guild.get_member(uid)) or True)
            print("score", scores)
            await interaction.message.edit(content=scores, view=self)
        except Exception as e:
            print(e)


# @bot.event
# async def on_ready():
#     print(f"Sigma??? = {bot.user.name}")


@bot.event
async def on_message(message):
    #prosseserer meldingen , uten ville meldingen ha "forsvunnet" etter return
    await bot.process_commands(message)

    if message.author.bot: #ignorer egen melding
        return
    
    if message.channel.id != channel_ID: #ignoerer melding som ikke er i rett kanal
        return
    
    if not message.attachments: #ignoerer om ikke har attacthment
        return

    for attachment in message.attachments:

        if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")): #om attachtment er bilde

            # print(attachment.url,message.author.id)
            jsonPython.add_image(attachment.url,message.author.id) #kaller på fra jsonPython filen og lgger til imgurl og authorID i json filen
            await message.channel.send("lagt til!!!")
    
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready!")

    # Hent kanal
    channel = bot.get_channel(channel_ID)

    # Hent alle meldinger med attachments
    async for message in channel.history(limit=None):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):

                    existing_urls = {img['image_url'] for img in jsonPython.load_images()} #lager set med alle img urls allerede i json
                    if attachment.url not in existing_urls:
                        jsonPython.add_image(attachment.url, message.author.id) #legger til imgurl og author ID til json

    
    print("All past images added to JSON!")




@bot.command()
async def spill(ctx):
    try:
        # await ctx.send(f"yo {ctx.author.mention}")
        #velger random bilde fra json
        image = jsonPython.get_random_image()
        # Velger 3 feil users og den rette
        all_authors = set([img["author_id"] for img in jsonPython.load_images()])
        print(all_authors)
        all_authors.discard(image["author_id"])

        k = min(3, len(all_authors))

        wrong_authors = random.sample(list(all_authors), k)
        options = wrong_authors + [image["author_id"]]
        random.shuffle(options)  # tilfeldig rekkeføle på buttons
        # Gjør ID om til navn
        options_labels = [(member.nick or member.name) if (member := ctx.guild.get_member(uid)) else bot.get_user(uid).name for uid in options] #sexy oneliner som prøver å bruker nicknames og fallbacker til username
        correct_index = options.index(image["author_id"])
        print(options_labels,correct_index)
        # Lager GuessView
        guess_view = GuessView(options_labels, correct_index)

        
        
        # await ctx.send(image["image_url"], view=guess_view)

        #discord embed gjør formatering med bilder bedre
        embed = Embed(title="Guess the sender!", description="Who sent this image?")
        # embed = Embed(title="Who sent this image?", description="")
        embed.set_image(url=image["image_url"])
        # Bot sender bilde og knappene med tekst
        message = await ctx.send(embed=embed, view=guess_view)



    except Exception as e:
        print(e)
        raise





bot.run(token, log_handler=handler, log_level=logging.DEBUG)
