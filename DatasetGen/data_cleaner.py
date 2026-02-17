import csv
import random

INPUT_FILE = "recipes_10000.csv"
OUTPUT_FILE = "recipes_10000_cleaned.csv"


PROTEINS = {"chicken", "mutton", "fish", "paneer", "egg"}
VEGETABLES = {
    "potato","cauliflower","spinach","okra","brinjal","mushroom",
    "peas","beans","carrot","capsicum","onion"
}


# ==================================================
# PARAPHRASE POOL (3 variants each)
# ==================================================

PARAPHRASE_MAP = {

    "Heat oil in pan.": [
        "Warm oil in a pan.",
        "Heat some oil in a cooking pan.",
        "Start by heating oil in a pan."
    ],

    "Heat ghee in a pot.": [
        "Warm ghee in a pot.",
        "Begin by heating ghee in a pot.",
        "Heat some ghee in a cooking pot."
    ],

    "Knead into soft dough.": [
        "Knead well until a soft dough forms.",
        "Work it into a smooth soft dough.",
        "Knead gently to make soft dough."
    ],

    "Cook covered and serve hot.": [
        "Cover and cook until done, then serve hot.",
        "Cook covered until ready and serve warm.",
        "Cover the pot, cook fully, and serve hot."
    ],

    "Cook on hot tawa and serve hot.": [
        "Cook on a hot tawa until done and serve hot.",
        "Roast on a heated tawa and serve warm.",
        "Place on hot tawa, cook evenly, and serve hot."
    ],

    "Cook in oven or tandoor.": [
        "Roast in an oven or tandoor until cooked.",
        "Cook inside oven or tandoor until done.",
        "Bake in tandoor or oven until ready."
    ],

    "Serve hot.": [
        "Serve immediately while hot.",
        "Serve warm and fresh.",
        "Enjoy hot."
    ]
}


# ==================================================
# STEP REPLACEMENT (ROTI / PARATHA)
# ==================================================

def replace_rest_step(output_text, recipe_name):

    if ("roti" in recipe_name.lower()) or ("paratha" in recipe_name.lower()):
        x = random.choice([15, 20, 25])
        output_text = output_text.replace(
            "Add spices according to your liking.",
            f"Let it rest for {x} minutes."
        )

    return output_text


# ==================================================
# RICE NAME FIX
# ==================================================

def fix_rice_name(recipe_name, ingredients):

    name_lower = recipe_name.lower()

    if "rice biryani" in name_lower or "rice pulao" in name_lower:

        ing_set = set(ingredients)
        replacement = None

        for p in PROTEINS:
            if p in ing_set:
                replacement = p.title()
                break

        if replacement is None:
            for v in VEGETABLES:
                if v in ing_set:
                    replacement = v.title()
                    break

        if replacement:
            recipe_name = recipe_name.replace("Rice", replacement)

    return recipe_name


# ==================================================
# PARAPHRASE RANDOMIZER
# ==================================================

def apply_paraphrasing(output_text):

    lines = output_text.split("\n")
    new_lines = []

    for line in lines:

        replaced = False

        for original, variants in PARAPHRASE_MAP.items():
            if original in line:
                line = line.replace(
                    original,
                    random.choice(variants)
                )
                replaced = True
                break

        new_lines.append(line)

    return "\n".join(new_lines)


# ==================================================
# CLEAN DATASET
# ==================================================

def clean_dataset():

    rows_out = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:

            ingredients = row["input"].split()
            recipe_name = row["recipe_name"]
            output_text = row["output"]

            # replace rest step
            output_text = replace_rest_step(output_text, recipe_name)

            # fix rice naming
            #recipe_name = fix_rice_name(recipe_name, ingredients)

            # update recipe name inside output
            output_text = output_text.replace(
                "<RECIPE_NAME> " + row["recipe_name"],
                "<RECIPE_NAME> " + recipe_name
            )

            # apply paraphrasing
            output_text = apply_paraphrasing(output_text)

            rows_out.append([
                row["input"],
                recipe_name,
                output_text
            ])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["input","recipe_name","output"])
        writer.writerows(rows_out)

    print("Cleaned dataset saved →", OUTPUT_FILE)


if __name__ == "__main__":
    clean_dataset()
