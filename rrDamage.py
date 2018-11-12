import bs4
import requests
import datetime
import asyncio
import aiohttp
import async_timeout


myheader = \
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "__cfduid=d2705bc460223ef7f069256427d659faf1541866862; PHPSESSID=lltg33li1lht38bmpv0qd2oec5; __atuvc=1%7C45%2C3%7C46; __atuvs=5be9a82b9e2e59ab000; rr=a5c5a9aa9b7f4aeff3a8e9130785f815; rr_id=2000268192; rr_add=b6f6c9c4302871cfc965f908109c6c21",
        "Host": "rivalregions.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    }


async def MultiplayerDmg(urllist,profildict,partylist,urlplayer):
    async with aiohttp.ClientSession(headers=myheader) as session:

        playerdmg = {}
        for url in urllist:
            adder = 0
            url0 = url.replace("#war/details", "war/damage") + "/0"
            tempdmg,profildict,urlplayer = await getPlayerDamage0(url0,session,profildict,partylist,adder,urlplayer)
            print("In multiplayer: ", tempdmg)
            for name in tempdmg:
                if name in playerdmg:
                    playerdmg[name] += tempdmg[name]
                else:
                    playerdmg[name]=tempdmg[name]
            adder = 0
            url1 = url.replace("#war/details", "war/damage") + "/1"
            tempdmg, profildict,urlplayer = await getPlayerDamage1(url1, session, profildict, partylist, adder,urlplayer)
            print("In multiplayer: ", tempdmg)
            for name in tempdmg:
                if name in playerdmg:
                    playerdmg[name] += tempdmg[name]
                else:
                    playerdmg[name] = tempdmg[name]

        return playerdmg,urlplayer

async def getPlayerDamage0(url,session,profildict,partylist,adder,urlplayer):
    print(partylist)
    print("Url=",url)
    player = []
    damage = []
    counter = 1

    html = await fetch(session, url)
    soup = await soup_d(html)


    counta=0
    for profil in soup.find_all(attrs={"class":"list_name pointer"}):
        print("normal",str(profil))
        counta +=1
        name=profil.get_text()
        if name not in profildict:
            profil = str(profil)
            profil = profil.split(" ")
            profil = profil[1].split("/")
            Id = profil[2]
            Id = Id[0:-1]

            urlplayer[name]= "rivalregions.com/#slide/profile/"+str(Id)

            party= await getProfilParty(Id,session)
            profildict[name]=party
            print(name)
            print(party)
        player.append(name)

    for profil in soup.find_all(attrs={"class": "list_name pointer tip green"}):
        print("normal tip green", str(profil))
        counta += 1
        name = profil.get_text()
        if name not in profildict:
            profil = str(profil)
            profil = profil.split(" ")
            profil = profil[1].split("/")
            Id = profil[2]
            Id = Id[0:-1]

            urlplayer[name] = "rivalregions.com/#slide/profile/" + str(Id)

            party = await getProfilParty(Id, session)

            print(name)
            print(party)
            profildict[name] = party
        player.append(name)

    print("counta:", counta)


    for dmg in soup.find_all(attrs={"class":"yellow"}):
        if counter%2 == 0:
            d = dmg.get_text()
            d = d.replace(".", "")
            damage.append(int(d))
        counter+=1

    playerdamagedict = {}

    for count, pl in enumerate(player):
        playerdamagedict [pl] = damage[count]

    print(playerdamagedict)
    playerpartys = {}
    for name in playerdamagedict:
        if profildict[name] in partylist:
            if name in playerpartys:
                playerpartys[name] += playerdamagedict[name]
            else:
                playerpartys[name] = playerdamagedict[name]

    if counta == 25:
        print("In adder", adder)
        if adder != 0:
            newurl = url.split("/")
            url = url.replace("/" + newurl[-1], "")
        adder += 25
        url = url + "/" + str(adder)
        tempdict, profildict,urlplayer = await getPlayerDamage0(url,session,profildict,partylist,adder,urlplayer)
        print("Tempdict: ",tempdict)
        print("Playerpartys: ", playerpartys)
        for name in tempdict:
            if name in playerpartys:
                playerpartys[name] += tempdict[name]
            else:
                playerpartys[name] = tempdict[name]

    return playerpartys,profildict,urlplayer


async def getPlayerDamage1(url, session, profildict, partylist,adder,urlplayer):
    print("Url=", url)

    player = []
    damage = []
    counter = 1

    html = await fetch(session, url)
    soup = await soup_d(html)

    counta=0
    for profil in soup.find_all(attrs={"class":"list_name pointer"}):
        counta +=1

        name = profil.get_text()
        if name not in profildict:
            profil = str(profil)
            profil = profil.split(" ")
            profil = profil[1].split("/")
            Id = profil[2]
            Id = Id[0:-1]

            urlplayer[name] = "http://rivalregions.com/#slide/profile/" + str(Id)
            party = await getProfilParty(Id, session)
            print(name)
            print(party)
            profildict[name] = party
        player.append(name)


    for dmg in soup.find_all(attrs={"class": "yellow"}):
        if counter % 2 == 0:
            d = dmg.get_text()
            d = d.replace(".","")
            damage.append(int(d))
        counter += 1

    playerdamagedict = {}

    for count, pl in enumerate(player):
        playerdamagedict[pl] = damage[count]

    playerpartys = {}
    for name in playerdamagedict:
        if profildict[name] in partylist:
            if name in playerpartys:
                playerpartys[name] += playerdamagedict[name]
            else:
                playerpartys[name] = playerdamagedict[name]



    if counta == 25:
        print("In adder",adder)
        if adder != 0:
            newurl = url.split("/")
            url = url.replace("/" + newurl[-1],"")
        adder += 25
        url = url + "/" + str(adder)
        tempdict, profildict,urlplayer = await getPlayerDamage1(url,session,profildict,partylist,adder,urlplayer)
        for name in tempdict:
            if name in playerpartys:
                playerpartys[name] += tempdict[name]
            else:
                playerpartys[name] = tempdict[name]

    print("RawDamage URL: ", url)
    print("In RawDamage" , playerpartys)

    return playerpartys,profildict,urlplayer


async def getMSUPlayer(partyid,adder):
    async with aiohttp.ClientSession(headers=myheader) as session:

        playernames = {}
        if adder == 0:
            partyurl = "http://rivalregions.com/listed/party/" + str(partyid)
        else:
            partyurl = "http://rivalregions.com/listed/party/" + str(partyid)+"/"+str(adder)

        profilurl = "http://rivalregions.com/#"

        html = await fetch(session, partyurl)
        soup = await soup_d(html)
        counter = 0

        for member in soup.find_all(attrs={"class": "list_name pointer"}):
            membername = member.get_text()
            membername = membername.strip()

            memberx = str(member)
            name = memberx.split('<div style="margin-top: -5px;">')
            name = name[1].split(' <span class="green">')
            name = name[0].strip()
            try:
                name = name.split("<br/>")
                name = name[0].strip()
            except:
                pass

            strings = memberx.split(" ")
            purl = strings[1].split("=")
            purl = purl[1].replace('"','')
            purl = profilurl + purl

            playernames[name] = purl
            counter += 1

        if counter == 25:
            adder += 25
            tempdict = await getMSUPlayer(partyid,adder)
            for x in tempdict:
                playernames[x]= tempdict[x]

        return playernames



async def getRawDamage(url,session):

    partys = []
    damage = []
    counter = 1

    url = url.replace("#war/details","listed/partydamage")
    html = await fetch(session, url)
    soup = await soup_d(html)

    for party in soup.find_all(attrs={"class":"list_name pointer"}):
        party=party.get_text()
        party= party[0:-14]
        partys.append(party)

    for dmg in soup.find_all(attrs={"class":"yellow"}):
        if counter%2 == 1:
            damage.append(dmg.get_text())
        counter+=1
    print("RawDamage URL: ", url)
    print("In RawDamage. damagelist: ", damage, " partylist ",partys)

    return partys,damage

async def RefineDamage(url,partylist,session):

    partys,damage= await getRawDamage(url,session)
    Gesamtdamage=0
    partydictRawDmg={}
    partydictPerDmg={}

    for n1,Rang in enumerate(partys):
        for n2,p in enumerate(partylist):
            if Rang == p:
                dmg=damage[n1].replace('.','')
                dmg=int(dmg)


                if Rang in partydictRawDmg:
                    partydictRawDmg[Rang] = partydictRawDmg[Rang] - dmg
                    Gesamtdamage = Gesamtdamage - dmg
                else:
                    partydictRawDmg[Rang]=dmg
                    Gesamtdamage += dmg

    for i in partydictRawDmg:
        Percent = partydictRawDmg[i]/Gesamtdamage * 100
        partydictPerDmg[i]=Percent

    return Gesamtdamage,partydictRawDmg,partydictPerDmg

async def MultiWar(urllist,partylist):
    async with aiohttp.ClientSession(headers=myheader) as session:

        urlcopy = urllist.copy()

        counter1=0
        for url in urllist:
            counter2=0
            for url2 in urllist:
                if url == url2:
                    if counter1 != counter2:
                        print ("Remove ",url)
                        urllist.remove(url)
                counter2 +=1
            counter1 +=1

        for url1 in urlcopy:
            if url1 in urllist:
                    pass
            else:
                print(url1)
                urllist.append(url1)

        print(urllist)
        Gesamtdamage = 0
        partydictRawDmg = {}
        partydictPerDmg = {}
        print("In Multiwar. URLlist: ", urllist)
        for x in urllist:
            PartDamage,PartRawDmg,PartPerDmg = await RefineDamage(x,partylist,session)
            Gesamtdamage += PartDamage

            for i in PartRawDmg:
                if i in partydictRawDmg:
                    partydictRawDmg[i] += PartRawDmg[i]
                else:
                    partydictRawDmg[i] = PartRawDmg[i]
            print(partydictRawDmg)

        for i in partydictRawDmg:
            Percent = partydictRawDmg[i]/Gesamtdamage * 100
            partydictPerDmg[i]=Percent

        return Gesamtdamage,partydictRawDmg,partydictPerDmg

async def getStateWars7d(stateid,days):
    async with aiohttp.ClientSession(headers=myheader) as session:
        regionlist = []
        StateUrl="http://rivalregions.com/listed/state/"
        url = StateUrl + stateid
        html = await fetch(session, url)
        soup = await soup_d(html)

        print("in get statewars, stateid: ", stateid)

        for e in soup.find_all(attrs={"class": "list_name pointer small"}):
            x = str(e)
            x = x.split(" ")
            y = x[1].split("=")
            z = y[1].replace('"', '')
            ids = z.split("/")
            id = ids[2]
            id = id.strip()
            regionlist.append(id)

        now = datetime.datetime.now()
        siebenDays = now + datetime.timedelta(days=-days)
        yesterday= now + datetime.timedelta(days=-1)

        warlistState = []

        BaseUrl = "http://rivalregions.com/war/top/"
        for i in regionlist:
            RegionWarUrl = BaseUrl + i
            html = await fetch(session, RegionWarUrl)
            soup = await soup_d(html)

            warlist = []
            for w in soup.find_all(attrs={"class": "list_avatar yellow pointer"}):
                x = str(w)
                x = x.split(" ")
                y = x[1].split("=")
                z = y[1].replace('"', '')
                ids = z.split("/")
                id = ids[2]
                warlist.append(id)

            warcounter = 0
            todaycounter = 0
            datelist = []
            for i in soup.find_all(attrs={"class": "list_avatar pointer small"}):
                date = i.get_text()
                try:
                    date = datetime.datetime.strptime(date, "%d %B %Y %H:%M")
                    if date > yesterday:
                        todaycounter += 1
                    else:
                        datelist.append(date)

                except:
                    todaycounter += 1
                    warcounter +=1


            for q in datelist:
                if q > siebenDays:
                    warcounter += 1
            if warcounter > 0:
                for i in range(warcounter):
                    if i >= todaycounter:
                        warlistState.append(warlist[i])
        print("WarListState: ",warlistState)
        return warlistState

async def KriegsAnalyse(url):
    async with aiohttp.ClientSession(headers=myheader) as session:
        html = await fetch(session, url)
        soup = await soup_d(html)

        print ("in Kriegsanalyse, url: ",url)

        for e in soup.find_all(attrs={"class": "minwidth"}):
            text = e.get_text()
            müll,text= text.split("series: [{ name: 'Damage', data:")
            text,müll = text.split(", negativeColor:")
            text = text.replace("[","")
            text = text.replace("]", "")
            liste = text.split(",")

        GesamtDamage = []
        Differenz = []

        counter = 0
        for point in liste:
            if counter % 2 == 0:
                GesamtDamage.append(int(point))
            if counter % 2 == 1:
                Differenz.append(int(point))

            counter +=1

        Dmg1h = Differenz[-1]-Differenz[-61]
        Dmg30min= Differenz[-1]-Differenz[-31]
        Dmg10min= Differenz[-1]-Differenz[-11]
        Dmg1h ="1h: " + MakeNumber2PrettyString(Dmg1h)
        Dmg30min = "Halbe Stunde: " + MakeNumber2PrettyString(Dmg30min)
        Dmg10min = "10 min: " + MakeNumber2PrettyString(Dmg10min)

        Dmg1h = Dmg1h.replace("-.","-")
        Dmg30min=Dmg30min.replace("-.","-")
        Dmg10min= Dmg10min.replace("-.","-")

        return Dmg1h,Dmg30min,Dmg10min


def MakeNumber2PrettyString(number):
    number = str(number)
    length = len(number)
    newnumber = ""
    counter = 0
    for x in range(length):
        if counter % 3 == 0 and counter != 0:
            newnumber+= "."+number[length-x-1]
            counter+=1
        else:
            newnumber+= number[length-x-1]
            counter +=1

    newLength=len(newnumber)
    finalnumber=''
    for i in range(newLength):
        finalnumber += newnumber[newLength-i-1]

    return finalnumber


async def fetch(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def soup_d(html, display_result=False):
    soup = bs4.BeautifulSoup(html, 'html.parser')
    if display_result:
        print(soup.prettify())
    return soup

async def RessToMoney(Ress,Marktdict):

    amount,TypeOfRess= Ress.split(' ')

    amount = int(amount.replace('.',''))

    # PriceStateMoney = 1
    # PriceStateGold = 500000
    # PriceOil = 150
    # PriceOre = 150
    # PriceDiamonds = 840000
    # PriceUranium = 1300

    Value = 0

    if "$" in TypeOfRess:
        Value = round(int(Marktdict["Staatsgeld"]) * amount)
    if "G" in TypeOfRess:
        Value = int(Marktdict["Staatsgold"]) * amount
    if "kg" in TypeOfRess:
        Value = int(Marktdict["Öl"]) * amount
    if "bbl" in TypeOfRess:
        Value = int(Marktdict["Erz"]) * amount
    if "pcs" in TypeOfRess:
        Value = int(Marktdict["Diamanten"]) * amount
    if "g" in TypeOfRess:
        Value = int(Marktdict["Uran"]) * amount

    return Value

async def getMarktPreise():
    async with aiohttp.ClientSession(headers=myheader) as session:
        url = "http://rivalregions.com/storage/listed/3"
        html = await fetch(session, url)
        soup = await soup_d(html)
        marktpreise = {}
        marktdict= {}
        marktdict["Öl"] = "3"
        marktdict["Erz"] = "4"
        marktdict["Diamanten"] = "15"
        marktdict["Uran"] = "11"

        for stoff in marktdict:
            url = "http://rivalregions.com/storage/listed/" + marktdict[stoff]
            html = await fetch(session, url)
            soup = await soup_d(html)
            counter = 0
            wert = 0
            for e in soup.find_all(attrs={"class": "white green imp small"}):
                x = e.get_text()
                x = x.replace("$","")
                x = x.replace(".","")
                x= x.strip()
                wert += int(x)
                counter += 1
                if counter == 3:
                    marktpreise[stoff] = str(round(wert/3))
                    break

        return marktpreise

async def getProfilParty(profilid,session):
    BaseUrl = "http://rivalregions.com/slide/profile/"
    url = BaseUrl + profilid
    print("Profilurl: ",url)


    html = await fetch(session, url)
    soup = await soup_d(html)

    #r = requests.get(url, headers=myheader)
    #r = r.content
    #soup = bs4.BeautifulSoup(r, 'html.parser')
    party = ""
    counter = 1
    for party in soup.find_all(attrs={"class": "header_buttons_hover slide_profile_link tc"}):
        if counter == 2:
            party = party.get_text()
        if counter == 3:
            party = party.get_text()
        counter +=1
    try:
        party = party.replace("Ã¼","ü")
        party  = party.replace("\n","")
    except:
        party = "Unaffiliated"
    #print(party + "Eintrag aus getProfilParty")
    return party


async def getRegionDonations(regionid, partylist,profildict, session,marktdict, days):
    try:
        id,adder = regionid.split("/")
        adder = int(adder)
    except:
        adder = 0

    BaseUrl = "http://rivalregions.com/listed/donated_regions/"
    url = BaseUrl + regionid
    print(url)

    html = await fetch(session, url)
    soup = await soup_d(html)

    #r = requests.get(url, headers=myheader)
    #soup = bs4.BeautifulSoup(r)

    now = datetime.datetime.now()
    siebenDays = now + datetime.timedelta(days=-days)
    datebool=[]

    for dates in soup.find_all(attrs={"class": "list_avatar pointer small"}):
        date = dates.get_text()
        try:
            date = datetime.datetime.strptime(date, "%d %B %Y %H:%M")
            if date > siebenDays:
                datebool.append(True)
            else:
                datebool.append(False)
        except:
            datebool.append(True)

    Party=""
    Partybool=False
    Partydonations={}


    counter = 0
    listcounter = 0
    for donation in soup.find_all(attrs={"class": "list_avatar pointer imp"}):

        if counter % 2 == 0 and counter != 0: listcounter += 1
        if datebool[listcounter]== True:

            if counter % 2 == 0:
                x = str(donation)
                x = x.split(" ")
                y = x[1].split("=")
                z = y[1].replace('"', '')
                ids = z.split("/")
                id = ids[2]

                if id in profildict:
                    Party = profildict[id]
                    #print(Party + "aus Profildict")
                else:
                    Party = await getProfilParty(id,session)
                    profildict[id]=Party

                try:
                    Party = Party.strip()
                except:
                    print(id)

                if Party in partylist:
                    Partybool = True
                else:
                    Partybool = False

            if counter % 2 == 1:
                donation = donation.get_text()
                if Partybool == True:
                    #print(Party)
                    if Party in Partydonations:
                        #print(Partydonations[Party])
                        Partydonations[Party] = Partydonations[Party] + await RessToMoney(donation,marktdict)
                    else:
                        Partydonations[Party] = await RessToMoney(donation,marktdict)
                        #print(RessToMoney(donation))
        counter+=1
        #print(Partydonations)
    print("Datebool: " , datebool[listcounter])
    if datebool[listcounter]==True:
        adder += 25
        try:
            id,a = regionid.split("/")
            id=id.strip()
            regionid = id
        except:
            pass
        regionid = regionid + "/" + str(adder)
        print("Im if, regionid: ", regionid)
        partydict = await getRegionDonations(regionid,partylist,profildict,session, marktdict,days)
        for x in partydict:
            if x in Partydonations:
                Partydonations[x] = Partydonations[x] + partydict[x]
            else:
                Partydonations[x] = partydict[x]

    return Partydonations

async def getStateDonations(stateid,partylist,profildict, marktdict, days):

    async with aiohttp.ClientSession(headers=myheader) as session:

        regionlist = []
        StateUrl = "http://rivalregions.com/listed/state/"
        url = StateUrl + stateid
        html = await fetch(session, url)
        soup = await soup_d(html)
        # r = requests.get(url, headers=myheader)
        # r = r.content
        # soup = bs4.BeautifulSoup(r, 'html.parser')

        partydonations={}

        for e in soup.find_all(attrs={"class": "list_name pointer small"}):
            x = str(e)
            x = x.split(" ")
            y = x[1].split("=")
            z = y[1].replace('"', '')
            ids = z.split("/")
            id = ids[2]

            regionlist.append(id)
        counter= 1
        for region in regionlist:
            print("region nr. %d: " %counter + region)
            tempdonations = await getRegionDonations(region,partylist,profildict,session, marktdict, days)
            for p in tempdonations:
                if p in partydonations:
                    partydonations[p] = partydonations[p] + tempdonations[p]
                else:
                    partydonations[p]=tempdonations[p]
            counter+=1

        return partydonations





