# Stellaris Tech Tree Viewer

This provides a set of files to view the technology tree for the 4x strategy game Stellaris.

Predominantly this repository contains a python3 tool to generate a HTML/CSS rendering of the tech tree information from the game files.
* /script/ contains the python code to parse the game files
* /public/ contains the output from the python tool and some HTML/CSS/JS and other assets to provide a view you can load in a web browser

# File Generation

1. Copy config.example.py to config.py.   Edit accordingly.  For windows, I use the values below with triple quotes.
```
    game_dir = """C:\Games\Steam\steamapps\common\Stellaris"""
    workshop_dir = """C:\Games\Steam\steamapps\workshop\content\281990"""
```
2. Run the python script.   It will may print warnings about some items which aren't handled properly.  It will generate public/vanilla/techs.json.
```
    python script\parse.py vanilla
```

# Viewing the output

You could upload the whole /public/ directory to a web server or run a local server.   Unfortunately it won't work if
you try to open it from your local disk.   You can easily run a webserver by switching into the public directory and running
```python -m http.server 8000``` and connect to http://localhost:8000 in your browser.

# Credits

This was pulled from a gitlab repo started by bipedalshark, but has not been updated since 2017, v2.0.1.   See https://gitlab.com/bipedalshark/stellaris-tech-tree/-/tree/master

Latest images have been merged from https://github.com/turanar/stellaris-tech-tree (see Alternatives below).

# Alternatives

There is another fork of bipedalshark's code on github managed by tunrar and other contributors.  This is active as of July 2020, but
has changed the parser from python to java and split the game file [parser](https://github.com/turanar/stellaris-technology)
and [viewer](https://github.com/turanar/stellaris-tech-tree) into two separate repositories.

# Overview of Parsing

Many of the Stellaris game rules are captured in YAML files.  Looking in /steamapps/common/Stellaris/common there are folders for many of the games basic concepts.

achievements                  | country_types              | leader_classes                | sector_focuses
achievements.txt              | decisions                  | mandates                      | sector_types
agendas                       | defines                    | map_modes                     | ship_behaviors
ai_budget                     | deposit_categories         | megastructures                | ship_sizes
alerts.txt                    | deposits                   | message_types.txt             | solar_system_initializers
ambient_objects               | diplo_phrases              | name_lists                    | special_projects
anomalies                     | diplomacy_economy          | notification_modifiers        | species_archetypes
archaeological_site_types     | diplomatic_actions         | observation_station_missions  | species_classes
armies                        | districts                  | on_actions                    | species_names
artifact_actions              | dynamic_text               | opinion_modifiers             | species_rights
ascension_perks               | economic_categories        | personalities                 | star_classes
asteroid_belts                | economic_plans             | planet_classes                | starbase_buildings
attitudes                     | edicts                     | planet_modifiers              | starbase_levels
bombardment_stances           | ethics                     | policies                      | starbase_modules
buildings                     | event_chains               | pop_categories                | starbase_types
button_effects                | fallen_empires             | pop_faction_types             | start_screen_messages
bypass                        | federation_law_categories  | pop_jobs                      | static_modifiers
casus_belli                   | federation_laws            | precursor_civilizations       | strategic_resources
colony_automation             | federation_perks           | random_names                  | subjects
colony_automation_exceptions  | federation_types           | relics                        | system_types
colony_types                  | galactic_focuses           | resolution_categories         | technology
colors                        | game_rules                 | resolutions                   | terraform
component_sets                | global_ship_designs        | scripted_effects              | trade_conversions
component_slot_templates      | governments                | scripted_loc                  | tradition_categories
component_tags                | graphical_culture          | scripted_triggers             | traditions
component_templates           | HOW_TO_MAKE_NEW_SHIPS.txt  | scripted_variables            | traits
country_customization         | lawsuits                   | section_templates             | war_goals

If you look inside /technology/ you can see files for the main tech areas [physics, social, engineering] and the DLC.

00_apocalypse_tech.txt      | 00_fallen_empire_tech.txt  | 00_phys_tech.txt             | 00_soc_tech_repeatable.txt       | tier/
00_distant_stars_tech.txt   | 00_horizonsignal_tech.txt  | 00_phys_tech_repeatable.txt  | 00_soc_weapon_tech.txt
00_eng_tech.txt             | 00_leviathans_tech.txt     | 00_phys_weapon_tech.txt      | 00_strategic_resources_tech.txt
00_eng_tech_repeatable.txt  | 00_megacorp_tech.txt       | 00_repeatable.txt            | 00_synthetic_dawn_tech.txt
00_eng_weapon_tech.txt      | 00_megastructures.txt      | 00_soc_tech.txt              | category/

The entries are mostly human readable.

```
tech_corvette_build_speed = {
        cost = @tier1cost2
        area = engineering
        tier = 1
        category = { voidcraft }
        prerequisites = { "tech_corvettes" }
        weight = @tier1weight2

        modifier = {
                shipsize_corvette_build_speed_mult = 0.25
                ship_corvette_cost_mult = -0.05
        }

        weight_modifier = {
                modifier = {
                        factor = 1.25
                        research_leader = {
                                area = engineering
                                has_trait = "leader_trait_expertise_voidcraft"
                        }
                }
        }

        ai_weight = {
                modifier = {
                        factor = 1.25
                        research_leader = {
                                area = engineering
                                has_trait = "leader_trait_expertise_voidcraft"
                        }
                }
        }
}
```

Mostly we want to pull out the name, tier, area, category, prerequisites, cost, weight, any adjustments to the weight, and the dlc requirements.

All the short string get maped to more readable English (or whatever language) from the Stellaris/common/localization/english

```
tech_corvette_build_speed:0 "Standardized Corvette Patterns"
tech_corvette_build_speed_desc:0 "Establishing new standards for the modeling and construction of corvettes greatly improves the efficiency of the production pipeline."
leader_trait_expertise_voidcraft:0 "Expertise: Voidcraft"
```

Items that show up with a @, $, or Brittish pound sign are replaceable parameters within a field and get hit with another level of substitution.

# Overview of Web Display

The tech tree viewer uses a Treant.js for displaying the tree.  It appears to have been designed for displaying corporate org charts.

The techs.json file is loaded by tech-tree.js and rebuilt into the json expected by Treant.

The custom files for the Stellaris tech viewer are mostly:
* /public/vanilla/index.html
* /public/js/tech-tree.js
* /public/css/tech-tree.cs