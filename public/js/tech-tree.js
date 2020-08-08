'use strict';

const AREAS = ['physics', 'society', 'engineering']
const TIERS = [1, 2, 3, 4, 5]

let config = {
    container: '#tech-tree',
    rootOrientation: 'WEST',
    nodeAlign: 'TOP',
    hideRootNode: true,
    siblingSeparation: 20,
    subTeeSeparation:  20,
    scrollbar: 'native',
    connectors: { type: 'step' },
    node: {
		HTMLclass: 'tech',
		collapsable: true
    },
    callback: {
		onTreeLoaded: function() {
			$(document).tooltip({
				items: 'p.description, p.weight-modifiers[title]',
				content: function() {
					let $button = $(this);
					
					setTimeout(function() {
						// TODO: Quite Hacky, Maybe swapout tooltip engine?
						// After the tooltip div is created, whack the tech.are class on it to change the border color
						var $c = $button.attr('class');
						AREAS.forEach(area => {
							if ($c.includes(area)) { $('.ui-tooltip').addClass(area) } else { $('.ui-tooltip').removeClass(area) }
						})
					}, 50);

					// copies class and raw html from the item being moused over into the tooltip window for display
					var $content = $('<span>')
						.addClass($button.attr('class'))
						.html($button.attr('title'));

					return $('<div class="tooltip-header">')
						.addClass($button.attr('class'))
						.html($button.data('header'))
						.after($content);
				}
			});
		}
    }
};

let rootNode = {HTMLid: 'root', data: {tier: 0}};

function colorize(s, extra_css_class)
{
	var start = '';
	var end = '';
	switch(s.charAt(1))
	{
		case 'R': start = '<span style="color: red;" class="' + extra_css_class + '">'; end = '</span>'; break;
		case 'G': start = '<span style="color: green;" class="' + extra_css_class + '">'; end = '</span>'; break;
		case 'Y': start = '<span style="color: yellow;" class="' + extra_css_class + '">'; end = '</span>'; break;
		// [H]ighlight maybe?
		case 'H': start = '<span style="color: orange;" class="' + extra_css_class + '">'; end = '</span>'; break;
		default: console.log('unexpected § color ' + s.charAt(1))
	}
	return start + s.slice(2, s.length-2) + end;
}

function subst_icons_and_colors(str, extra_css_class = "")
{
	return str
		// £ is \u00a3 for embedding icons
		.replace(new RegExp(/£(\w+)£/,'g'), '<img class="resource ' + extra_css_class + '" src="../icons/$1.png" />')
		// TODO: We don't need both forms in the json?   This is used for feature unlocks
		.replace(/\(\[\[(\w+)\]\]\)/g, '<img class="resource ' + extra_css_class + '" src="../icons/$1.png" />')
		// § is \u00a7 for changing text colors
		.replace(/[\u00a7][A-Z][^\u00a7]*[\u00a7][!]/g, colorize)
		;
}

function prerequisite_name_lookup(techData, key, area)
{
	return techData.filter( t => t.key == key).map(t => t.name + (t.area == area ? ' (tier ' + t.tier + ')' : ' (' + t.area + ', tier ' + t.tier + ')'));
}

function area_compare(a, b)
{
	return AREAS.indexOf(b) - AREAS.indexOf(a);
}

$(document).ready(function() {
	
	(function ($) {
		$.each(['show', 'hide'], function (i, ev) {
			var el = $.fn[ev];
			$.fn[ev] = function () {
			this.trigger(ev);
			return el.apply(this, arguments);
			};
		});
		})(jQuery);

    $.getJSON('techs.json', function(techData) {

		console.time('sort')
		techData.sort( (a, b) => area_compare(a.area, b.area) * -100 + a.category.localeCompare(b.category) * 10 + a.name.localeCompare(b.name) );
		console.timeEnd('sort')

		function extraDataDiv(tech) {

			let $descBtn = $('<p>').addClass('description').addClass(tech.area).append('<span class="dots">…</span>');
			let prerequisites = tech.prerequisites.reduce( (out, x) => out += '<br />&nbsp;&nbsp;&nbsp;' + prerequisite_name_lookup(techData, x, tech.area), "");
			let unlocks = '';
			if ( tech.feature_unlocks.length > 0 ) {
				let $unlockList = $('<ul>');
				tech.feature_unlocks.forEach( unlock => {
					if (null === unlock) {
						console.log('Ignored null feature_unlock for ' + tech.key);
					} else {
						$unlockList.append($('<li>').append(subst_icons_and_colors(unlock)));
					}
				});				
				unlocks = '<br /><div class="tooltip-header second-tooltip ' + tech.area + '">Research Effects</div>';
				unlocks += $unlockList[0].outerHTML;
			}
			$descBtn.attr('title', tech.description + '<br />'
				+ (tech.dlc && tech.dlc.length > 0 ? '<br />Requires DLC: ' + tech.dlc.join(', ') + '<br />' : "")
				+ (prerequisites.length > 0 ? '<br />Prerequisites:' + prerequisites + '<br />' : '')
				+ (tech.is_dangerous ? '<br />Tech is dangerous' : "")
				+ (tech.is_rare ? '<br />Tech is rare<br />' : "")
				+ unlocks
			);
			$descBtn.attr('data-header', 'Description');		
			if (tech.prerequisites.filter( p => techData.some( t => t.key == p && t.tier > 0 )).reduce(c => ++c, 0) > 1)
			{
				$descBtn.addClass('multiple-prerequisistes');
			}

			let $modifiersBtn = $('<p>').addClass('weight-modifiers').addClass(tech.area).html('⚄');
			if ( tech.weight_modifiers.length > 0 ) {
				let weightModifiers = tech.weight_modifiers.join('')
				weightModifiers = weightModifiers.replace(/(?:\(.?)([0-9.+-]+)(?:\))/g,  m => '<span class="' + (parseFloat(m.replace(/[^0-9.+-]/g,'')) >= 1.0 ? 'mod-good' : 'mod-bad') + '">' + m + '</span>');
				$modifiersBtn.attr('title', subst_icons_and_colors(weightModifiers));
				$modifiersBtn.attr('data-header', 'Weight Modifiers');
			}
			else {
				$modifiersBtn.addClass('disabled');
			}

			return $('<div class="extra-data">').addClass('tier'+tech.tier).addClass(tech.area).append($descBtn).append($modifiersBtn)[0].outerHTML;
		}

		console.time('add keys')
		let maxTier = 0
		let techs = techData.filter(function(tech) {
			return Object.keys(tech)[0].search(/^@\w+$/) == -1;
		}).map(function(tech) {
			let tier = tech.is_start_tech ? ' (Starting)' : ' (Tier ' + tech.tier + ')';
			let cost = tech.tier > 0 ? 'Cost: <span class="' + tech.area + '-research">' + tech.cost + '</span>' : null;
			let weight = tech.tier > 0 ? 'Weight: ' + tech.base_weight : null;
			if (tech.tier > maxTier) {
				maxTier = tech.tier;
			}
			return {
				HTMLid: tech.key,
				HTMLclass: tech.area + (tech.dlc && tech.dlc.length > 0 ? " dlc" : "") + (tech.is_rare ? ' rare' : '') + (tech.is_dangerous ? ' dangerous' : ''),
				data: tech,
				innerHTML: '<div class="icon" style="background-image:url(img/' + tech.key + '.png)"></div>'
					+ '<p class="node-name" title="' + tech.name + '">' + tech.name + '</p>'
					+ '<p class="node-title">' + (tech.category + tier) + '</p>'
					+ '<p class="node-desc">' + ( tech.start_tech || tech.tier == 0 ? '' : cost + ',' + weight) + '</p>'
					+ extraDataDiv(tech)
			};
		});
		console.timeEnd('add keys')


		const TIERS = Array.from({length: maxTier}, (v, k) => k+1); 

		// dummy root nodes for techs which start with no lower tier dependencies
		let tierNodes = {}
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
		let SPECIAL_NODES = [rootNode];
		Object.values(tierNodes).forEach( x => Object.values(x).forEach( y => SPECIAL_NODES.push(y) ));

		console.time('find parents')
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
				if (tech.parent == null) {
					console.log('No match for any prerequisistes of ' + tech.data.key + ' ' + JSON.stringify(tech.data.prerequisites))
					if (TIERS.includes(tech.data.tier)) {
						tech.parent = tierNodes[tech.data.area][tech.data.tier]
					} else {
						tech.parent = rootNode
					}
				}
			}
		});
		console.timeEnd('find parents')

		function compute_age(tech) {
			let parent = tech.parent;
			let age = 0;
			while (!SPECIAL_NODES.includes(parent))
			{
				parent = parent.parent;
				age += 1;
				if (parent.childrenDropLevel) {
					age += parent.childrenDropLevel;
				}
			}
			if (parent != rootNode) {
				age += parent.data.tier;
			}
			return age;
		}

		console.time('rearrange')
		// Some rearranging to get the unparented + parented techs to group better by area
		let techlist = [config, rootNode]
		let remaining_areas = Array.from(AREAS)
		let last_area = null
		techs.forEach( tech => {
			// Push in pseudonodes for items with no prerequisistes. They should get inserted after any well formed trees tracing from a starter tech.
			if (last_area == null) {
				last_area = tech.data.area;
			} else if (tech.data.area !== last_area && remaining_areas.length > 0 && tech.data.tier == 0) {
				last_area = remaining_areas.shift();
				Object.entries(tierNodes[last_area]).forEach(([k, v]) => techlist.push(v));
				last_area = tech.data.area
			}

			// Build up dummy pseudonodes so high leveled techs are never rendered in a column lower than their tier
			let age = compute_age(tech);
			if (age < tech.data.tier && !SPECIAL_NODES.includes(tech.parent))
			{
				// console.log("Bumping " + tech.data.name + ' from ' + age + ' to ' + tech.data.tier);
				let o = { 
					parent: tech.parent,
					pseudo: true,
					childrenDropLevel: tech.data.tier - age - 1
				}
				tech.parent = o;
				techlist.push(o)
			}

			techlist.push(tech)
		});
		remaining_areas.forEach( area => {
			Object.entries(tierNodes[area]).forEach(([k, v]) => techlist.push(v));
		});
		console.timeEnd('rearrange')

		console.time('new Treant')
		new Treant(techlist);
		console.timeEnd('new Treant')
    });
});
