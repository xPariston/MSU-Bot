from discord.ext.commands import Bot
import discord
import random
import asyncio
import datetime
import os
import rrDamage

BOT_PREFIX = ("!")

client = Bot(command_prefix=BOT_PREFIX)

profildict={}


async def getPartys():
    parteienchannel = discord.Object(id='504982742707077120')
    parteiliste = []
    async for m in client.logs_from(parteienchannel, 100):
        p = m.content.strip()
        parteiliste.append(p)
    return parteiliste



@client.command(name="WarListPartyAnalyse",
                description='Analysiere Kriege aus Datenbank auf Teilnahme unserer Parteien.',
                brief='Kriegsanalyse von allen Kriegen',
                pass_context=True)

async def WarListPartyAnalyse(context):
    parteiliste = await getPartys()

    warchannel = discord.Object(id='505500419221618729')
    warliste = []
    async for n in client.logs_from(warchannel, 100):
        warliste.append(n.content)

    GesamtDamage,partydictRawDmg,partydictPerDmg = await rrDamage.MultiWar(warliste,parteiliste)

    #for x in partydictRawDmg:
    #    if partydictRawDmg[x] > 100000000:
    #        await client.say(x + ": " + rrDamage.MakeNumber2PrettyString(partydictRawDmg[x]) + "\n")
    Msg1= "Gesamtschaden der Partei(en): " + rrDamage.MakeNumber2PrettyString(GesamtDamage) + "\n\n"
    Msg2= "Roher Schaden der Parteien:\n"
    for j in partydictRawDmg:
        Msg2 += j + ": " + rrDamage.MakeNumber2PrettyString(partydictRawDmg[j])+ '\n'
    await client.say(Msg1 + Msg2)

@client.command(name="WarListPlayerAnalyse",
                description='Analysiere Kriege aus Datenbank auf Teilnahme unserer Parteien.',
                brief='Kriegsanalyse von allen Kriegen',
                pass_context=True)

async def WarListPlayerAnalyse(context):
    parteiliste = await getPartys()

    warchannel = discord.Object(id='505500419221618729')
    warliste = []
    async for n in client.logs_from(warchannel, 100):
        warliste.append(n.content)

    urlplayer = {}
    spielerdict,urlplayer = await rrDamage.MultiplayerDmg(warliste,profildict,parteiliste,urlplayer)

    # Msg2= "Roher Schaden der Spieler:\n"
    # for j in spielerdict:
    #     Msg2 += j + ": " + rrDamage.MakeNumber2PrettyString(spielerdict[j])+ '\n' + "SpielerURL: " + urlplayer[j] + '\n\n'
    # await client.say(Msg2)

    Msg3 = "\n \n Spieler:\n"
    for j in spielerdict:
        name= j.replace("[MSU]","")
        name = name.strip()
        Msg3 += name +"\n"
    Msg3 = Msg3 + "\n"+"Schaden:\n"
    for j in spielerdict:
        Msg3 += rrDamage.MakeNumber2PrettyString(spielerdict[j])+"\n"
    Msg3 = Msg3 + "\n"+"URL:\n"
    for j in spielerdict:
        Msg3 += urlplayer[j]+"\n"

    await client.say(Msg3)

@client.command(name="AllDonations",
                description='Analysiere alle Spenden in unseren Regionen in den letzten Tagen.',
                brief='Spendenanalyse aller Regionen in den letzten Tagen',
                pass_context=True)


async def AllDonations(context):
    author = context.message.author

    days = context.message.content
    days = days.replace("!AllDonations","")
    days = days.strip()
    days = int(days)
    parteiliste = await getPartys()

    stateschannel = discord.Object(id='504982760251850752')
    stateids = []
    async for n in client.logs_from(stateschannel, 100):
        n=n.content
        n=n.split(":")
        n=n[1].strip()
        stateids.append(n)

    partydon={}
    counter=1
    Gesamtspendenvolumen=0

    marktdict = await rrDamage.getMarktPreise()
    await client.say("Starte Analyse")
    for state in stateids:
        await client.say("Analysiere Staat %d"%counter)
        print("Staat Nr.%d: " %counter + state)
        tempdict = await rrDamage.getStateDonations(state,parteiliste,profildict,marktdict,days)
        print("Staat beendet")
        counter +=1
        for p in tempdict:
            Gesamtspendenvolumen= Gesamtspendenvolumen + tempdict[p]
            if p in partydon:
                partydon[p] = partydon[p] + tempdict[p]
            else:
                partydon[p] = tempdict[p]
    await client.say("Analyse abgeschlossen")
    print("Alle Staaten beendet")
    partydonPro={}

    Msg1 = "Gesamtspenden der Staaten während der letzten 21 Tage: " + rrDamage.MakeNumber2PrettyString(Gesamtspendenvolumen) + "\n\n"
    Msg2 = "Spendenvolumen der Parteien:\n"
    for j in partydon:
        Msg2 += j + ": " + rrDamage.MakeNumber2PrettyString(partydon[j]) + '\n'

    await asyncio.shield(client.send_message(context.message.channel, Msg1 + Msg2))


async def update_markt_background_task():
    await client.wait_until_ready()
    while not client.is_closed:
        Preise = await rrDamage.getMarktPreise()
        preischannel = discord.Object(id="504982618631045132")
        if "Öl" in Preise:
            await client.send_message(preischannel, "Routinecheck geschafft.")
        else:
            await client.send_message(preischannel, "@Admin#9464 pls fix me senpai")
        await asyncio.sleep(86400)

@client.event
async def on_member_join(member):
    server = member.server
    fmt = 'Willkommen {0.mention} auf dem Server des Staatenbundes! Um verifiziert zu werden poste bitte ein Screenshot deines RR Profils. Akzeptiert werden alle Bürger des Staatenbundes. Eines unserer Teammitglieder wird sich dann die Daten genauer prüfen und dich bei erfolgreicher Prüfung auf dem Server verifizieren.'
    await client.send_message(client.get_channel('496286798624849923'), fmt.format(member, server))

@client.command(name='Jukebox',
                description="Best of Pariston Songs",
                brief='Lass mich zu Pariston singen.',
                aliases=['Musik','Music','Song'],
                pass_context=True)



async def Jukebox(context):
    possible_responses = [
        'Julie - Der perfekte Zeuge: Das ist der perfekte Zeuge, das ist der perfekte Mann, lass dich einfach von ihm missionieren, schon bist du in Paristons Bann.',
        'Haftbefehl - Zeugen wissen wer die Gottheit ist: Zeugen wissen, wer die Gottheit ist, Gotti Pari ist der, der in Sänfte und im Himmel sitzt, Mosambik Gold Rich, Wissen, wer Safari ritzt.',
        'Scorpions - Wind of Pariston: Take me to the only true belief, in the whole world, where the zeugen of tomorrow pray ahead, in the wind of Pariston.',
        'Frei Wild - Land der Paristoten: Das ist das Land der Paristoten, die denken Gottes Plan hat noch viel parat, wir sind reine Glaubensbrüder und keine Kurasisten, wir kenn einfach den echten Weg, Parsem.',
        'Sportfreunde Stiller - Parsem Parsem: Parsem Parsem, auf deinen Glauben, er stieg hinauf, und er wacht, Parsem Parsem, Für seine Art mich zu missionieren, Hör niemals damit auf! Pariston mein Herr, hör bitte niemals damit auf.',
        'Feine Sahne Fischfilet - Ich bin komplett im Bann: Ich bin komplett im Bann, Pariston wacht über mich, Ich bin komplett im Bann, Er hat ein Plan wie es weiter geht. Ich bin komplett im Bann. Noch mehr Zeugen wünsch ich mir, Ich bin komplett im Bann, will sofort alle missionieren.',
        'Cro - Meinen Bann: Alles was ich brauch ist meinen Bann, meinen Bann, denn keiner kennt mich so wie Pariston, Pariston, Wirf deine Blicke ind die Luft! (Pahar sem Pahar sem) Bin schon lange Zeuge und hoffe du auch, auch, auch!',
        'Trailerpark - Beten kannst du überall: Junge, du sitzt immer nur zu Hause vorm Pc, Geh doch auch mal raus für Gebete. (okay) Beten kannst du überall! Morgens beim Warten im Bus, andere liegen beim heiligen Gruß NO PRAY NO LIFE!',
        'Rammstein - Käse: Eins, hier kommt der Käse. Zwei, hier kommt der Käse. Drei, Er ist der klebrigste Käse von allen. Vier, hier kommt der Käse.'
        'Helene Fischer - Pariston auch in der Nacht: Pariston auch in der Nacht, der Erlöser über uns wacht, Pariston unser Haus, Seine Famile nimmt dich auf, Pariston auch in der Nacht, spüre was sein Wort mit dir macht.',
        'Alligatoah - Willst du?: Willst du mit mir Klinken putzen? Dann wird uns Pariston beschützen. Missionieren ist unser größter Nutzen. Willst du mit mir Klinken putzen?',
        'Kraftklub - Songs an Pariston: Wenn du betest, sreibt Dean wieder Songs an Pariston. Wenn du betest! Wenn du betest, komm unsere Freunde zurück aus TSE. Wenn du betest! Wenn du betest, dann allein oder wollen wir beide? Wenn du betest!',
        'The Cranberries - Pariston: With their love and their prays, and their prays and their words, in your head in your head he`s seeing youuuu. In your heaaaaad, in your hee heeaadd, Pariston, Pariston, Pariston, ton, ton. He`s in your heaaaad, in your heee heeead! Pariston, Pariston, Pariston, ton, ton, ton oh Par Par Par Par Par Paaaar.',
        'Rabauken - Was wollen wir beten?: Was wollen wir beten, für Pariston man, was wollen wir beten, unser Gott!',
        'Comedian Harmonists - Mein kleiner frommer Zeuge: Ein kleiner frommer Zeuge, steht draußen vor der Tür, Holari, holari, holaro! Was wird er mir wohl sagen? Was bin ich schon nervös. Holari, Holari, Holaro! Nun öffne ich dir Klink, steht Paristons gutes Kind, holt einmal ganz tief Luft, und er spricht, spricht, spricht. Ein kleiner frommer Zeuge, steht draußen vor der Tür, Holari, holari, hollaro!',
        'Lynard Skynard - Sweet Home bei den Zeugen: Big wheels keep on turning. Carry me home to see my Pariston. Singing songs about the Zeugen. I miss Pariston once again. And I think its a sin, yes. Well I heard the Zeugen sing about him Well, I heard ol` Nico put him up Well, I hope every Zeuge will remember A Zeugen-man always needs him around, anyhow. Sweet home bei den Zeugen. Where the skies are so blue. Sweet Home bei den Zeugen. Pariston, I`m coming home to you!',
        'Fürstenfeld - S.T.S.: I brauch kan Gürtel i brauch kan Ring, I will z`ruck hintern Pariston. I brauch nur des bissl Göid Für die Fahrt zu Pariston. I will wieder ham, fühl mi do so allan. I brauch ka grosse Welt, i will ham zu Pariston. I will wieder ham, fühl mi do so allan. I brauch ka grosse Welt, i will ham zu Pariston.'
        ' Laudato si, o-mi Pariston. Laudato si, o-mi Pariston. Laudato si, o-mi Pariston. Laudato si, o-mi Pariston. Sei gepriesen, du hast die Welt erschaffen. Sei gepriesen, für Sonne, Mond und Sterne. Sei gepriesen, für Meer und Kontinente. Sei gepriesen, denn du bist wunderbar, Herr!'

    
    ]
    await client.say(random.choice(possible_responses))

@client.command(name='Huldigung',
                description="Konversation über den Kult führen.",
                brief='Lass mich zu Pariston huldigen',
                aliases=['Gebet','Predigt','Gespräch'],
                pass_context=True)

async def Huldigung(context):
    possible_responses = [
        'Es kann nur einen wahren Gott geben. Parsem Pariston.',
        'Ein Glaubensbruder ist für mich wie ein echter Bruder',
        'Warum Pariston der wahre Gott ist? Ich hab ihn gefragt, er verneinte. Diese Bescheidenheit hat nur ein wahrer Gott',
        'Was wären wir ohne Pariston, meine Brüder?',
        'Ritualmeister Nico macht einen zufriedenstellenden Job.',
        'Die letzte Ausgabe vom Leuchtturm hat mir ser gefallen.',
        'Für mich ist Zeuge der Woche Raion. Er präsentiert uns in den Artikeln wie kein anderer.',
        'Riecht es für euch hier auch nach Heiligtum?',
        'Schließe deine Augen und erinnere dich an die letzten Worte Paristons. Welche waren diese?',
        'Manchmal werde ich gefragt ob Kuras heilig wäre. Natürlich ist er das, er ist Kaiser in Gnaden Paristons.',
        'Könnt ihr euch noch an die Gemälde von Mohnarchfalter erinnern? Für mich immer wieder ein Ort zur Entspannung.',
        'Die Begnung Raions mit Pariston fand ich sehr inspirierend. Wie fandet ihr sie?',
        'Wie die Erde, die Pflanzen, die Meere und die Völker, so hat auch mich Pariston mit seinen heiligen Fingern erschaffen.',
        'Goldenes Haar, pinker Anzug, Zeuge na klar, alles andere wär Unfug.',
        'Willst du mit mir Klinken putzen?',
        'Meine Brüder, ihr müsst euch jeden Tag fragen: Was habe ich heute bereits für Pariston getan?',
        'Wer denkst wer du bist, hier auf dem Server nicht mal deine Schuhe auszuziehen?',
        'Gibt es was zu tun, mein Bruder?',
        'Essen? Trinken? Frauen? Ich brauch nur eins im Leben und das ist der große Pariston. Parsem mein Bruder',
        'Manchmal frag ich mich, ob die Freizeitzeugen einfach nur cool sein wollen mit dem Zeugennamen dahinter. Dann sag ich mir, es sind sicher nur stumme Glaubensbrüder.',
        'Entsagt allem weltlichen und dem Streben nach Macht, damit ihr euch komplett auf die Liebe zu unserem Heiland und Erlöser konzentrieren könnt.',
        'Vertraut auf Pariston unseren Herren. Er wird uns alle auf den richtigen Weg und in das Paradies führen.',
        'Das ewige Licht des Leuchtturms leuchte euch den Weg in die Arme unseres Erlösers.',
        'Rosen sind rot, Veilchen sind blau. Bist du kein Zeuge, wanderst du in den Bau.',
        'Vater Pariston im Himmel. Geheiligt werde deine Herrlichkeit. Dein Reich expandiere, Dein Wille geschehe. Wie bei den Zeugen, So überall auf Erden. Und vergib uns unsere Schuld, Wie auch wir vergeben unseren Schuldigern. Führe uns nicht in Kuras Arme,Sondern erlöse uns von dem Bösen. Denn du bist allwissend, gutaussehend und wunderbar. In Ewigkeit, Parsem.',
        'Ich werde nie vergessen wie Raion durch die Hallen des Paristons als erstes in wenigen Minuten durchmaschiert ist. So viel Wissen über unseren Erleuchter hätte ich auch gern.',
        'Hast du schonmal von Knäckebrot gehört? Guter Glaubensbruder.',
        'Viele Neulinge finden grad zum echten Glauben, ich denke uns stehen rosige Zeiten bevor.',
        'Es war dieser einer Tag in der Dusche. Ich hatte wieder Überstunden bei McDonalds machen müssen und Streß weil alle HappyMeal Spielzeuge alle waren. Komplett kaputt zu hause unter der Dusche dachte ich dann: Pariston, falls es dich gibt, gib mir ein Zeichen! Durch das Fenster am Duschvorhang vorbei wichen die Wolken der Berührung Paristons. Meine Haut erschien in seinem Anlitz und es wurde überall warm. Da war mir bewusst, es gibt ihn wirklich.',
        'Habt ihr schon eure Tipps für Tippspiel abgeben. Unser große Pariston weisten uns nur selten so deutlich den Weg, meine Brüder.',
        'Mal rein hypothetisch wir hätten Ungläubige hier: Düfrte ich ihren Account auf Discord sperren? Ich frag für ein Freund.',
        'Meine Zeugennummer werde ich nie vergessen. Pariston gab sie mir persönlich - in Hexadezimal <3',
        'Paristons Taten versetzen mich immer wieder ins Staunen. Mit welch einer Ausdauer und Liebe er sich seinen Söhnen und Töchtern widmet ist für mich jeden Tag aufs Neue ein Wunder.',
        'Ich kann mir gar nicht vorstellen, dass unser Pariston einst ein berühmter Bierpirat war. Sugoi!',
        'Psst, soll ich dir n Geheimnis erzählen? Der Parteiführer der BDD Barash. Das ist auch n Zeuge. Aber Undercover. Genauso wie Kuras und Daryl. Letztere können aber bei weiterm besser schauspielern.',
        'Holt Areon hierher, er soll die Leistungsträger im Chat waschen! - Oh falsche Zeit, oder?',
        'Manchmal frage ich mich, ob es schonmal Tage gab, an denen Didam und Schwüppe nicht grumpy waren. Dann denke ich mir, dass unser Pariston sicher auch mit ihnen ein höheren Plan verfolgt.',
        'Weißt du wer den Reifen erfunden hat? Ich auch nicht. Aber Pariston weiß es.',
        'Ich hab gehört Pariston kann mit einem Fingerwink Bilder,Texte und Personen bannen. Er muss ein Gott sein!',
        'Sorry hab grad n bisschen gedöst, was möchtest du?',
        'Treffen sich Costa, Kuras und Pariston beim Döner. Sagt Pariston:"Ich lad euch ein meine Söhne". Happy End.',
        'Hätte Pariston in Game of Thrones mit gespielt, wäre schon längst ein Zeuge auf dem Eisernen Thron.',
        'Hab letztens Hunter X Hunter geschaut, finde es toll wie außerordentlich clever sie Pariston dort darstellen.',
       
    ]
    await client.say('Lieber Bruder ' + context.message.author.mention + ': ' + random.choice(possible_responses))

@client.command(name='Ave',
                description="Freundliche Begrüßung",
                brief='Ave Pariston',
                aliases=['Ave Pariston'],
                pass_context=True)

async def Ave(context):
    await client.say('Ave Pariston!')



@client.event
async def on_ready():
    print('Logged in as MSU')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.loop.create_task(update_markt_background_task())
client.run(os.getenv('TOKEN'))


