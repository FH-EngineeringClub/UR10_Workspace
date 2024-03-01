import json


# Function to generate the new JSON data
def generate_json():
    base_data = {"a1": {"x": 0, "y": 0}}
    letters = ["a", "b", "c", "d", "e", "f", "g", "h"]

    # Generate the JSON data according to the pattern
    for number in range(1, 9):
        for i in range(1, 9):
            letter = letters[i - 1]
            base_data[letter + str(number)] = {
                "x": 42
                * (
                    number - 1
                ),  # set 25.4 to the offset between center of each square in mm
                "y": -1 * 42 * (i - 1),
            }

    return base_data


# Generate JSON data
new_json_data = generate_json()

# Write JSON data to a file
with open("generated_json.json", "w") as outfile:
    json.dump(new_json_data, outfile, indent=4)

print("JSON file generated successfully!")
