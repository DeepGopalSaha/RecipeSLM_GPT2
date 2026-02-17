import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModelForTokenClassification
)
import re

class IngredientExtractor:

    def __init__(self):

        MODEL_PATH = "models/ingredient_extractor"

        print("Loading ingredient extractor:", MODEL_PATH)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        self.model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

        self.model.to(self.device)
        self.model.eval()

        print("Ingredient extractor loaded on:", self.device)

    def extract(self, text):

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        predictions = torch.argmax(outputs.logits, dim=-1)[0]

        tokens = self.tokenizer.convert_ids_to_tokens(
            inputs["input_ids"][0]
        )

        ingredients = []
        current_word = ""

        for token, label in zip(tokens, predictions):

            if label.item() in [1, 2]:  # B-ING or I-ING

                if token.startswith("##"):
                    current_word += token[2:]
                else:
                    if current_word:
                        ingredients.append(current_word)
                    current_word = token

            else:
                if current_word:
                    ingredients.append(current_word)
                    current_word = ""

        if current_word:
            ingredients.append(current_word)

        return ingredients


class SmallLanguageModel:

    def __init__(self):
        MODEL_PATH = "models/train_slm_final_3"

        print("Loading recipe model:", MODEL_PATH)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
        self.model.to(self.device)
        self.model.eval()

        print("Recipe model loaded on:", self.device)

    def parse_output(self, text):

        if "<RECIPE_NAME>" in text:
            text = text.split("<RECIPE_NAME>", 1)[1]
            text = "<RECIPE_NAME>" + text

        for tok in ["<END>", "<|endoftext|>"]:
            if tok in text:
                text = text.split(tok)[0]

        text = text.strip()

        recipe_name = "Recipe"

        if "<RECIPE_NAME>" in text:
            try:
                recipe_name = (
                    text.split("<RECIPE_NAME>", 1)[1]
                    .split("<STEP>", 1)[0]
                    .strip()
                )
            except: pass

        body = text

        if "<RECIPE_NAME>" in body:
            body = body.split("<RECIPE_NAME>", 1)[1]
            if "<STEP>" in body:
                body = body.split("<STEP>", 1)[1]

        raw_sentences = re.split(r'[.!?]+', body)

        steps = []

        COOK_VERBS = [
            "heat", "add", "cook", "saute", "sauté", "mix", "stir",
            "serve", "marinate", "knead", "roll", "fry", "boil",
            "simmer", "roast", "bake"
        ]

        for s in raw_sentences:
            s = re.sub(r'\s+', ' ', s).strip()

            if len(s.split()) < 4:
                continue

            lower = s.lower()
            if not any(v in lower for v in COOK_VERBS):
                continue

            s = s[0].upper() + s[1:]

            steps.append(s)

        return {
            "recipe_name": recipe_name,
            "steps": steps
        }

    def generate(self, prompt, max_new_tokens=220):

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt"
        ).to(self.device)

        end_token_id = self.tokenizer.encode(
            "<END>",
            add_special_tokens=False
        )[0]

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.8,
                top_p=0.95,
                do_sample=True,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=end_token_id
            )

        generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

        full_text = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=False
        )

        if "<END>" in full_text:
            full_text = full_text.split("<END>")[0]

        print("\n------RAW MODEL OUTPUT-----")
        print(full_text)
        print("-----------------------------\n")

        return self.parse_output(full_text)


class RecipeBot:
    def __init__(self):

        self.ingredients = IngredientExtractor()
        self.slm = SmallLanguageModel()
        self.last_ingredients = None

    def answer_question(self, user_input):

        extracted = self.ingredients.extract(user_input)

        ingredients = extracted if extracted else self.last_ingredients

        if not ingredients:
            return "Please provide ingredients first."

        self.last_ingredients = ingredients

        prompt = f"""### CONTEXT
Ingredients: {", ".join(ingredients)}

### ANSWER
"""

        return self.slm.generate(prompt)


if __name__ == "__main__":

    bot = RecipeBot()

    print(bot.answer_question("I have onion potato paneer"))
