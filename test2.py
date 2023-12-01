from app.main.translations.translation import languages, translation


def get_translated_values(key, lang_code):
    translated_values = {}
    if key in translation:
        for sub_key, sub_value in translation[key].items():
            translated_values[sub_key] = sub_value.get(lang_code, sub_value.get('en'))
    return translated_values


# Example usage:
language_code = 'bg'
translated_values = get_translated_values('', language_code)
print(f"Translated values in {languages[language_code]}:")

print(translated_values['title'])

for key, value in translated_values.items():
    print(f'{key}: {value}')