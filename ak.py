# Akamai Property Manager Migration Tool

# This script generates a html page (output.html in the same directory) which provides an interface to view an Akamai Property Manager Export. 
# It requires this file to be saved as akamai_export.json in the same directoy. 
# It parses this file and matched behaviors to an external CSV file hosted on Google Docs: <internal>
# CSV and mapping is proprietary to CF.

# This is a work in progress. You'll still need to check default options. I've not included variables as these are unique to Akamai. 

# To run you'll need to install the requests library as it's not standard python install: $ pip install requests

import json
import csv
import requests
import io

# Recursive function to traverse the JSON tree and extract information about each node.
def extract_behaviors_and_criteria(data, result_list, child_list, depth=0):
    if isinstance(data, dict):
        if "children" in data:
            # For each child node in the tree, extract information such as name, behaviors, criteria and children nodes.
            # Append this information to the result list.
            name = data.get("name", "N/A")
            behaviors = data.get("behaviors", [])
            criteria = data.get("criteria", [])
            children = data.get("children", [])
            
            result_list.append({"name": name, "behaviors": behaviors, "criteria": criteria, "children": children, "depth": depth})

            # Recursively call the function on each child node.
            for child in children:
                child_list.append(child.get("name", "N/A"))
                extract_behaviors_and_criteria(child, result_list, child_list, depth=depth+1)

        # For each key-value pair in the data dictionary, if the key is not "children", 
        # recursively call the function on the value.
        for key, value in data.items():
            if key != "children":
                extract_behaviors_and_criteria(value, result_list, child_list, depth=depth)

    elif isinstance(data, list):
        # If data is a list, recursively call the function on each item in the list.
        for item in data:
            extract_behaviors_and_criteria(item, result_list, child_list, depth=depth)

# Function to format JSON data.
def format_json(json_data):
    # Use json.dumps to format the JSON data.
    # Replace various characters in the resulting string to further format the data.
    formatted_json = json.dumps(json_data, indent=2)
    return formatted_json.replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace(',', '').replace('"', '').replace('\'', '')

# Function to load behavior data from a CSV file hosted on Google Docs.
def load_behaviors_csv():
    url = '<add google docs url here>' 
    response = requests.get(url)
    # Check that the request was successful.
    response.raise_for_status()

    behaviors_dict = {}
    # Use the csv.reader to read the CSV data and store it in a dictionary.
    reader = csv.reader(io.StringIO(response.text))
    behaviors_dict = {rows[0]:{"behavior": rows[1], "link": rows[2]} for rows in reader}
    return behaviors_dict

def main():
    input_json_file = 'akamai_export.json'
    output_file = 'output.html'

    # Load JSON data from the input file.
    with open(input_json_file, 'r') as f:
        data = json.load(f)

    rule_children = []
    child_list = []
    # Extract information about each node in the JSON tree.
    extract_behaviors_and_criteria(data, rule_children, child_list)

    # Load behavior data from the CSV file.
    behaviors_dict = load_behaviors_csv()

    # Write the resulting HTML to the output file.
    with open(output_file, 'w') as f:
        # Write the HTML header and styles.
        f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rule Children</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.16/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .hidden { display: none; }
        .scrollable { overflow-x: auto; white-space: nowrap; }
        .indent-0 { padding-left: 0; }
        .indent-1 { padding-left: 10px; }
        .indent-2 { padding-left: 20px; }
        .indent-3 { padding-left: 30px; }
        .indent-4 { padding-left: 40px; }
        .indent-5 { padding-left: 50px; }
        pre {
        white-space: pre-wrap;       /* Since CSS 2.1 */
        white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
        white-space: -pre-wrap;      /* Opera 4-6 */
        white-space: -o-pre-wrap;    /* Opera 7 */
        word-wrap: break-word;       /* Internet Explorer 5.5+ */
        }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto py-10 px-4">
        <h1 class="text-2xl font-bold mb-4">Akamai Property Manager Rules:</h1>
        ''')

        # Count the total number of child objects and those that have been added inside a card.
        total_child_count = len(child_list)
        added_child_count = sum(len(rule_child['children']) for rule_child in rule_children)

        # If there are child objects that haven't been added inside a card, display a warning.
        if total_child_count > added_child_count:
            f.write(f'''
            <div class="alert alert-warning" role="alert">
                Warning: {total_child_count - added_child_count} child objects have not been added inside a card. These include: {', '.join(child_list[added_child_count:])}
            </div>
            ''')

        # Create a navigation bar on the left side of the screen.
        f.write('''
        <div class="flex h-screen">
            <div class="w-1/4 bg-white border-r border-gray-300 overflow-auto sticky top-0">
                <nav class="p-4">
        ''')

        # For each child object, create a link in the navigation bar that allows the user to view the child's details.
        for idx, rule_child in enumerate(rule_children):
            indent_class = f'indent-{rule_child["depth"]}'
            f.write(f'''
                    <a id="nav-item-{idx}" href="javascript:void(0)" onclick="displayRuleChild({idx})" class="{indent_class} block py-2 px-4 hover:bg-gray-200">{rule_child["name"]}</a>
            ''')

        # Create a container for displaying the child object details.
        f.write('''
                </nav>
            </div>
            <div class="w-3/4 p-4">
                <div id="rule-child-container">
        ''')

        # For each child object, create a card with the child's details.
        for idx, rule_child in enumerate(rule_children):
            behaviors = rule_child['behaviors']
            criteria = format_json(rule_child['criteria'])

            f.write(f'''
                    <div id="rule-child-{idx}" class="rule-child hidden">
                        <h2 class="text-xl font-bold mb-4">{rule_child["name"]}</h2>
                        <h3 class="text-lg font-bold mb-2">Behaviors:</h3>
            ''')

            # If behaviors are present, look up for their equivalent in the behaviors dictionary,
            # and create a section for each of them in the details card.
            for behavior in behaviors:
                behavior_name = behavior.get('name', None)
                if behavior_name:
                    matching_behavior_data = behaviors_dict.get(behavior_name, None)
                    if matching_behavior_data:
                        f.write(f'''
                        <div class="flex mb-4">
                            <div class="w-1/2 border p-4">
                                <h3 class="text-lg font-bold mb-2">{behavior_name}:</h3>
                                <pre>{json.dumps(behavior, indent=2)}</pre>
                            </div>
                            <div class="w-1/2 border p-4">
                                <h3 class="text-lg font-bold mb-2">Cloudflare Equivalent:</h3>
                                <pre>{matching_behavior_data["behavior"]}</pre>
                                {'' if not matching_behavior_data["link"] else f'<a href="{matching_behavior_data["link"]}">{matching_behavior_data["link"]}</a>'}
                            </div>
                        </div>
                        ''')
                    
            f.write(f'''
                        <h3 class="text-lg font-bold mb-2">Criteria:</h3>
                        <pre class="border p-4 mb-4">{criteria}</pre>
            ''')

            # Closing tag for the child's card            
            f.write('</div>')                                

        # Closing tags for the parent containers and the HTML body and document.
        f.write('''
                </div>
            </div>
        </div>
    </div>
    <script>
        function displayRuleChild(idx) {
            var ruleChildElements = document.getElementsByClassName('rule-child');
            for (var i = 0; i < ruleChildElements.length; i++) {
                ruleChildElements[i].classList.add('hidden');
                document.getElementById('nav-item-' + i).classList.remove('bg-gray-300');
            }
            var ruleChildElement = document.getElementById('rule-child-' + idx);
            ruleChildElement.classList.remove('hidden');

            var navItemElement = document.getElementById('nav-item-' + idx);
            navItemElement.classList.add('bg-gray-300');
        }
    </script>
</body>
</html>
        ''')

# boot it up!
if __name__ == '__main__':
    main()