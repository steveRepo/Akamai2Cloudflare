This script is work in progress and a proof of concept. 

The script creates a HTML page which details the JSON in an easy to read format and maps some cloudflare config to the behaviors via a CSV which contains Akamai config mapped to cloudflare. The idea would be to expand this mapping. 

The script requires an Akamai Property Manager JSON export. You should have this file present in the same directory and titled: akamai_export.json.

* Update: This script now pulls down this Google sheets file as the Source CSV for mapping: <Cloudflare Property>

Stylings will be added in the next update.

To use run: $ python ak.py. You'll be presented with behaviors tree in the sidebar and each page contains the behvaiors criteria for each 
config item. 

The intention is to work towards scripting up CF API calls from the Akamai behaviors and criteria on each page to create the config on 
cloudflare. 

I've included some sample JSON exports from previous projects and a sample output.html where you can see what an export looks like.

Reach out with any feedback to smoylan@cloudflare.com - it's much appreciated!
