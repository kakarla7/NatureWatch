"""
NatureWatch — Master Wildlife List
Definitive list of viewable US wildlife species.
Add/remove animals here — the refresh script uses this as source of truth.
Every refresh generates data for exactly these animals, nothing more, nothing less.
"""

MASTER_LIST = {

    "Mammal": [
        # Bears
        "Grizzly Bear",
        "American Black Bear",
        "Polar Bear",
        # Wolves & Canids
        "Gray Wolf",
        "Red Wolf",
        "Coyote",
        "Arctic Fox",
        "Red Fox",
        "Swift Fox",
        # Big Cats
        "Mountain Lion",
        "Florida Panther",
        "Bobcat",
        "Canada Lynx",
        "Ocelot",
        # Deer & Ungulates
        "Rocky Mountain Elk",
        "Moose",
        "White-tailed Deer",
        "Mule Deer",
        "Caribou",
        "American Bison",
        "Pronghorn",
        "Dall Sheep",
        "Bighorn Sheep",
        "Desert Bighorn Sheep",
        "Mountain Goat",
        "Musk Ox",
        # Small Mammals
        "Wolverine",
        "American Badger",
        "North American River Otter",
        "American Beaver",
        "North American Porcupine",
        "Virginia Opossum",
        "Nine-banded Armadillo",
        "Black-tailed Prairie Dog",
        "American Pika",
        "Snowshoe Hare",
        "Black-tailed Jackrabbit",
        # Bats
        "Mexican Free-tailed Bat",
        "Indiana Bat",
        # Primates (none native, but notable)
        # Mustelids
        "American Mink",
        "Striped Skunk",
        "Black-footed Ferret",
        "Sea Otter",
        # Seals (coastal/marine but not fully marine)
        "Northern Elephant Seal",
        "Harbor Seal",
        "Steller Sea Lion",
        "California Sea Lion",
        "Walrus",
    ],

    "Marine Mammal": [
        # Whales
        "Humpback Whale",
        "Blue Whale",
        "Gray Whale",
        "Orca",
        "Sperm Whale",
        "North Atlantic Right Whale",
        "Bowhead Whale",
        "Beluga Whale",
        "Narwhal",
        "Minke Whale",
        "Fin Whale",
        # Dolphins & Porpoises
        "Bottlenose Dolphin",
        "Pacific White-sided Dolphin",
        "Common Dolphin",
        "Harbor Porpoise",
        "Spinner Dolphin",
        # Manatees
        "West Indian Manatee",
    ],

    "Bird": [
        # Eagles & Hawks
        "Bald Eagle",
        "Golden Eagle",
        "Osprey",
        "Red-tailed Hawk",
        "Ferruginous Hawk",
        "Peregrine Falcon",
        "American Kestrel",
        # Large Birds
        "California Condor",
        "Turkey Vulture",
        "Wild Turkey",
        # Owls
        "Great Horned Owl",
        "Snowy Owl",
        "Great Gray Owl",
        "Barred Owl",
        "Burrowing Owl",
        # Waterbirds
        "Whooping Crane",
        "Sandhill Crane",
        "Great Blue Heron",
        "Great Egret",
        "Roseate Spoonbill",
        "American White Pelican",
        "Brown Pelican",
        "Wood Stork",
        "American Flamingo",
        # Waterfowl
        "Trumpeter Swan",
        "Tundra Swan",
        "Snow Goose",
        "Canada Goose",
        "Wood Duck",
        "Common Loon",
        "Atlantic Puffin",
        "Tufted Puffin",
        # Shorebirds & Songbirds
        "American Avocet",
        "Black Skimmer",
        "Painted Bunting",
        "Western Meadowlark",
        "Scissor-tailed Flycatcher",
        "Resplendent Quetzal",  # rare AZ
        "Elegant Trogon",
        # Woodpeckers
        "Pileated Woodpecker",
        "Ivory-billed Woodpecker",  # possibly extinct, notable
        # Hummingbirds
        "Ruby-throated Hummingbird",
        "Rufous Hummingbird",
        # Corvids
        "Common Raven",
        "Clark's Nutcracker",
        # Others
        "Roadrunner",
        "Atlantic Puffin",
        "Snowy Plover",
        "Piping Plover",
    ],

    "Reptile": [
        # Crocodilians
        "American Alligator",
        "American Crocodile",
        # Sea Turtles
        "Loggerhead Sea Turtle",
        "Green Sea Turtle",
        "Leatherback Sea Turtle",
        "Hawksbill Sea Turtle",
        "Kemp's Ridley Sea Turtle",
        # Land Turtles & Tortoises
        "Desert Tortoise",
        "Gopher Tortoise",
        "Eastern Box Turtle",
        "Alligator Snapping Turtle",
        # Lizards
        "Gila Monster",
        "Western Fence Lizard",
        "Green Iguana",
        "Horned Lizard",
        "Chuckwalla",
        "Komodo Dragon",  # only in zoos, remove
        "Collared Lizard",
        # Snakes
        "Eastern Diamondback Rattlesnake",
        "Western Diamondback Rattlesnake",
        "Timber Rattlesnake",
        "Eastern Indigo Snake",
        "Cottonmouth",
        "Coral Snake",
        "Bull Snake",
        "King Snake",
    ],

    "Amphibian": [
        "American Bullfrog",
        "Pacific Giant Salamander",
        "Hellbender",
        "Mudpuppy",
        "Red-backed Salamander",
        "Tiger Salamander",
        "California Red-legged Frog",
        "Wood Frog",
        "American Toad",
        "Spotted Salamander",
        "Axolotl",  # Mexican but notable for US enthusiasts
        "Spring Peeper",
    ],

    "Fish": [
        "Atlantic Salmon",
        "Chinook Salmon",
        "Sockeye Salmon",
        "Coho Salmon",
        "Steelhead Trout",
        "Lake Sturgeon",
        "White Sturgeon",
        "Paddlefish",
        "Alligator Gar",
        "Manta Ray",
        "Whale Shark",
        "Hammerhead Shark",
        "Great White Shark",
        "Bull Shark",
        "Coelacanth",  # not US, remove
        "Brook Trout",
        "Largemouth Bass",
    ],

    "Insect": [
        "Monarch Butterfly",
        "Eastern Tiger Swallowtail",
        "Painted Lady Butterfly",
        "Luna Moth",
        "Cecropia Moth",
        "American Bumble Bee",
        "Firefly (Eastern)",
        "Periodical Cicada",
        "Dragonfly (Common Green Darner)",
        "Praying Mantis",
        "Walking Stick",
        "Tarantula (Desert Blonde)",
        "Black Widow Spider",
        "American Horseshoe Crab",
        "Giant Water Bug",
    ],

    "Marine Life": [
        "Pacific Octopus",
        "Giant Pacific Octopus",
        "Bioluminescent Dinoflagellates",
        "Jellyfish (Moon)",
        "Dungeness Crab",
        "American Lobster",
        "Coral (Elkhorn)",
        "Coral (Brain)",
        "Sea Anemone",
        "Starfish (Sunflower Sea Star)",
        "Pacific Sea Nettle",
        "Mantis Shrimp",
    ],
}

# Flatten for easy counting
ALL_ANIMALS = []
for category, animals in MASTER_LIST.items():
    for name in animals:
        ALL_ANIMALS.append({"name": name, "category": category})

if __name__ == "__main__":
    print(f"Total animals: {len(ALL_ANIMALS)}")
    for cat, animals in MASTER_LIST.items():
        print(f"  {cat}: {len(animals)}")