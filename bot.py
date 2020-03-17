import discord
import time
import glob
import os


#######################
#configuration details#
#######################

#discord bot token
TOKEN = ''

#production discord channel id
channel_id = ''




client = discord.Client()


@client.event
async def alert_discord(subdomain, service):

  channel = client.get_channel(int(channel_id))

  embed = discord.Embed()
  embed.set_author(name=str(subdomain), icon_url="http://www.pngmart.com/files/8/Exclamation-Mark-Transparent-PNG.png")
  embed.add_field(name="Service:", value=str(service), inline=True)
  await channel.send(embed=embed)


@client.event
async def on_ready():
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')



  old_contents = glob.glob("zoinks/*")

  while True:
    new_contents = glob.glob("zoinks/*")


    #get new files
    if new_contents != old_contents:
      new_files = list(set(new_contents) - set(old_contents))

      #parse new files
      for file in new_files:
        subdomain = os.path.basename(file)
        for line in open('zoinks/' + subdomain, 'r').readlines(): service = line.rstrip('\n')

        #post to server
        await alert_discord(subdomain, service)
        old_contents = new_contents
    

    time.sleep(5)

client.run(TOKEN)