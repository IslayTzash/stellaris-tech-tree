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
		    if ( $button.is('p.feature-unlocks') ) {
			let unlocks = $button.attr('title').split(', ');
			var $content = unlocks.map(
			    function(unlock) {
				return $('<li>').html(
				    unlock.replace(/\[\[(\w+)\]\]/,
						   '<img class="resource" src="img/resources/$1.png" />')
				); }
			).reduce(
			    function($ul, $unlock) {
				return $ul.append($unlock);
			    },
			    $('<ul>')
			);
		    }
		    else {
			var $content = $('<span>')
				.addClass($button.attr('class'))
				.html($button.attr('title'));
		    }

		    return $('<div class="tooltip-header">')
			.html($button.data('header'))
			.after($content);
		}
	    });
	}
    }
};
let rootNode = {HTMLid: 'root', data: {tier: 0}};
// society, engineering, physics 1 2 3 4 5
let tierNodes = {}
const AREAS = ['society', 'engineering', 'physics']
const TIERS = [1, 2, 3, 4, 5]
AREAS.forEach(area => {
	tierNodes[area] = {}
	TIERS.forEach(tier => {
		let o = { 
			HTMLid: area+'-tier-'+tier,
			HTMLclass: area,
			data: {tier: tier},
			parent: rootNode, // tier == 1 ? rootNode : tierNodes[area][tier-1],
			pseudo: true,
			childrenDropLevel: tier - 1,
			connectors: {
				style: {
					'stroke-opacity': 0,
					'stroke': 'white'
				}
			},
			text: { 
				name: 'T' + tier + ' No Prereq',
				title: area
			}
		}
		tierNodes[area][tier] = o
	})
})

$(document).ready(function() {
    $.getJSON('techs.json', function(techData) {
	let techs = techData.filter(function(tech) {
	    return Object.keys(tech)[0].search(/^@\w+$/) == -1;
	}).map(function(tech) {
	    let key = tech.key;
	    let tier = tech.is_start_tech
		    ? ' (Starting)'
		    : ' (Tier ' + tech.tier + ')';

	    let costClass = tech.area + '-research';
	    let cost = tech.tier > 0
		    ? 'Cost: <span class="' + costClass + '">' + tech.cost + '</span>'
		    : null;
	    let weight = tech.tier > 0
		    ? 'Weight: ' + tech.base_weight
		    : null;
	    let category = tech.category + tier;
	    let iconClass = 'icon'
		    + (tech.is_dangerous ? ' dangerous' : '')
		    + (!tech.is_dangerous && tech.is_rare ? ' rare' : '');

	    let $extraDataDiv = function() {
		let $descBtn = $('<p>');
		$descBtn.addClass('description');
		$descBtn.attr('title', tech.description + '<br />'
			+ (tech.dlc.length > 0 ? '<br />Requires DLC: ' + tech.dlc.join(', ') + '<br />' : "")
			+ (tech.is_dangerous ? '<br />Tech is dangerous' : "")
			+ (tech.is_rare ? '<br />Tech is rare' : "")
		);
		$descBtn.attr('data-header', 'Description');
		$descBtn.html('…');
		let weightModifiers = tech.weight_modifiers.length > 0
			? tech.weight_modifiers.join('')
			: null;
		let featureUnlocks = tech.feature_unlocks.length > 0
			? tech.feature_unlocks.join(', ')
			: null;

		let $modifiersBtn = $('<p>');
		$modifiersBtn.addClass('weight-modifiers');
		if ( weightModifiers !== null ) {
		    $modifiersBtn.attr('title', weightModifiers);
		    $modifiersBtn.attr('data-header', 'Weight Modifiers');
		}
		else {
		    $modifiersBtn.addClass('disabled');
		}
		$modifiersBtn.html('⚄');

		let $unlocksBtn = $('<p>');
		$unlocksBtn.addClass('feature-unlocks');
		if ( featureUnlocks !== null ) {
		    $unlocksBtn.attr('title', featureUnlocks);
		    $unlocksBtn.attr('data-header', 'Research Effects');
		}
		else {
		    $unlocksBtn.addClass('disabled');
		}
		$unlocksBtn.html('🎁');

		let $extraDataDiv = $('<div class="extra-data">');
		$extraDataDiv.append($descBtn);
		$extraDataDiv.append($modifiersBtn);
		$extraDataDiv.append($unlocksBtn);
		return $extraDataDiv;
	    }();

	    return {
		HTMLid: key,
		HTMLclass: tech.area + (tech.dlc.length > 0 ? " dlc" : ""),
		data: tech,
		innerHTML: '<div class="' + iconClass + '" style="background-image:url(img/' + key + '.png)"></div>'
		    + '<p class="node-name" title="' + tech.name + '">'
		    + tech.name
		    + '</p>'
		    + '<p class="node-title">' + category + '</p>'
		    + '<p class="node-desc">' + ( tech.start_tech || tech.tier == 0 ? '<br />' : [cost, weight].join(', ')) + '</p>'
		    + $extraDataDiv[0].outerHTML
	    };
	});

	techs = techs.map(function(tech) {
	    let key = tech.data.key;
	    let prerequisite = tech.data.prerequisites[0] || null;

	    if ( tech.data.tier === 0 || prerequisite === null) {
			if (tech.data.tier === 1 || tech.data.tier === 2 || tech.data.tier === 3 ||tech.data.tier === 4 ||tech.data.tier === 5) {
				tech.parent = tierNodes[tech.data.area][tech.data.tier]
			} else {
				tech.parent = rootNode
			}
	    }
	    else {
			let parentKey = prerequisite;
			tech.parent = parentKey.match('-pseudoParent')
				? { HTMLid: tech.HTMLid + '-pseudoParent',
					parent: rootNode,
					pseudo: true,
					data: {tier: 0}
					}
				: techs.filter(function(candidate) {
					return candidate.HTMLid === parentKey;
					})[0];
	    }

	    let tierDifference = tech.data.tier - tech.parent.data.tier;
	    let nestedTech = tech;
	    while ( tierDifference > 1 && nestedTech.parent != rootNode ) {
		var pseudo = {
		    HTMLid: nestedTech.HTMLid + '-pseudoParent',
		    parent: nestedTech.parent, pseudo: true,
		    data: { tier: nestedTech.data.tier - 1 }
		};
		tierDifference--;
		nestedTech.parent = pseudo;
		nestedTech = pseudo;
	    }

	    return tech;
	});

	for ( let i = 0; i < techs.length; i++ ) {
	    let tech = techs[i]
	    while ( tech.parent.pseudo ) {
		techs.push(tech.parent);
		tech = tech.parent;
		}
	}

	// Some rearranging to get the unparented + parented techs to group better by area
	// assuming techs are ordered: physics, society, engineering
	let techlist = [config, rootNode, tierNodes['physics'][1], tierNodes['physics'][2], tierNodes['physics'][3], tierNodes['physics'][4], tierNodes['physics'][5]]
	let last_area = 'physics'
	let remaining_areas = [ 'society', 'engineering']
	for ( let i = 0; i < techs.length; i++ ) {
		techlist = techlist.concat(techs[i])
		if (techs[i].data.area !== last_area && remaining_areas.length > 0) {
			let area = remaining_areas.shift()
			techlist = techlist.concat(tierNodes[area][1], tierNodes[area][2], tierNodes[area][3], tierNodes[area][4], tierNodes[area][5])
			last_area = techs[i].data.area
		}
	}
	// Just in case we were totally out of order and missed one
	remaining_areas.forEach( area => {
		techlist = techlist.concat(tierNodes[area][1], tierNodes[area][2], tierNodes[area][3], tierNodes[area][4], tierNodes[area][5])
	})

	new Treant(techlist);

    });
});
