"""Episode scripts for the four Wonder Pebbles series (ages 2-5).

Each episode is a list of segments. A segment is narrated by Pebble and
shown with a layout from render.py. Repetition, call-and-response pauses
and simple quizzes are deliberate: they are what helps toddlers learn.
"""
import random

CHANNEL = "Wonder Pebbles"

NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
PLURAL = {"strawberry": "strawberries", "butterfly": "butterflies", "fish": "fish",
          "ice cream": "ice creams", "cupcake": "cupcakes", "bee": "bees", "grapes": "bunches of grapes"}

COUNT_ITEMS = ["apple", "star", "balloon", "fish", "duck", "flower", "ball", "butterfly", "car",
               "strawberry", "cupcake", "bee", "heart", "leaf", "kite", "cookie", "frog", "orange"]

COLORS = [
    ("red", (235, 64, 64), ["apple", "strawberry", "heart", "car", "balloon"]),
    ("blue", (64, 140, 240), ["ball", "fish", "balloon", "raindrop", "heart"]),
    ("yellow", (255, 205, 40), ["star", "sun", "lemon", "duck", "banana"]),
    ("green", (80, 185, 90), ["leaf", "frog", "tree", "pear", "caterpillar"]),
    ("orange", (255, 140, 40), ["orange", "fish", "balloon", "cat", "heart"]),
    ("purple", (150, 90, 220), ["grapes", "umbrella", "balloon", "heart", "flower"]),
    ("pink", (250, 120, 180), ["flower", "balloon", "heart", "ice cream", "cupcake"]),
    ("brown", (150, 100, 60), ["cookie", "nest", "seed", "cocoon", "volcano"]),
]
# icons whose colour can be tinted
TINTABLE = {"apple", "balloon", "fish", "flower", "heart", "leaf", "raindrop", "star"}

SHAPE_LIST = [
    ("circle", "A circle is round, round, round. It has no corners at all!", ["ball", "orange", "cookie"]),
    ("square", "A square has four sides, and all the sides are the same size.", ["quilt"]),
    ("triangle", "A triangle has three sides and three pointy corners.", ["volcano"]),
    ("rectangle", "A rectangle has four sides. Two sides are long, and two sides are short.", ["xylophone"]),
    ("star", "A star has five pointy points. Twinkle, twinkle!", ["star"]),
    ("heart", "A heart is a shape that means love!", ["heart"]),
    ("oval", "An oval is like a stretched circle. It looks like an egg!", ["egg", "lemon"]),
    ("diamond", "A diamond has four sides. It looks like a kite!", ["kite"]),
    ("pentagon", "A pentagon has five sides and five corners.", []),
    ("hexagon", "A hexagon has six sides. Bees make hexagons in their honeycomb!", ["bee"]),
]
SIDES = {"square": 4, "triangle": 3, "rectangle": 4, "diamond": 4, "pentagon": 5, "hexagon": 6}

ABC = {
    "A": "apple", "B": "ball", "C": "cat", "D": "duck", "E": "egg", "F": "fish", "G": "grapes",
    "H": "house", "I": "ice cream", "J": "jellyfish", "K": "kite", "L": "leaf", "M": "moon",
    "N": "nest", "O": "orange", "P": "pear", "Q": "quilt", "R": "rainbow", "S": "sun", "T": "tree",
    "U": "umbrella", "V": "volcano", "W": "watermelon", "X": "xylophone", "Y": "yo-yo", "Z": "zebra",
}
ABC_EXTRA = {"B": "balloon", "C": "car", "F": "frog", "S": "star", "C2": "cookie", "B2": "bee",
             "R": "rocket", "L": "lemon", "M": "moon", "H": "heart", "T": "tadpole", "W": "waves"}

SCIENCE = [
    {"topic": "The Sun", "slug": "sun", "thumb": "sun", "lines": [
        ("The sun is a star! It is the closest star to us.", ["sun", "star"], "row"),
        ("The sun is very, very big, and very, very hot.", ["sun"], "row"),
        ("The sun gives us light, so we can see in the daytime.", ["sun", "house"], "row"),
        ("The sun keeps us warm.", ["sun", "earth"], "row"),
        ("Plants need sunlight to grow big and tall.", ["sun", "sprout", "flower"], "seq"),
        ("Remember: never look right at the sun. It can hurt your eyes!", ["sun"], "row"),
    ], "quiz": ("What gives us light in the daytime?", "sun", ["moon", "sun", "cloud"])},
    {"topic": "Rain", "slug": "rain", "thumb": "raindrop", "lines": [
        ("Clouds are made of tiny, tiny drops of water.", ["cloud", "raindrop"], "row"),
        ("When the drops get big and heavy, they fall down.", ["cloud", "raindrop"], "seq"),
        ("That is rain! Pitter, patter, pitter, patter!", ["raindrop", "raindrop", "raindrop"], "row"),
        ("Rain gives water to plants and trees.", ["raindrop", "tree"], "seq"),
        ("Rain fills up rivers, lakes, and the sea.", ["raindrop", "waves"], "seq"),
        ("When it rains, we can use an umbrella!", ["umbrella"], "row"),
    ], "quiz": ("What falls from the clouds?", "raindrop", ["raindrop", "apple", "car"])},
    {"topic": "Rainbows", "slug": "rainbow", "thumb": "rainbow", "lines": [
        ("Have you ever seen a rainbow in the sky?", ["rainbow"], "row"),
        ("Rainbows happen when sunshine shines through raindrops.", ["sun", "raindrop", "rainbow"], "seq"),
        ("A rainbow has many colors.", ["rainbow"], "row"),
        ("Red, orange, yellow, green, blue, and purple!", ["rainbow"], "row"),
        ("Look for a rainbow when the sun comes out after the rain!", ["sun", "rainbow"], "row"),
    ], "quiz": ("What do we need to make a rainbow?", "sun", ["sun", "cookie", "car"])},
    {"topic": "How Plants Grow", "slug": "plants", "thumb": "sprout", "lines": [
        ("A plant starts as a tiny seed.", ["seed"], "row"),
        ("We put the seed in the soil, and give it water.", ["seed", "raindrop"], "row"),
        ("The sun shines, and a little sprout pops up!", ["sun", "sprout"], "row"),
        ("The sprout grows and grows.", ["sprout"], "row"),
        ("And then, it becomes a beautiful flower!", ["seed", "sprout", "flower"], "seq"),
        ("Plants need water, sunshine, and soil to grow.", ["raindrop", "sun", "sprout"], "row"),
    ], "quiz": ("What does a plant start as?", "seed", ["seed", "ball", "fish"])},
    {"topic": "Butterflies", "slug": "butterfly", "thumb": "butterfly", "lines": [
        ("A butterfly starts as a tiny egg on a leaf.", ["egg", "leaf"], "row"),
        ("Out comes a hungry little caterpillar! Munch, munch, munch!", ["caterpillar", "leaf"], "row"),
        ("The caterpillar makes a cozy cocoon.", ["caterpillar", "cocoon"], "seq"),
        ("Inside, it changes, and changes.", ["cocoon"], "row"),
        ("Then, out comes a beautiful butterfly!", ["cocoon", "butterfly"], "seq"),
        ("Egg, caterpillar, cocoon, butterfly!", ["egg", "caterpillar", "cocoon", "butterfly"], "seq"),
    ], "quiz": ("What does a caterpillar turn into?", "butterfly", ["fish", "butterfly", "duck"])},
    {"topic": "Day and Night", "slug": "day-night", "thumb": "moon", "lines": [
        ("In the daytime, the sun is up in the sky.", ["sun", "house"], "row"),
        ("Our Earth spins around, and around, like a slow, slow top.", ["earth"], "row"),
        ("When our side turns away from the sun, it becomes night.", ["sun", "earth", "moon"], "seq"),
        ("At night, we can see the moon and the stars.", ["moon", "star", "star"], "row"),
        ("Night time is sleepy time. Good night!", ["moon"], "row"),
    ], "quiz": ("What can we see in the sky at night?", "moon", ["sun", "moon", "rainbow"])},
    {"topic": "Bees and Flowers", "slug": "bees", "thumb": "bee", "lines": [
        ("Buzz, buzz! This is a bee.", ["bee"], "row"),
        ("Bees fly from flower to flower.", ["bee", "flower", "flower"], "row"),
        ("Bees drink sweet nectar from flowers.", ["bee", "flower"], "row"),
        ("Bees help flowers make seeds, so new flowers can grow.", ["bee", "flower", "seed"], "seq"),
        ("Bees are our helpers! We say thank you, bees!", ["bee", "heart"], "row"),
    ], "quiz": ("Which one says buzz, buzz?", "bee", ["frog", "bee", "duck"])},
    {"topic": "Frogs", "slug": "frogs", "thumb": "frog", "lines": [
        ("Ribbit, ribbit! This is a frog.", ["frog"], "row"),
        ("A frog starts as a tiny egg in the water.", ["egg", "waves"], "row"),
        ("Out comes a tadpole! It swims with its little tail.", ["tadpole", "waves"], "row"),
        ("The tadpole grows legs, and its tail gets smaller.", ["tadpole", "frog"], "seq"),
        ("Now it is a frog! Hop, hop, hop!", ["egg", "tadpole", "frog"], "seq"),
    ], "quiz": ("What does a tadpole grow into?", "frog", ["frog", "bee", "cat"])},
    {"topic": "Snow", "slug": "snow", "thumb": "snowflake", "lines": [
        ("When it is very, very cold, clouds make snow!", ["cloud", "snowflake"], "seq"),
        ("Snow falls down as tiny snowflakes.", ["snowflake", "snowflake", "snowflake"], "row"),
        ("Every snowflake has six sides.", ["snowflake"], "row"),
        ("Snow is made of frozen water.", ["raindrop", "snowflake"], "seq"),
        ("When it gets warm, snow melts back into water!", ["snowflake", "sun", "raindrop"], "seq"),
    ], "quiz": ("What falls from the clouds when it is very cold?", "snowflake", ["snowflake", "apple", "kite"])},
    {"topic": "The Moon", "slug": "moon", "thumb": "moon", "lines": [
        ("Look up at night. Can you see the moon?", ["moon"], "row"),
        ("The moon goes around and around our Earth.", ["earth", "moon"], "row"),
        ("The moon does not make its own light.", ["moon"], "row"),
        ("Sunlight bounces off the moon, so it shines!", ["sun", "moon"], "seq"),
        ("Astronauts flew in a rocket all the way to the moon!", ["rocket", "moon"], "seq"),
    ], "quiz": ("Which one flies to the moon?", "rocket", ["car", "rocket", "fish"])},
    {"topic": "Our Planet Earth", "slug": "earth", "thumb": "earth", "lines": [
        ("This is our home. It is called Earth!", ["earth"], "row"),
        ("Earth is a planet. It is round like a ball.", ["earth", "ball"], "row"),
        ("Earth has lots of water. That is the blue part!", ["earth", "waves"], "row"),
        ("Earth has land, with trees, and flowers, and animals.", ["tree", "flower", "frog"], "row"),
        ("Let's take good care of our Earth!", ["earth", "heart"], "row"),
    ], "quiz": ("What is the name of our planet?", "earth", ["moon", "earth", "sun"])},
    {"topic": "Fish", "slug": "fish", "thumb": "fish", "lines": [
        ("Splash! Fish live in the water.", ["fish", "waves"], "row"),
        ("Fish swim using their fins and tails.", ["fish"], "row"),
        ("Fish breathe underwater with gills.", ["fish", "waves"], "row"),
        ("Some fish are big, and some fish are small.", ["fish", "fish"], "row"),
        ("Let's swim like a fish! Swish, swish, swish!", ["fish", "fish", "fish"], "row"),
    ], "quiz": ("Which one lives in the water?", "fish", ["cat", "fish", "bee"])},
]

INTROS = [
    "Hi friends! I'm Pebble! Welcome to Wonder Pebbles!",
    "Hello, hello! It's me, Pebble! Are you ready to learn?",
    "Hi there, friends! Pebble here! Let's have some fun!",
]
PRAISE = ["Great job!", "You did it!", "Wonderful!", "Super!", "Well done!", "Yay! You're so smart!"]
OUTROS = [
    "That was so much fun! See you next time, friends! Bye bye!",
    "You learned so much today! Bye bye, friends! See you soon!",
    "Thank you for learning with me! Bye bye!",
]


def S(text, layout, pause=0.6, **params):
    return {"text": text, "layout": layout, "pause": pause, "params": params}


def plural(name, n):
    if n == 1:
        return name
    return PLURAL.get(name, name + "s")


# -------------------------------------------------------------- series builders
def numbers_episode(k, rng):
    n = [5, 3, 7, 4, 10, 6, 8, 9, 5, 10][k % 10]
    item = COUNT_ITEMS[(k * 7) % len(COUNT_ITEMS)]
    pl = plural(item, n)
    segs = [
        S(rng.choice(INTROS), "title", 0.4, title=f"Count {n} {pl.title()}", icon=item),
        S(f"Today, let's count {pl}! Count with me!", "count", 0.3, item=item, n=n, shown=0),
    ]
    for i in range(1, n + 1):
        segs.append(S(f"{NUMBER_WORDS[i].capitalize()}!", "count", 0.55, item=item, n=n, shown=i,
                      pop=True, highlight=i))
    segs.append(S(f"{NUMBER_WORDS[n].capitalize()} {pl}! Let's count them again, a little faster!",
                  "count", 0.4, item=item, n=n, shown=n))
    for i in range(1, n + 1):
        segs.append(S(f"{NUMBER_WORDS[i].capitalize()}!", "count", 0.15, item=item, n=n, shown=n, highlight=i))
    segs.append(S(rng.choice(PRAISE), "count", 0.4, item=item, n=n, shown=n, cheer=True))
    # quiz: smaller number
    q = rng.randint(2, max(2, min(n - 1, 5)))
    segs.append(S(f"Now, how many {plural(item, q)} can you see?", "count", 3.0, item=item, n=q, shown=q,
                  question=True))
    segs.append(S(f"{NUMBER_WORDS[q].capitalize()}! There are {NUMBER_WORDS[q]} {plural(item, q)}! {rng.choice(PRAISE)}",
                  "count", 0.5, item=item, n=q, shown=q, reveal=q, cheer=True))
    # fingers / numerals review
    segs.append(S(f"Let's say the numbers together! Hold up your fingers!", "numerals", 0.3, n=n, highlight=0))
    for i in range(1, n + 1):
        segs.append(S(f"{NUMBER_WORDS[i].capitalize()}!", "numerals", 0.2, n=n, highlight=i))
    segs.append(S(rng.choice(OUTROS), "outro", 1.2, icon=item))
    title = f"Let's Count {n} {pl.title()}! | Counting 1 to {n} for Toddlers | {CHANNEL}"
    desc = (f"Count from 1 to {n} with Pebble and {NUMBER_WORDS[n]} {pl}! "
            "Toddlers and preschoolers practise number words, one-to-one counting and recognising numerals, "
            "with repetition and a little quiz.")
    tags = ["counting for kids", "learn numbers", "123", f"count to {n}", "toddler learning", "preschool"]
    return dict(series="numbers", title=title, desc=desc, tags=tags, thumb=dict(icon=item, text=f"1-{n}"),
                hue=(255, 236, 200), segs=segs)


def colors_episode(k, rng):
    name, rgb, objs = COLORS[(k // 2) % len(COLORS)]
    segs = [S(rng.choice(INTROS), "title", 0.4, title=f"The Color {name.title()}", icon="flower" if name != "brown" else "cookie", color=rgb)]
    segs.append(S(f"Today's color is... {name}!", "color_splash", 0.6, color=rgb, word=name))
    segs.append(S(f"Can you say {name}? {name.capitalize()}!", "color_splash", 2.0, color=rgb, word=name, prompt=True))
    for o in objs[:4]:
        tint = rgb if o in TINTABLE else None
        segs.append(S(f"A {name} {o}!", "object", 0.7, icon=o, tint=tint, word=f"{name} {o}", color=rgb))
    # quiz
    others = [c for c in COLORS if c[0] != name]
    choices = rng.sample(others, 2) + [(name, rgb, objs)]
    rng.shuffle(choices)
    q_icon = "balloon"
    opts = [dict(icon=q_icon, tint=c[1], label=c[0]) for c in choices]
    ans = [c[0] for c in choices].index(name)
    segs.append(S(f"Which balloon is {name}? Can you point to it?", "choose", 3.0, options=opts, answer=ans))
    segs.append(S(f"This one! The {name} balloon! {rng.choice(PRAISE)}", "choose", 0.6, options=opts, answer=ans, reveal=True))
    segs.append(S(f"Let's look around your room. Can you find something {name}?", "color_splash", 3.0, color=rgb, word=name, prompt=True))
    segs.append(S(f"{rng.choice(PRAISE)} {name.capitalize()}, {name}, {name}!", "color_splash", 0.6, color=rgb, word=name))
    segs.append(S(rng.choice(OUTROS), "outro", 1.2, icon="balloon", tint=rgb))
    title = f"Learn the Color {name.title()}! | Colors for Toddlers | {CHANNEL}"
    desc = (f"Learn the color {name} with Pebble! Toddlers name {name} things, play a find-the-color game "
            "and look for the color at home.")
    tags = ["learn colors", f"color {name}", "colors for toddlers", "preschool learning", "kids colors"]
    return dict(series="colors", title=title, desc=desc, tags=tags,
                thumb=dict(icon="balloon", tint=rgb, text=name.title()), hue=tuple(min(255, int(c * 0.25 + 200)) for c in rgb), segs=segs)


def shapes_episode(k, rng):
    name, fact, examples = SHAPE_LIST[(k // 2) % len(SHAPE_LIST)]
    col = rng.choice([(255, 150, 60), (90, 170, 250), (250, 110, 160), (110, 200, 120), (160, 120, 240)])
    an = "an" if name[0] in "aeiou" else "a"
    segs = [S(rng.choice(INTROS), "title", 0.4, title=f"The {name.title()} Shape", shape=name, color=col)]
    segs.append(S(f"Today's shape is {an} {name}!", "shape", 0.6, shape=name, color=col, word=name))
    segs.append(S(f"Can you say {name}? {name.capitalize()}!", "shape", 2.0, shape=name, color=col, word=name))
    segs.append(S(fact, "shape", 0.6, shape=name, color=col, word=name))
    if name in SIDES:
        segs.append(S(f"Let's count the sides!", "shape", 0.2, shape=name, color=col, word=name))
        for i in range(SIDES[name]):
            segs.append(S(f"{NUMBER_WORDS[i + 1].capitalize()}!", "shape", 0.25, shape=name, color=col,
                          word=name, side=i, side_count=i + 1))
        segs.append(S(f"{NUMBER_WORDS[SIDES[name]].capitalize()} sides! {rng.choice(PRAISE)}", "shape", 0.4,
                      shape=name, color=col, word=name, side_count=SIDES[name]))
    for e in examples[:2]:
        segs.append(S(f"{an.capitalize()} {name} looks like {'an' if e[0] in 'aeiou' else 'a'} {e}!", "shape_vs", 0.6,
                      shape=name, color=col, icon=e))
    pool = [s[0] for s in SHAPE_LIST if s[0] != name]
    choices = rng.sample(pool, 2) + [name]
    rng.shuffle(choices)
    cols = [(255, 150, 60), (90, 170, 250), (250, 110, 160)]
    opts = [dict(shape=c, tint=cols[i], label=c) for i, c in enumerate(choices)]
    ans = choices.index(name)
    segs.append(S(f"Can you find the {name}?", "choose", 3.0, options=opts, answer=ans))
    segs.append(S(f"There it is! {rng.choice(PRAISE)}", "choose", 0.6, options=opts, answer=ans, reveal=True))
    segs.append(S(f"Let's draw {an} {name} in the air with your finger!", "shape", 3.0, shape=name, color=col, word=name, trace=True))
    segs.append(S(rng.choice(OUTROS), "outro", 1.2, shape=name, color=col))
    title = f"Learn Shapes: The {name.title()}! | Shapes for Toddlers | {CHANNEL}"
    desc = f"Learn the {name} shape with Pebble! Count its sides, find it among other shapes and draw it in the air."
    tags = ["learn shapes", f"{name} shape", "shapes for kids", "preschool", "toddler learning"]
    return dict(series="shapes", title=title, desc=desc, tags=tags,
                thumb=dict(shape=name, color=col, text=name.title()), hue=(225, 238, 255), segs=segs)


def abc_episode(k, rng):
    L = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[k % 26]
    word = ABC[L]
    extra = ABC_EXTRA.get(L)
    segs = [S(rng.choice(INTROS), "title", 0.4, title=f"Letter {L}", letter=L)]
    segs.append(S(f"Today's letter is... {L}!", "letter", 0.6, letter=L, case="both"))
    segs.append(S(f"This is a big {L}.", "letter", 0.4, letter=L, case="upper"))
    segs.append(S(f"And this is a little {L}.", "letter", 0.4, letter=L, case="lower"))
    segs.append(S(f"Can you say {L}? {L}!", "letter", 2.0, letter=L, case="both"))
    segs.append(S(f"{L} is for {word}!", "word", 0.7, letter=L, icon=word, word=word))
    segs.append(S(f"{word.capitalize()}! Can you say {word}?", "word", 2.0, letter=L, icon=word, word=word))
    if extra and extra != word:
        segs.append(S(f"{L} is also for {extra}!", "word", 0.7, letter=L, icon=extra, word=extra))
    segs.append(S(f"Let's draw the letter {L} in the air with your finger!", "letter", 3.5, letter=L, case="upper", trace=True))
    pool = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c != L]
    choices = rng.sample(pool, 2) + [L]
    rng.shuffle(choices)
    cols = [(255, 150, 60), (90, 170, 250), (250, 110, 160)]
    opts = [dict(letter=c, tint=cols[i], label=c) for i, c in enumerate(choices)]
    ans = choices.index(L)
    segs.append(S(f"Can you find the letter {L}?", "choose", 3.0, options=opts, answer=ans))
    segs.append(S(f"Here it is! {L}! {rng.choice(PRAISE)}", "choose", 0.6, options=opts, answer=ans, reveal=True))
    segs.append(S(f"{L}, {L}, {word}! {L}, {L}, {word}!", "word", 0.5, letter=L, icon=word, word=word))
    segs.append(S(rng.choice(OUTROS), "outro", 1.2, letter=L))
    title = f"Letter {L} | {L} is for {word.title()}! | ABC for Toddlers | {CHANNEL}"
    desc = (f"Learn the letter {L} with Pebble! See big {L} and little {L.lower()}, learn that {L} is for {word}, "
            "trace the letter in the air and play a find-the-letter game.")
    tags = ["abc", "alphabet for kids", f"letter {L}", "phonics", "toddler learning", "preschool"]
    return dict(series="abc", title=title, desc=desc, tags=tags,
                thumb=dict(letter=L, icon=word, text=f"{L} is for {word.title()}"), hue=(255, 226, 236), segs=segs)


def science_episode(k, rng):
    t = SCIENCE[k % len(SCIENCE)]
    segs = [S(rng.choice(INTROS), "title", 0.4, title=t["topic"], icon=t["thumb"])]
    segs.append(S(f"Today, let's learn about... {t['topic'].lower()}!", "fact", 0.6, icons=[t["thumb"]], mode="row"))
    for text, icons, mode in t["lines"]:
        segs.append(S(text, "fact", 0.8, icons=icons, mode=mode))
    q, a, choices = t["quiz"]
    choices = list(choices)
    rng.shuffle(choices)
    opts = [dict(icon=c, label=c) for c in choices]
    ans = choices.index(a)
    segs.append(S(f"Quiz time! {q}", "choose", 3.0, options=opts, answer=ans))
    segs.append(S(f"The {a}! {rng.choice(PRAISE)}", "choose", 0.6, options=opts, answer=ans, reveal=True))
    segs.append(S(rng.choice(OUTROS), "outro", 1.2, icon=t["thumb"]))
    title = f"{t['topic']} for Kids! | Science for Toddlers | {CHANNEL}"
    desc = f"Pebble explains {t['topic'].lower()} in simple words for curious toddlers and preschoolers, with a little quiz at the end."
    tags = ["science for kids", t["topic"].lower(), "preschool science", "toddler learning", "nature for kids"]
    return dict(series="science", title=title, desc=desc, tags=tags,
                thumb=dict(icon=t["thumb"], text=t["topic"]), hue=(214, 240, 226), segs=segs)


def build_episode(episode_number):
    """Rotate series daily: numbers, colors/shapes, ABC, science."""
    rng = random.Random(episode_number * 7919)
    series_idx = episode_number % 4
    k = episode_number // 4
    if series_idx == 0:
        ep = numbers_episode(k, rng)
    elif series_idx == 1:
        ep = colors_episode(k, rng) if k % 2 == 0 else shapes_episode(k, rng)
    elif series_idx == 2:
        ep = abc_episode(k, rng)
    else:
        ep = science_episode(k, rng)
    ep["episode"] = episode_number
    ep["seed"] = episode_number * 7919
    return ep
