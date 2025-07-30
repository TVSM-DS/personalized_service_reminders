import json
def get_pitch(json_file_path, segment, language, pitch_type):
    segment_name = segment.replace("_", " ").title()
    print(f"Fetching pitch for segment: {segment_name}, language: {language}, pitch type: {pitch_type}")
    if pitch_type not in ["pitch_30s", "pitch_2min"]:
        print(f"Invalid pitch type: {pitch_type}. Must be 'pitch_30s' or 'pitch_2min'.")
        return None

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("mmmmmmmmmmmmmmmmmmm ",json_file_path, segment_name, language, pitch_type)
    for lang_block in data:
        if lang_block.get("language") == language:
            for pitch in lang_block.get("pitches", []):
                if pitch.get("segment") == segment_name:
                    return pitch.get(pitch_type)
    return f"Pitch not found for segment '{segment_name}' in '{language}'."



# Example usage:mmmmmmmmmmmmmmmmmmm  TVS_AllLanguages_Pitches_Complete.json free_service_maximisers Hindi pitch_30s
json_path = 'TVS_AllLanguages_Pitches_Complete.json'  # Put your actual JSON filename here
language = "Hindi"
segment_name = "Free Service Maximizers"
pitch_type = "pitch_30s"

pitch_text = get_pitch("TVS_AllLanguages_Pitches_Complete.json", segment_name, language, pitch_type)
if pitch_text:
    print(f"Pitch found:\n{pitch_text}")
else:
    print("No matching pitch found.")
