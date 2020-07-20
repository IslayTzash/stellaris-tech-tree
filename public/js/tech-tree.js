'use strict';

let config = {
    container: '#tech-tree',
    rootOrientation: 'WEST', // NORTH || EAST || WEST || SOUTH
    nodeAlign: 'TOP',
    // levelSeparation: 30,
    hideRootNode: true,
    siblingSeparation: 20,
    subTeeSeparation:  20,
    scrollbar: 'fancy',
    connectors: { type: 'step' },
    node: {
		HTMLclass: 'tech',
		collapsable: true
    },
    callback: {
		onTreeLoaded: function() {
			$(document).tooltip({
				items: 'p.description, p.weight-modifiers[title], p.feature-unlocks[title]',
				content: function() {
					let $button = $(this);

					// copies class and raw html from the item being moused over into the tooltip window for display
					var $content = $('<span>')
						.removeClass(['weight-modifiers','feature-unlocks', 'description'])
						.addClass($button.attr('class'))
						.html($button.attr('title'));

					return $('<div class="tooltip-header">')
						.html($button.data('header'))
						.after($content);
				}
			});
		}
    }
};

let rootNode = {HTMLid: 'root', data: {tier: 0}};

// dummy root nodes for techs which start with no lower tier dependencies
let tierNodes = {}
const AREAS = ['physics', 'society', 'engineering']
const TIERS = [1, 2, 3, 4, 5]
AREAS.forEach(area => {
	tierNodes[area] = {}
	TIERS.forEach(tier => {
		let o = { 
			HTMLid: area+'-tier-'+tier,
			HTMLclass: area,
			data: {tier: tier},
			parent: rootNode,
			pseudo: true,
			childrenDropLevel: tier - 1,
			connectors: {
				style: {
					'stroke-opacity': 0
				}
			},
			text: { 
				name: 'Tier ' + tier + ', No Prereq',
				title: area
			}
		}
		tierNodes[area][tier] = o
	})
})

function replace_icons(str, extra_css_class = "")
{
	return str
		.replace(new RegExp(/£(\w+)£/,'g'), '<img class="resource ' + extra_css_class + '" src="../icons/$1.png" />')
		// TODO: We don't need both forms in the json?
		.replace(/\(\[\[(\w+)\]\]\)/, '<img class="resource ' + extra_css_class + '" src="../icons/$1.png" />');
}

function prerequisite_name_lookup(techData, key, area)
{
	return techData.filter( t => t.key == key).map(t => t.name + (t.area == area ? '' : ' (' + t.area + ', tier ' + t.tier + ')'));
}

$(document).ready(function() {
    $.getJSON('techs.json', function(techData) {
		let techs = techData.filter(function(tech) {
			return Object.keys(tech)[0].search(/^@\w+$/) == -1;
		}).map(function(tech) {
			let tier = tech.is_start_tech ? ' (Starting)' : ' (Tier ' + tech.tier + ')';
			let cost = tech.tier > 0 ? 'Cost: <span class="' + tech.area + '-research">' + tech.cost + '</span>' : null;
			let weight = tech.tier > 0 ? 'Weight: ' + tech.base_weight : null;
			let category = tech.category + tier;

			function extraDataDiv() {
				let $descBtn = $('<p>').addClass('description').append('<span class="dots">…</span>');
				let prerequisites = tech.prerequisites.reduce( (out, x) => out += '<br />&nbsp;&nbsp;&nbsp;' + prerequisite_name_lookup(techData, x, tech.area), "");
				$descBtn.attr('title', tech.description + '<br />'
					+ (tech.dlc.length > 0 ? '<br />Requires DLC: ' + tech.dlc.join(', ') + '<br />' : "")
					+ (prerequisites.length > 0 ? '<br />Prerequisites:' + prerequisites + '<br />' : '')
					+ (tech.is_dangerous ? '<br />Tech is dangerous' : "")
					+ (tech.is_rare ? '<br />Tech is rare' : "")
				);
				$descBtn.attr('data-header', 'Description');		
				if (tech.prerequisites.some( p => techData.some( t => t.key == p && t.tier > 0 )))
				{
					$descBtn.addClass('multiple-prerequisistes');
				}

				let $modifiersBtn = $('<p>').addClass('weight-modifiers').html('⚄');
				if ( tech.weight_modifiers.length > 0 ) {
					let weightModifiers = tech.weight_modifiers.join('')
					weightModifiers = weightModifiers.replace(/(?:\(.?)([0-9.+-]+)(?:\))/g,  m => '<span class="' + (parseFloat(m.replace(/[^0-9.+-]/g,'')) >= 1.0 ? 'mod-good' : 'mod-bad') + '">' + m + '</span>');
					$modifiersBtn.attr('title', weightModifiers);
					$modifiersBtn.attr('data-header', 'Weight Modifiers');
				}
				else {
					$modifiersBtn.addClass('disabled');
				}

				let $unlocksBtn = $('<p>').addClass('feature-unlocks').html('🎁');
				if ( tech.feature_unlocks.length > 0 ) {
					let $unlockList = $('<ul>');
					tech.feature_unlocks.forEach( unlock => {
						if (null === unlock) {
							console.log('Ignored null feature_unlock for ' + tech.key);
						} else {
							$unlockList.append($('<li>').append(replace_icons(unlock)));
						}
					});				
					$unlocksBtn.attr('title', $unlockList[0].outerHTML);
					$unlocksBtn.attr('data-header', 'Research Effects');
				}
				else {
					$unlocksBtn.addClass('disabled');
				}

				return $('<div class="extra-data">').append($descBtn).append($modifiersBtn).append($unlocksBtn)[0].outerHTML;
			}

			return {
				HTMLid: tech.key,
				HTMLclass: tech.area + (tech.dlc.length > 0 ? " dlc" : "") + (tech.is_rare ? ' rare' : '') + (tech.is_dangerous ? ' dangerous' : ''),
				data: tech,
				innerHTML: '<div class="icon" style="background-image:url(img/' + tech.key + '.png)"></div>'
					+ '<p class="node-name" title="' + tech.name + '">' + tech.name + '</p>'
					+ '<p class="node-title">' + category + '</p>'
					+ '<p class="node-desc">' + ( tech.start_tech || tech.tier == 0 ? '' : cost + ',' + weight) + '</p>'
					+ extraDataDiv()
			};
		});

		techs.map(tech => {
			if ( tech.data.tier === 0 || tech.data.prerequisites < 1)
			{
				if (TIERS.includes(tech.data.tier)) {
					tech.parent = tierNodes[tech.data.area][tech.data.tier]
				} else {
					tech.parent = rootNode
				}
			}
			else
			{
				tech.parent = techs.filter( candidate => tech.data.prerequisites.includes(candidate.data.key) )
					.reduce( (parent, candidate) => {
						if ( ! parent ) {
							parent = candidate
						} else if (parent.data.area == tech.data.area) {
							if (tech.data.area == candidate.data.area && parent.data.tier > candidate.data.tier) {
								parent = candidate;
							}
						} else if (tech.data.area == candidate.data.area) {
							parent = candidate;
						} else if (parent.data.tier > candidate.data.tier) {
							parent = candidate;
						}
						return parent;
					}, tech.parent);
			}
		});

		// Some rearranging to get the unparented + parented techs to group better by area
		let techlist = [config, rootNode]
		let remaining_areas = Array.from(AREAS)
		let last_area = null
		techs.forEach( tech => {
			techlist = techlist.concat(tech)
			if (tech.data.area !== last_area && remaining_areas.length > 0) {
				last_area = remaining_areas.shift();
				techlist = techlist.concat(tierNodes[last_area]);
			}
		});
		remaining_areas.forEach( area => {
			techlist = techlist.concat(tierNodes[area]);
		});

		new Treant(techlist);
    });
});
