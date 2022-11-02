from SQLHelper import *
from CardSet import *
import subprocess
from JasonToMysql import setupDB


class MtgDbHelper:
    dbName = 'MTG_FULL4'
    subDbName = 'MTG_DragonFriendly'
    user = 'mal'
    pw = 'sql'

    @classmethod
    def __MakeFull(cls):
        data_url = 'https://mtgjson.com/api/v5/AllPrintings.json'
        file = '/media/VMShare/AllPrintings20221101.json'
        setupDB(data_url,file,cls.dbName)        

    @classmethod
    def __MakeSub(cls, reset=False):
        connection = create_server_connection('localhost', MtgDbHelper.user, MtgDbHelper.pw)
        if reset:
            showDatabases(connection)
            remove_database(connection, MtgDbHelper.subDbName)
            showDatabases(connection)
        dbExists = dbExist(connection, MtgDbHelper.subDbName)
        if not dbExists:
            create_database(connection, MtgDbHelper.subDbName)
            newCols = '(name text, manacost text, manavalue text, loyalty text, types text, subtypes text, text text, multiverseId text, availability text, side text)'
            showTables(connection, MtgDbHelper.subDbName)
            autoCommit(connection, 'ON')
            createTable(connection, MtgDbHelper.subDbName, 'cards', newCols)
            showTables(connection, MtgDbHelper.subDbName)
            showTable(connection, MtgDbHelper.subDbName, 'cards')
            
            oldCols = 'name, manacost, manavalue, loyalty, types, subtypes, text, multiverseId, availability, side'
            validCards = """(
                (availability LIKE '%paper%')
                AND (not types = 'Plane') 
                AND (not types = 'Scheme') 
                and (not types = 'Phenomenon')
                and (not types = 'Conspiracy')
                and (not types like '%Summon%') 
                and (not types = 'Eaturecray')
                and (not subtypes = 'Contraption') 
                and (not types = 'Vanguard')
                and (not multiverseId = '0')
            )"""
            isDragon="""(       
                (types LIKE '%Creature%' AND subtypes LIKE '%Dragon%')
                OR (types = 'Planeswalker' AND subtypes = 'Bolas')
                OR (types = 'Planeswalker' AND subtypes = 'Ugin')
                OR (types = 'Planeswalker' AND subtypes = 'Bahamut')
                OR (types not LIKE '%Creature%' AND text LIKE '%Dragon%creature token%')
            )""" # planeswalker exceptions based on game lore
            isSympathizer="""(
                (
                    (types LIKE '%Creature%') 
                    AND (  
                        (text LIKE '%dragon spells%') 
                        OR (text LIKE '%becomes%dragon%') 
                        OR (text LIKE '%Dragon%creature token%')
                    )
                )
                OR (types = 'Planeswalker' AND subtypes = 'Sarkhan')
                OR (types = 'Planeswalker' AND text LIKE '%dragon%')
                OR (name = 'Kargan Dragonlord')
                OR (name = 'Sylvia Brightspear')
                OR (name = 'Garth One-Eye')
            )"""# become, make, or enable casting
            isChangeling="""(
                (
                    (types LIKE '%Creature%') 
                    AND (  
                        (text LIKE '%is every creature type%')
                        OR (text LIKE '%Changeling%')
                    )
                )
                OR (
                    (text LIKE '%creature token%')
                    AND (text LIKE '%Changeling%')
                )
                OR (name = 'Reaper King') 
            )""" #(is or makes) changeling creature 
            #with Reaper King via the userper exception
            #consider including the remaining changeling spells/artifacts
            nonTribal="""(  (   (not types LIKE '%Creature%')
                                and (
                                    (not text LIKE '%creature token%')
                                    or (text LIKE '%populate%')
                                )
                                and (not types = 'Planeswalker') 
                            )
                            OR (name = 'Dwarven Mine')
                            OR (name = 'Forbidden Orchard')
                            OR (name = 'Supply // Demand')
                            OR (name = "Oketra's Monument")
                        )"""# non-"creature" cards and some exceptional creature cards
            rows = validCards + \
            " AND (" + isDragon + " OR " + isSympathizer + " OR " +isChangeling+ " OR " +nonTribal+ ")" 
            # TODO make an exclude list; add anything with name including dragon, then exclude things like dragonfly;
            # this will make importing new cards to include cards I may miss until they are manually excluded
            # may need to watch oracle text for creating tokens
            # todo consider altering names betwee dbs; right now they need to match
            moveDatabaseInfoWithSubSelect(connection,
                                          MtgDbHelper.dbName + '.cards',
                                          rows,
                                          oldCols,
                                          MtgDbHelper.subDbName + '.cards',
                                          oldCols,
                                          'name',
                                          'multiverseId')
            AddCol(connection, MtgDbHelper.subDbName, 'cards',"isDragon",isDragon)
            AddCol(connection, MtgDbHelper.subDbName, 'cards',"isSympathizer",isSympathizer)
            AddCol(connection, MtgDbHelper.subDbName, 'cards',"isChangeling",isChangeling)
            showTable(connection, MtgDbHelper.subDbName, 'cards')
            autoCommit(connection, 'OFF')
            # doNotThrashTheDisk(connection, 2 ** 29)
            # todo consider adding timestamp to name : db file backups are not too common and can easily be out-dated
            # db in current form lacks primary key;
            # may want to add decks as seperate tables
            p = subprocess.Popen(
                ['mysqldump -u' + MtgDbHelper.user + ' -p' + MtgDbHelper.pw + ' '
                 + MtgDbHelper.subDbName + ' > /media/VMShare/' + MtgDbHelper.subDbName + '.sql'],
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.readlines():
                print(line)
            err = p.wait()
            if err:
                print('failed import2 with ' + str(err))
            # p = subprocess.Popen(
            #     ['cp /dev/shm/' + MtgDbHelper.subDbName + '.sql /media/VMShare/' + MtgDbHelper.subDbName + '.sql'],
            #     shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # for line in p.stdout.readlines():
            #     print(line)
            # err = p.wait()
            # if err:
            #     print('failed copy2 with ' + str(err))
            showDatabases(connection)
        return connection
        # return connection #debating to pass this around...skippin since half the work is at the mysql level

    @classmethod
    def __MakeCardSet(cls):
        connection = create_server_connection('localhost', MtgDbHelper.user, MtgDbHelper.pw)
        # cols = ['name', 'manacost', 'manavalue', 'loyalty', 'types', 'subtypes', 'text', 'multiverseid', 'availability', 'side']
        table = parseDbTable(connection, MtgDbHelper.subDbName, 'cards')
        cards = []
        for row in table:
            if not row[7] == '0':
                card = Card(name=row[0],
                            manacost=row[1],
                            manavalue=row[2],
                            loyalty=row[3],
                            types=row[4],
                            subtypes=row[5],
                            text=row[6],
                            multiverseid=row[7],
                            side=row[9],
                            isTribal=row[10],
                            isNearTribal=row[11],
                            isChangeling=row[12])
                cards = cards + [card]
            else:
                print('throwing out '+row[0])
        MtgDbHelper.cards = CardSet(cards)
        MtgDbHelper.cards.mergeTransforms()

    @classmethod
    def initDb(cls, reset):
        """
        (if needed OR reset) reads from file & save full database
        (if needed OR reset) generates & save simplified database
        reads simplified database and maps simplified database into CardSet
        :rtype: CardSet
        """
        # raise ValueError("db setup not implemented")
        if(reset):
            MtgDbHelper.__MakeFull()
        MtgDbHelper.__MakeSub(reset)
        MtgDbHelper.__MakeCardSet()

    cards = None

    @classmethod
    def reset(cls):
        cls.initDb(True)


if __name__ == '__main__':
    helper=MtgDbHelper()
    helper.initDb(True)


