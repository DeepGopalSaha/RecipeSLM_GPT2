import csv
import random

OUTPUT_FILE = "recipes_10000.csv"
NUM_SAMPLES = 10000


# =========================
# MAIN BASE TYPES
# =========================

PROTEINS = ["chicken","mutton","fish","paneer","egg"]
VEG_MAIN = [
    "potato","cauliflower","spinach","okra","brinjal",
    "mushroom","peas","beans","carrot","capsicum"
]

MAIN_BASE = ["protein","rice","flour","veg"]


# =========================
# STYLE BY BASE
# =========================

STYLE_BY_BASE = {
    "protein":["curry","dry_fry","tandoori"],
    "rice":["biryani","pulao"],
    "flour":["roti","paratha"],
    "veg":["curry","dry_fry"]
}


# =========================
# INGREDIENT POOLS
# =========================

INGREDIENTS_BY_STYLE = {

    "curry":[
        "oil","ghee","onion","tomato","garlic","ginger",
        "cream","yogurt","cashew paste",
        "peas","beans","carrot","capsicum","spinach",
        "cauliflower","potato","mushroom","brinjal","okra"
    ],

    "dry_fry":[
        "oil","onion","garlic","ginger","butter",
        "capsicum","beans","carrot","peas",
        "mushroom","cauliflower","potato","spinach"
    ],

    "tandoori":[
        "yogurt","garlic","ginger","lemon",
        "butter","cream","mint","coriander",
        "hung curd"
    ],

    "biryani":[
        "rice","ghee","onion","mint","coriander",
        "cashew","raisins","yogurt","peas","beans",
        "carrot","potato","mushroom","paneer","egg"
    ],

    "pulao":[
        "rice","ghee","peas","carrot","beans",
        "onion","cashew","mushroom","paneer",
        "potato","egg","capsicum"
    ],

    "roti":[
        "flour","water","salt","ghee",
        "oil","milk","curd"
    ],

    "paratha":[
        "flour","water","salt","ghee","oil","yogurt",
        "potato","paneer","spinach","cauliflower",
        "onion","peas","mushroom"
    ]
}

USED_SIGNATURES = set()


# =========================
# NAME GENERATOR
# =========================

def get_dominant_ing(ingredients):

    priority = PROTEINS + VEG_MAIN

    for p in priority:
        if p in ingredients:
            return p

    for i in ingredients:
        if i not in ["rice","flour","oil","ghee","water","salt"]:
            return i

    return "Veg"


def generate_name(main_ing, style, ingredients):

    dom = get_dominant_ing(ingredients).title()

    if style == "tandoori":
        return f"Tandoori {dom}"
    if style == "dry_fry":
        return f"{dom} Fry"

    if style == "curry":
        if dom == "Paneer":
            return random.choice(
                ["Paneer Butter Masala","Shahi Paneer","Malai Paneer"]
            )
        if dom == "Chicken":
            return random.choice(
                ["Butter Chicken","Afghani Chicken","Chicken Curry"]
            )
        return f"{dom} Curry"

    if style == "biryani":
        return f"{dom} Biryani"

    if style == "pulao":
        return f"{dom} Pulao"

    if style == "roti":
        return random.choice(["Roti","Chapati","Tandoori Roti"])

    if style == "paratha":
        if dom in ["Potato","Paneer","Spinach","Cauliflower","Onion"]:
            return f"{dom} Paratha"
        return "Paratha"

    return f"{dom} Dish"


# =========================
# STEP BUILDER (UNCHANGED)
# =========================

def build_steps(style, main_ing, ingredients):

    extra = [x for x in ingredients if x != main_ing]

    while len(extra) < 4:
        extra.append(extra[0])

    a, b, c, d = extra[:4]

    if style in ["roti", "paratha"]:
        return [
            f"Mix flour with {a} and {b} until evenly combined",
            f"Knead the mixture well until a soft smooth dough forms",
            f"Let the dough rest for some time so it becomes soft",
            f"Divide dough into small balls and roll into flat rounds",
            f"Cook each round on hot tawa using little {c}",
            f"Flip and cook until both sides develop light brown spots",
            f"Serve hot with {a} or yogurt"
        ]

    if style in ["biryani", "pulao"]:
        return [
            f"Heat ghee in a pot and sauté {a} until fragrant",
            f"Add {b} and cook gently until slightly soft",
            f"Mix rice with {main_ing} and stir carefully",
            f"Add {c} and cook briefly so flavors combine well",
            "Add spices according to your liking and mix evenly",
            f"Cover the pot and cook on low flame until rice is fluffy",
            f"Rest for few minutes before serving hot with {b}"
        ]

    if style == "tandoori":
        return [
            f"Marinate {main_ing} with {a}, {b} and {c} thoroughly",
            f"Coat the mixture well so {main_ing} absorbs all flavors",
            "Add spices according to your liking and mix again",
            f"Let the marinated {main_ing} rest for better flavor",
            f"Cook in oven or tandoor until edges become slightly charred",
            f"Brush with butter and roast briefly again",
            f"Serve hot with {a} and lemon"
        ]

    if style == "dry_fry":
        return [
            f"Heat oil in pan and sauté {a} until aromatic",
            f"Add {main_ing} and cook on medium heat until sealed",
            f"Add {b} and stir continuously so ingredients combine well",
            f"Mix in {c} and cook until moisture reduces",
            "Add spices according to your liking and toss evenly",
            f"Cook until dry and lightly crisp while stirring occasionally",
            f"Serve hot with {b} and {c}"
        ]

    return [
        f"Heat oil in pan and sauté {a} until slightly golden",
        f"Add {b} and cook until the mixture turns soft",
        f"Add {main_ing} with {c} and stir gently to coat",
        f"Cook the mixture until {main_ing} absorbs the flavors",
        "Add spices according to your liking and mix well",
        f"Simmer on low flame until the curry thickens nicely",
        f"Serve hot with rice or roti"
    ]


# =========================
# SAMPLE GENERATION
# =========================

def generate_sample():

    for _ in range(50):

        base = random.choice(MAIN_BASE)
        style = random.choice(STYLE_BY_BASE[base])

        if base == "protein":
            main_ing = random.choice(PROTEINS)
        elif base == "veg":
            main_ing = random.choice(VEG_MAIN)
        elif base == "rice":
            main_ing = "rice"
        else:
            main_ing = "flour"

        pool = INGREDIENTS_BY_STYLE[style]

        k = random.randint(3, min(6, len(pool)))
        extras = random.sample(pool, k)

        ingredients = [main_ing] + extras
        ingredients = list(dict.fromkeys(ingredients))

        sig = tuple(sorted(ingredients))
        if sig in USED_SIGNATURES:
            continue
        USED_SIGNATURES.add(sig)

        recipe_name = generate_name(main_ing, style, ingredients)
        steps = build_steps(style, main_ing, ingredients)

        step_text = "\n".join([f"<STEP> {s}." for s in steps])

        # ===== CONTEXT + ANSWER FORMAT =====
        output = f"""### CONTEXT
Ingredients: {", ".join(ingredients)}

### ANSWER
<RECIPE_NAME> {recipe_name}
{step_text}
<END>"""

        return [" ".join(ingredients), recipe_name, output]

    return None


# =========================
# GENERATE DATASET
# =========================

rows = []

while len(rows) < NUM_SAMPLES:
    sample = generate_sample()
    if sample:
        rows.append(sample)

with open(OUTPUT_FILE,"w",newline="",encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["input","recipe_name","output"])
    writer.writerows(rows)

print("Dataset generated →", OUTPUT_FILE)