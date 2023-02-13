from MtgDbHelper import *

def getDeckLists(addCombos=False):
    location = '/media/VMShare/OldDecks/Dragons/'
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(location) if isfile(join(location, f))]
    decks = []
    for file in onlyfiles:
        CD=CockatriceDeck()
        CD.load(location + file)
        decks.append(CD.cardSet)

    if addCombos:
        combos = getKnownCombos(True)  # other cards worth tracking
        usefull = set()
        usefull.add('Kyodai, Soul of Kamigawa')
        usefull.add('Tiamat')
        for combo in combos:
            for card in combo[1]:
                usefull.add(card)
        cardSet = MtgDbHelper.cards.subsetByNames(usefull)
        decks.append(cardSet)

    return decks


def combineComboTables(A, B):
    C = []
    for comboA in A:
        for comboB in B:
            C.append((comboA[0] * comboB[0], comboA[1] + comboB[1]))
    return C


def getKnownCombos(addGarbage=False, genPairs=False, namesOnly=False):
    # Finite
    combos = []
    nonLeathalWeight = 0.5
    combos.append((nonLeathalWeight, ['Arena', 'Foe-Razer Regent']))
    combos.append((nonLeathalWeight, ['Helm of the Host', 'Skyline Despot']))
    combos.append((nonLeathalWeight, ['Helm of the Host', 'Utvara Hellkite']))
    combos.append((nonLeathalWeight, ['Cackling Counterpart', 'Mirrorwing Dragon']))
    combos.append((nonLeathalWeight, ['Hematite Talisman', 'Swirl the Mists']))
    combos.append((nonLeathalWeight, ['Lapis Lazuli Talisman', 'Swirl the Mists']))
    combos.append((nonLeathalWeight, ['Malachite Talisman', 'Swirl the Mists']))
    combos.append((nonLeathalWeight, ['Onyx Talisman', 'Swirl the Mists']))
    combos.append((nonLeathalWeight, ['Nacre Talisman', 'Swirl the Mists']))
    combos.append((nonLeathalWeight, ['Dispersing Orb', 'Swirl the Mists']))
    combos.append((nonLeathalWeight, ['Pyre of Heroes', "Debtors' Knell"]))
    # combat trickery
    combos.append((nonLeathalWeight, ['Access Tunnel', 'Quicksilver Dragon']))
    combos.append((nonLeathalWeight, ['Scion of the Ur-Dragon', 'Teneb, the Harvester']))
    # destroy and resurrect
    combos.append((nonLeathalWeight, ['Synod Sanctum', "Bontu's Last Reckoning"]))
    combos.append((nonLeathalWeight, ['Living End', 'Supreme Verdict']))
    combos.append((nonLeathalWeight, ['Kindred Boon', "Kaya's Wrath"]))
    combos.append((nonLeathalWeight, ['Safe Haven', 'Damnation']))
    combos.append((nonLeathalWeight, ['Endless Sands', 'Day of Judgment']))
    combos.append((nonLeathalWeight, ['Grimoire of the Dead', 'Wrath of God']))
    combos.append((nonLeathalWeight, ["Twilight's Call", 'Tunnel Vision']))
    # repeatable combat cancellations
    combos.append((nonLeathalWeight, ['Sunstone', 'Waking the Trolls', 'Nesting Grounds', 'Ghirapur Orrery']))
    combos.append((nonLeathalWeight, ['Constant Mists', 'Clockspinning', 'Fall of the Thran']))

    leathalWeight = 1
    # Player Enders
    combos.append((leathalWeight, ['Inferno of the Star Mounts', 'Mana Flare', 'Extraplanar Lens', 'Chaos Moon']))
    combos.append((leathalWeight, ['Mindslaver', 'Trading Post', 'Followed Footsteps']))
    combos.append((leathalWeight, ['Mindslaver', 'Soldevi Digger', 'Planar Portal']))
    combos.append((leathalWeight, ['Aether Tunnel', 'Fireshrieker', 'Skithiryx, the Blight Dragon']))
    combos.append((leathalWeight, ['Hellkite Tyrant', 'Gadrak, the Crown-Scourge']))
    combos.append((leathalWeight,
                   ['Junji, the Midnight Sky', 'Heirloom Blade', 'Mortuary', 'Salvaging Station', 'Lotus Bloom',
                    'Mana Reflection', 'Betrothed of Fire']))
    # infinite damage/tokens/attack power
    combos.append((leathalWeight, ['Enduring Scalelord', 'Reflections of Littjara']))
    combos.append((leathalWeight, ['Goldspan Dragon', 'Seething Anger', 'Memory Crystal']))
    combos.append((leathalWeight, ['Lathliss, Dragon Queen', 'Nim Deathmantle', "Ashnod's Altar", 'Panharmonicon']))
    combos.append((leathalWeight, ['Lathliss, Dragon Queen', 'Deathrender', 'Zodiac Dragon', 'Life Chisel']))
    combos.append((leathalWeight, ['Worldgorger Dragon', 'Flameshadow Conjuring', 'Spawn of Thraxes']))
    combos.append((leathalWeight, ['Scourge of Valkas', 'Molten Echoes', 'Cryptic Gateway', 'Cloudstone Curio']))
    combos.append(
        (leathalWeight, ['Terror of the Peaks', 'Scythe of the Wretched', 'Bogardan Hellkite', 'Claws of Gix']))
    combos.append((leathalWeight, ['Vrondiss, Rage of Ancients', 'Blazing Sunsteel', 'That Which Was Taken']))
    combos.append((leathalWeight, ['Dragon Tempest', 'Bladewing the Risen', 'Mirrorpool']))
    combos.append((leathalWeight, ['Prossh, Skyraider of Kher', 'The Cauldron of Eternity', 'Verdant Succession']))
    combos.append(
        (leathalWeight, ['Broodmate Dragon', 'Dual Nature', 'Primal Vigor', 'Phyrexian Altar', 'Decaying Soil']))
    # draw based infinite damage
    combos.append((leathalWeight, ['Niv-Mizzet, Dracogenius', 'Cadaverous Bloom', 'False Dawn', 'Temporal Cascade']))
    combos.append((leathalWeight, ['Niv-Mizzet, Parun', 'Keen Sense', 'Temporal Cascade']))
    combos.append((leathalWeight, ['Niv-Mizzet, the Firemind', 'Curiosity', 'Mnemonic Nexus']))
    combos.append((leathalWeight, ['Sliv-Mizzet, Hivemind', 'Helm of the Ghastlord', 'Temporal Cascade']))
    # infinite landfall dragons
    combos.append((leathalWeight, ['Akoum Hellkite', 'Price of Glory', 'Sacred Ground', "Puca's Mischief"]))
    combos.append(
        (leathalWeight, ['Nesting Dragon', 'Perilous Forays', 'Squandered Resources', 'Wheel of Sun and Moon']))
    # infinite attacks
    combos.append((leathalWeight, ['Key to the City', 'Spellbinder', 'Savage Beating']))
    combos.append((leathalWeight, ['Whispersilk Cloak', 'Aggravated Assault', 'Savage Ventmaw']))
    combos.append(
        (leathalWeight, ["Rogue's Passage", "Nature's Will", 'Hellkite Charger', 'Klauth, Unrivaled Ancient']))
    combos.append((leathalWeight, ['Hot Soup', 'Breath of Fury', 'Enduring Renewal', 'Emergence Zone', 'Old Gnawbone']))
    nearLeathalWeight = .9
    # infinite turns with library restore
    combos.append((nearLeathalWeight, ['Timesifter', 'Mirror of Fate', 'Bow of Nylea', 'Draco']))
    combos.append((nearLeathalWeight, ['Beacon of Tomorrows', 'Obelisk of Undoing', 'Ring of Three Wishes']))
    # infinite turns
    combos.append((nearLeathalWeight, ["Magistrate's Scepter", 'Contagion Engine', 'Energy Chamber']))
    combos.append((nearLeathalWeight, ['Time Stretch', 'Power Conduit', 'The Mirari Conjecture']))
    combos.append((nearLeathalWeight, ['Time Stretch', 'Kairi, the Swirling Sky', 'Dawn of the Dead']))
    combos.append((nearLeathalWeight,
                   ['Time Sieve', 'Anointed Procession', 'Atsushi, the Blazing Sky', 'Sigil of the New Dawn',
                    'Immersturm Predator']))
    combos.append((nearLeathalWeight, ['Walk the Aeons', 'Crucible of Worlds', 'Rites of Flourishing', 'Druid Class']))
    combos.append((nearLeathalWeight, ['Second Chance', 'Skull of Orm']))
    combos.append((nearLeathalWeight, ['Time Warp', 'Mystic Sanctuary', 'Trade Routes']))
    combos.append((nearLeathalWeight,
                   ['Final Fortune', 'Sundial of the Infinite', "Conqueror's Galleon // Conqueror's Foothold"]))
    combos.append(
        (nearLeathalWeight, ["Gonti's Aether Heart", 'Prototype Portal', "Glassblower's Puzzleknot", 'Academy Ruins']))
    # combos.append((nearLeathalWeight,['Magosi, the Waterveil', "Karn's Bastion", 'Everythingamajig(Everythingamajig(a))']))
    combos.append((nearLeathalWeight, ['Magosi, the Waterveil', "Karn's Bastion", 'Giant Fan']))
    combos.append((nearLeathalWeight, ['Magosi, the Waterveil', "Karn's Bastion", 'Nesting Grounds']))

    # infinite mana
    mWeight = 1
    manaCombos = []
    manaCombos.append((mWeight, ['Gemstone Array', 'Doubling Season', 'Mirrormade']))
    manaCombos.append((mWeight, ['Mycosynth Lattice', 'Rings of Brighthearth', 'Basalt Monolith']))
    manaCombos.append((mWeight, ['Cave of the Frost Dragon', 'Sheltered Aerie', "Pemmin's Aura"]))
    manaCombos.append((mWeight, ['Component Pouch', 'Animate Artifact', 'Freed from the Real', "Battlemage's Bracers"]))
    # spell based infinit mana
    spellmanaCombos = []
    spellmanaCombos.append((mWeight, ['Inner Fire', 'Reiterate']))
    spellmanaCombos.append(
        (mWeight, ['Rude Awakening', "Narset's Reversal", 'Primal Amulet // Primal Wellspring', 'Swarm Intelligence']))
    spellmanaCombos.append((mWeight, ['Early Harvest', 'Mirror Sheen']))
    spellmanaCombos.append((mWeight, ['Thousand-Year Storm', 'Spelljack', "Brass's Bounty"]))
    manaCombos = manaCombos + spellmanaCombos
    # draw based infinite mana
    manaCombos.append((mWeight, ['Mesmeric Trance', 'Telekinetic Bonds', 'Storm the Vault // Vault of Catlacan',
                                 'Elixir of Immortality']))
    # token infinite mana with untaps
    untapAndSpellManaCombos = []
    untapAndSpellManaCombos.append((mWeight, ['Isochron Scepter', 'Dramatic Reversal', 'Gilded Lotus']))
    untapAndSpellManaCombos.append((mWeight,
                                    ['Hematite Talisman', 'Crown of Flames', 'Scorched Ruins', "Dawn's Reflection",
                                     'Trace of Abundance']))
    untapAndSpellManaCombos.append((mWeight, ['Lapis Lazuli Talisman', 'Shimmering Wings', 'Lotus Vale', 'Wild Growth',
                                              'Wolfwillow Haven', 'Zendikar Resurgent']))
    untapAndSpellManaCombos.append(
        (mWeight, ['Malachite Talisman', 'Whip Silk', 'City of Shadows', 'Overgrowth', 'Verdant Haven']))
    untapAndSpellManaCombos.append((mWeight, ['Onyx Talisman', 'Mourning', 'Lotus Field', 'Market Festival',
                                              'Dictate of Karametra', 'Heartbeat of Spring']))
    untapAndSpellManaCombos.append((mWeight,
                                    ['Nacre Talisman', 'Flickering Ward', "Serra's Sanctum", 'Glittering Frost',
                                     'Fertile Ground', 'Swirl the Mists']))
    manaCombos = manaCombos + untapAndSpellManaCombos
    # infinite mana/copy
    manaCopyCombos = []
    manaCopyCombos.append((.1, ['Lithoform Engine', 'Toils of Night and Day', 'Coveted Jewel', 'Dreamstone Hedron']))
    manaCopyCombos.append((.1, ['Twinning Staff', 'Turnabout', 'Empowered Autogenerator']))
    manaCombos = manaCombos + manaCopyCombos

    # token based infinite mana
    cmWeight = 1
    tokenManaCombo = []
    tokenManaCombo.append((cmWeight, ['Cryptolith Rite', 'Intruder Alarm']))
    tokenManaCombo.append((cmWeight, ['Song of Freyalise', 'Faces of the Past', 'Fanatical Devotion']))
    tokenManaCombo.append((cmWeight, ['Earthcraft', 'Overlaid Terrain',
                                      'Vernal Bloom']))  # depends on cost of tokens assuming broodkeeper and forest

    # infinite damage/tokens/attack power for infinite mana & untap/non-creature
    comboWeight = 1
    untapmanaConsumers = []
    untapmanaConsumers.append((comboWeight, ["Volrath's Laboratory"]))
    untapmanaConsumers.append((comboWeight, ['Riptide Replicator']))
    untapmanaConsumers.append((comboWeight, ['Mimic Vat']))
    untapmanaConsumers.append((comboWeight, ['Bag of Tricks']))
    untapmanaConsumers.append((comboWeight, ['Feywild Trickster', 'Fractured Powerstone']))
    untapmanaConsumers.append((comboWeight, ['Feywild Trickster', 'Component Pouch']))
    untapmanaConsumers.append((comboWeight, ['Song of the Worldsoul', 'Littjara Mirrorlake']))
    untapmanaConsumers.append((comboWeight, ['Soul Foundry']))
    combos = combos + combineComboTables(untapmanaConsumers, untapAndSpellManaCombos)

    # spell based consumers
    spellConsumers = []
    spellConsumers.append((comboWeight, ['Sprite Dragon']))
    spellConsumers.append((comboWeight, ['Cunning Breezedancer']))
    combos = combos + combineComboTables(spellConsumers, untapAndSpellManaCombos)
    spellConsumers.append((comboWeight, ['Smoldering Egg // Ashmouth Dragon']))
    combos = combos + combineComboTables(spellConsumers, spellmanaCombos)  # misses isochron mana

    # infinite damage/tokens/attack power for infinite mana
    manaConsumers = []
    consumerWeight = 1
    manaConsumers.append((consumerWeight, ['Kilnmouth Dragon', 'Staff of Domination']))
    manaConsumers.append((consumerWeight, ['Sarkhan the Masterless', 'Oath of Teferi', 'Disappear']))
    manaConsumers.append((consumerWeight, ['Sarkhan, the Dragonspeaker', 'Oath of Teferi', 'Disappear']))
    manaConsumers.append((consumerWeight, ['Sarkhan Unbroken', "Sarkhan's Whelp", 'Words of Wind']))
    manaConsumers.append((consumerWeight, ['Clockwork Dragon']))
    manaConsumers.append((consumerWeight, ['Skarrgan Hellkite']))
    manaConsumers.append((consumerWeight, ['Flameblast Dragon']))
    manaConsumers.append((consumerWeight, ['Shivan Hellkite']))
    manaConsumers.append((consumerWeight, ['Shivan Dragon']))
    manaConsumers.append((consumerWeight, ['Moonveil Dragon']))
    manaConsumers.append((consumerWeight, ['Mordant Dragon']))
    manaConsumers.append((consumerWeight, ['Freejam Regent']))
    manaConsumers.append((consumerWeight, ['Dragon Roost']))
    manaConsumers.append((consumerWeight, ['Mana-Charged Dragon']))
    manaConsumers.append((consumerWeight, ['Hellkite Igniter']))
    manaConsumers.append((consumerWeight, ["Tatsumasa, the Dragon's Fang", 'Fallen Ideal']))
    manaConsumers.append((consumerWeight, ['Korvold, Fae-Cursed King', 'Dark Privilege', 'Arashin Sovereign']))
    # token mana consumers
    tokenManaConsumers = []
    tokenManaConsumers.append((consumerWeight, ['Garth One-Eye', 'Escape Routes', 'Thousand-Year Elixir']))
    tokenManaConsumers.append((consumerWeight, ['Brood Keeper', 'Ghitu Firebreathing']))
    tokenManaConsumers.append((consumerWeight, ['Draconic Disciple', "Fool's Demise", 'Fires of Yavimaya']))
    tokenManaConsumers.append((consumerWeight, ['Goro-Goro, Disciple of Ryusei']))
    tokenManaConsumers.append((consumerWeight, ['Dragon Whisperer']))
    tokenManaConsumers.append((consumerWeight, ['Minion Reflector', 'Equilibrium']))
    combos = combos + combineComboTables(tokenManaConsumers, tokenManaCombo)
    manaConsumers = manaConsumers + tokenManaConsumers
    combos = combos + combineComboTables(manaConsumers, manaCombos)

    # infinite damage/tokens/attack power for infinite copy
    copySeeds = []
    copyWeights = 1
    copySeeds.append((copyWeights, ['Cackling Counterpart']))
    copySeeds.append((copyWeights, ['Back from the Brink', 'Pull from Eternity']))
    combos = combos + combineComboTables(manaConsumers, manaCopyCombos)

    if genPairs and addGarbage:
        combos0 = combos
        combos = []
        for c in combos0:
            for n1 in range(len(c[1])):
                combos.append((c[0], [c[1][n1]]))

    if addGarbage:
        garbageSynergy = .001
        garbage = []
        # some mostly worthless cards given the infinite goals
        garbage.append((garbageSynergy, ['Abandon Reason']))
        garbage.append((garbageSynergy, ['Abnormal Endurance']))
        garbage.append((garbageSynergy, ['Accelerated Mutation']))
        garbage.append((garbageSynergy, ['Act of Heroism']))
        garbage.append((garbageSynergy, ['Arcane Subtraction']))
        garbage.append((garbageSynergy, ["Angel's Tomb"]))
        garbage.append((garbageSynergy, ['Accelerate']))
        garbage.append((garbageSynergy, ['Act of Authority']))
        garbage.append((garbageSynergy, ['Aim High']))
        garbage.append((garbageSynergy, ["Alchemist's Gift"]))
        garbage.append((garbageSynergy, ["Arnjlot's Ascent"]))
        garbage.append((garbageSynergy, ["Arcum's Sleigh"]))
        garbage.append((garbageSynergy, ['Blessed Alliance']))
        # garbage.append((garbageSynergy,['Better Offer']))
        garbage.append((garbageSynergy, ['Bond of Revival']))
        garbage.append((garbageSynergy, ['Earthbind']))
        garbage.append((garbageSynergy, ['Healing Leaves']))
        garbage.append((garbageSynergy, ['Base Camp']))
        garbage.append((garbageSynergy, ['Absorb']))
        garbage.append((garbageSynergy, ['Cathedral of War']))
        garbage.append((garbageSynergy, ['Cloudpost']))
        garbage.append((garbageSynergy, ['Coral Atoll']))
        # garbage.append((garbageSynergy,['Field of the Dead']))
        garbage.append((garbageSynergy, ['Ruins of Oran-Rief']))
        garbage.append((garbageSynergy, ['Untaidake, the Cloud Keeper']))
        garbage.append((garbageSynergy, ['Wintermoon Mesa']))
        garbage.append((garbageSynergy, ['Aether Helix']))
        garbage.append((garbageSynergy, ['Awesome Presence']))
        garbage.append((garbageSynergy, ['Bad Moon']))
        garbage.append((garbageSynergy, ['Bar the Door']))
        garbage.append((garbageSynergy, ['Capture Sphere']))
        garbage.append((garbageSynergy, ['Cast Down']))
        garbage.append((garbageSynergy, ['Cast into Darkness']))
        garbage.append((garbageSynergy, ['Celestial Purge']))
        garbage.append((garbageSynergy, ['Crystal Slipper']))
        garbage.append((garbageSynergy, ['Curate']))
        garbage.append((garbageSynergy, ['Drown in Dreams']))
        garbage.append((garbageSynergy, ['Dry Spell']))
        garbage.append((garbageSynergy, ['Fiery Intervention']))
        garbage.append((garbageSynergy, ['Fire Whip']))
        garbage.append((garbageSynergy, ['Infuse']))
        # garbage.append((garbageSynergy,['Inscription of Insight']))
        garbage.append((garbageSynergy, ['Inspiration']))
        garbage.append((garbageSynergy, ['Intangible Virtue']))
        garbage.append((garbageSynergy, ['Luminescent Rain']))
        garbage.append((garbageSynergy, ['Macabre Waltz']))
        garbage.append((garbageSynergy, ["Mage Hunters' Onslaught"]))
        garbage.append((garbageSynergy, ['Magefire Wings']))
        garbage.append((garbageSynergy, ['Magma Mine']))
        garbage.append((garbageSynergy, ["Nature's Cloak"]))
        if not namesOnly:
            combos = combineComboTables(combos, garbage)

    if namesOnly:
        combos0 = combos
        combos = []
        for c in combos0:
            combos=combos+c[1]
        if addGarbage:
            for c in garbage:
                combos=combos+c[1]
    else:
        if genPairs and not addGarbage:
            combos0 = combos
            combos = []
            for c in combos0:
                for n1 in range(len(c[1])):
                    for n2 in range(n1 + 1, len(c[1])):
                        combos.append((c[0], [c[1][n1], c[1][n2]]))

    return combos

def getKnownCombosAndDeck(addGarbage=False, genPairs=False, namesOnly=False):
    combos=getKnownCombos(addGarbage, genPairs, namesOnly)
    decks=getDeckLists(False)
    for deck in decks:
        for row in range(len(deck)):
            for col in range(row,len(deck)):
                combos.append([.25,[deck[row].name]+[deck[col].name]])
    return combos


class CockatriceDeck:
    def __init__(self) -> None:
        self.cards=dict()
        self.cardSet=[]
        self.cardSetIndexes=[]
        if not MtgDbHelper.cards:
            MtgDbHelper.initDb(False)

    def setByInds(self,inds):
        self.cardSetIndexes=inds
        self.cardSet=MtgDbHelper.cards.subsetByInds(inds)
        for card in self.cardSet.internalSet:
            if(card.name in self.cards):
                self.cards[card.name]=self.cards[card.name]+1
            else:
                self.cards[card.name]=1;

    def load(self,file):
        with open(file) as f:
            lines = f.readlines()
            f.close()
        # todo switch to xml reader
        deck = []
        for line in lines:
            if '<card' in line:
                info = line.split('"')
                count = int(info[1])
                name = info[3]
                for element in range(count):
                    deck.append(name)
        self.setByInds(MtgDbHelper.cards.findCards(deck, equalsNotLike=False))
    
    def save(self,file):
        lines=[]
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append('<cockatrice_deck version="1">')
        lines.append('    <deckname>Arcades</deckname>')
        lines.append('    <comments></comments>')
        lines.append('    <zone name="main">')
        for name in self.cards.keys:
            count=self.cards[name]
            lines.append('      <card number="'+ str(count) +'" name="'+name+'"/>')
        lines.append('    </zone>')
        lines.append('</cockatrice_deck>')
        with open(file,'wb') as f:
            f.writelines(lines)
            f.close()

    def loadText(self,file):
        with open(file) as f:
            deck = f.read().splitlines()
            f.close()        
        self.setByInds(MtgDbHelper.cards.findCards(deck))
    
    def saveText(self,file):
        deck=[]
        for name in self.cards.keys():
            count=self.cards[name]
            for c in range(count):
                deck.append(name)
        with open(file,'w') as f:
            for card in deck:
                f.write(card+'\r\n')
            f.close()