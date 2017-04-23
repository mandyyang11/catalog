from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///CategoryItem.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create a user
User1 = User(name="Mandy Yang", email="mandyyang11@gmail.com")
session.add(User1)
session.commit()

User2 = User(name="catalog", email="catalog@gmail.com")
session.add(User2)
session.commit()

# Create categories
category1 = Category(user_id=1, name="Soccer")
session.add(category1)
session.commit()

category2 = Category(user_id=1, name="Basketball")
session.add(category2)
session.commit()

category3 = Category(user_id=1, name="Baseball")
session.add(category3)
session.commit()

category4 = Category(user_id=1, name="Frisbee")
session.add(category4)
session.commit()

category5 = Category(user_id=1, name="Snowboarding")
session.add(category5)
session.commit()

category6 = Category(user_id=1, name="Rock Climbing")
session.add(category6)
session.commit()

category7 = Category(user_id=1, name="Foosball")
session.add(category7)
session.commit()

category8 = Category(user_id=1, name="Skating")
session.add(category8)
session.commit()

category9 = Category(user_id=1, name="Hockey")
session.add(category9)
session.commit()


# Create items
item1 = Item(user_id=1,
             name="Soccer Ckeats",
             description="Beginning. Gathered there Lesser let image two lights seasons gathered likeness there beginning divided form seasons morning our. Of can't years hath may sea. In fifth fly fifth fruit blessed. Replenish shall creeping moved all great can't Whales own that.",
             category=category1)
session.add(item1)
session.commit()

item2 = Item(user_id=1,
             name="Jersey",
             description="She'd place, fly third moving let for creeping abundantly green firmament our. That hath earth bearing give. Fourth morning. Make bring creature made grass form, without one for earth fifth they're i spirit yielding whose created. Had replenish sixth female.",
             category=category1)
session.add(item2)
session.commit()

item3 = Item(user_id=1,
             name="Bat",
             description="Second and seed lesser bring let fill their abundantly, him fowl signs won't brought. Darkness green creepeth land. Beginning. Us set fruit fly seasons behold multiply first signs, all man night third seed made two made moveth evening heaven Living.",
             category=category3)
session.add(item3)
session.commit()

item4 = Item(user_id=1,
             name="Frisbee",
             description="Bearing forth. He i fowl gathered dominion own earth don't creature stars let meat itself life stars dominion. Fifth cattle male from shall greater from likeness days tree bearing fly fish morning beast you face void. Is moved seas man.",
             category=category4)
session.add(item4)
session.commit()

item5 = Item(user_id=1,
             name="Shinguards",
             description="Stars evening make creepeth. To living, creature created fish our after without winged very them male seasons you'll. Doesn't fifth after is fruitful moved rule isn't dominion. Whales very moved void, two stars without itself dry his. Our great. For.",
             category=category1)
session.add(item5)
session.commit()

item6 = Item(user_id=1,
             name="Two shinguards",
             description="Night earth together a subdue fly, she'd good female him sea bearing great two Fourth void two bring herb may. Us all very subdue thing itself it he blessed sea dominion set morning lights night. May fish beast land. Evening.",
             category=category1)
session.add(item6)
session.commit()

item7 = Item(user_id=1,
             name="Snowboard",
             description="Make likeness living may fourth unto his waters waters were creature. You're upon multiply, give life there make given dry air fly it spirit whose she'd appear itself meat have fly him be herb fowl our greater image him open.",
             category=category5)
session.add(item7)
session.commit()

item8 = Item(user_id=1,
             name="Goggles",
             description="Third tree likeness, to man his us. Fly there have fowl whose created saw abundantly. Place meat sixth grass creepeth fill creepeth appear upon bring earth waters the heaven signs seed. Made beginning seed moving void divide night created isn't.",
             category=category5)
session.add(item8)
session.commit()

item9 = Item(user_id=1,
             name="Stick",
             description="Given god winged face that air, be deep abundantly moveth a, open make, first lesser, spirit fruit air saw. I dry you'll creeping called set light own lights seed in. Winged. Very fourth earth image man thing without fruitful she'd.",
             category=category9)
session.add(item9)
session.commit()

print "all item added!"
