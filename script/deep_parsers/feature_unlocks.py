import re

class FeatureUnlocks:
    def __init__(self, armies, army_attachments, buildable_pops, buildings,
                 components, edicts, policies, resources, spaceport_modules,
                 tile_blockers, localizer, at_vars):
        self._armies = armies
        self._army_attachments = army_attachments
        self._buildable_pops = buildable_pops
        self._buildings = buildings
        self._components = components
        self._edicts = edicts
        self._policies = policies
        self._resources = resources
        self._spaceport_modules = spaceport_modules
        self._tile_blockers = tile_blockers
        self._localizer = localizer
        self._at_vars = at_vars


    # Modifiers gained as a result of completing research
    def parse(self, tech_key, tech_data):
        return self._modifiers(tech_data) \
            + self._unlocks(tech_data) \
            + self._feature_flags(tech_data) \
            + self._army_attachment_unlocks(tech_key) \
            + self._buildable_pop_unlocks(tech_key) \
            + self._building_unlocks(tech_key) \
            + self._component_unlocks(tech_key) \
            + self._edict_unlocks(tech_key) \
            + self._policy_unlocks(tech_key) \
            + self._resource_unlocks(tech_key) \
            + self._spaceport_module_unlocks(tech_key) \
            + self._tile_blocker_unlocks(tech_key)


    def _dedupe_list(self, original):
        """Remove duplicates and items that differ by pularalness from lists.  Also elements which are None."""
        newlist = []
        for i in original:
            if i is not None and i not in newlist and i+'s' not in newlist and re.sub(r's$', '', i) not in newlist:
                newlist.append(i)
        return newlist

    def _expand_modifiers(self, modifier, has_description_parameters):
        """
        Helper invoked by _modifiers() to process one list element

        :returns: string of the form 'key: value' or None
        """
        key = list(modifier.keys())[0]
        m = modifier[key]

        if 'description' == key and has_description_parameters:
            # We don't have a good processor for the description_parameters, so far it only shows with gene tailoring which includes another line item for the +1 points
            return None
        elif key in ('description_parameters', 'show_only_custom_tooltip'):  # Always skip over these            
            return None
        elif 'custom_tooltip' == key:  # For now, hand-roll tooltip contents here            
            if m == 'ADD_NAVAL_CAPACITY_FROM_SOLDIERS':
                return '([[fleet_size_icon]]) Naval Capacity from ([[job_soldier]]) Soldiers: +2'
            else:
                print(' ** No match for modifier tooltip: ' + m)
                return { 'tooltip': m }

        if type(m) is str and m.startswith('@') and m in self._at_vars:
            value = self._at_vars[m]
        elif m in ['yes', 'no', 'YES', 'NO', 'Yes', 'No']:
            value = m
        else:
            try:
                value = ('{:+.0%}'.format(m)
                        if int(m) < 1
                        or int(m) != m
                        else '{:+d}'.format(int(m)))
            except:
                value = None
                if type(m) is str:
                    value = self._localizer.get_or_default(m, None)
                if value is None:
                    print(' ++ Unexpected modifier in feature_unlocks.py: ' + repr(m))
                    value = m

        # Dyslexic remapping
        if key == 'all_technology_research_speed':
            key = 'MOD_COUNTRY_ALL_TECH_RESEARCH_SPEED'
        elif key == 'science_ship_survey_speed':
            key = 'MOD_SHIP_SCIENCE_SURVEY_SPEED'
        elif key == 'species_leader_exp_gain':
            key = 'MOD_LEADER_SPECIES_EXP_GAIN'
        elif key == 'ship_archeaological_site_clues_add':
            key = 'MOD_SHIP_ARCHAEOLOGICAL_SITE_CLUES_ADD'
        elif key == 'ship_anomaly_research_speed_mult':
            key =  'MOD_SHIP_ANOMALY_RESEARCH_SPEED'

        found_prefix_match = False
        for prefix in [ '', 'MOD_', 'MOD_COUNTRY_', 'MOD_POP_', 'MOD_PLANET_']:
            alt_key = (prefix + key).upper()
            try:
                localized_key = self._localizer.get_or_default(alt_key, None)
                if localized_key is None:
                    continue
                key =  localized_key
                found_prefix_match = True
                break
            except KeyError:
                pass
        if not found_prefix_match:
            # Most often is a dyslexic entry in the localization/english files.  See remapping entries above.
            print(' ** No match for modifier: ' + repr(key))

        return '{}: {}'.format(key, value)


    def _modifiers(self, tech_data):
        """
        Parse the modifier field in each tech

        modifier = {
            description = tech_gene_tailoring_modifier_desc
            description_parameters = {
                POINTS = @tech_gene_tailoring_POINTS
            }
            BIOLOGICAL_species_trait_points_add = @tech_gene_tailoring_POINTS
        }

        modifier = {
            country_command_limit_add = 20
        }
        """
        try:
            has_description_parameters = 'description_parameters' in repr(tech_data)
            return self._dedupe_list([self._expand_modifiers(modifier, has_description_parameters)
                    for modifier
                    in next(iter(attribute for attribute
                                in tech_data
                                if list(attribute.keys())[0] == 'modifier'))['modifier']])
        except (StopIteration):
            return []


    def _unlocks(self, tech_data):
        """
        Techs have an inverse prequistes map, indicating what they lead to.

        prereqfor_desc = {
                hide_prereq_for_desc = component
                custom = {
                        title = "TECH_UNLOCK_COMBAT_COMPUTERS_2_TITLE"
                        desc = "TECH_UNLOCK_COMBAT_COMPUTERS_2_DESC"
                }
        }
        """
        try:
            unlock_types = [unlock_type for unlock_type in next(iter(
                attribute for attribute in tech_data
                if list(attribute.keys())[0] == 'prereqfor_desc'
            ))['prereqfor_desc']]
            return self._dedupe_list([self._localizer.get(list(unlock.values())[0][0]['title'])
                               for unlock in unlock_types
                               if list(unlock)[0] != 'hide_prereq_for_desc'])
        except (StopIteration):
            return []


    def _feature_flags(self, tech_data):
        """
        Techs have a forward mapping to unlocked features

        feature_flags = {
                planetary_ftl_inhibitor
        }
        """
        try:
            return self._dedupe_list([
                'Unlocks Feature: ' + self._localizer.get('feature_' + feature_flag)
                for feature_flag
                in next(iter(
                    attribute for attribute in tech_data
                    if list(attribute.keys())[0] == 'feature_flags'
                ))['feature_flags']
            ])
        except (StopIteration):
            return []

    def _policy_unlocks(self, tech_key):
        def relevant_options(policy):
            return [{'name': option.name,
                     'policy_name': policy.name }
                    for option in policy.options
                    if tech_key in option.prerequisites]

        unlocked_options = [option for options
                            in [relevant_options(policy)
                                for policy in self._policies]
                            for option in options]

        return self._dedupe_list(['Unlocks Policy: {} - {}'.format(option['policy_name'],
                                                                   option['name'])
                for option in unlocked_options])

    def _resource_unlocks(self, tech_key):
        return self._dedupe_list(['Reveals Resource: {} ([[{}]])'.format(resource.name, resource.key)
                for resource in self._resources if tech_key in resource.prerequisites])

    # We also do a lot of prerequiste checks on other data types
    # Find other data types which list this tech as a prerequisite

    def _generic_keyed_unlocks(self, key, collection, label):
        return self._dedupe_list(['{}: {}'.format(label, i.name) for i in collection if key in i.prerequisites])

    def _army_unlocks(self, tech_key):
        return self._generic_keyed_unlocks(tech_key, self._armies, 'Unlocks Army')

    def _army_attachment_unlocks(self, tech_key):
        return self._generic_keyed_unlocks(tech_key, self._army_attachments, 'Unlocks Attachment')

    def _buildable_pop_unlocks(self, tech_key):
        return self._generic_keyed_unlocks(tech_key, self._buildable_pops, 'Unlocks Buildable Pop')

    def _building_unlocks(self, tech_key):
        return self._generic_keyed_unlocks(tech_key, self._buildings, 'Unlocks Building')

    def _component_unlocks(self, tech_key):
        return self._generic_keyed_unlocks(tech_key, self._components, 'Unlocks Component')

    def _edict_unlocks(self, tech_key):
        return self._generic_keyed_unlocks(tech_key, self._edicts, 'Unlocks Edict')

    def _spaceport_module_unlocks(self, tech_key):
        return self._generic_keyed_unlocks(tech_key, self._spaceport_modules, 'Unlocks Module')

    def _tile_blocker_unlocks(self, tech_key):
        return self._generic_keyed_unlocks(tech_key, self._tile_blockers, 'Clear Blockers')
