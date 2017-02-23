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
  }
};
let rootNode = {HTMLid: 'root', data: {tier: 0}};

$(document).ready(function() {
  $.getJSON('techs.json', function(techData) {
    let techs = techData.filter(function(tech) {
      return (tech.tier == 0 || tech.weight > 0)
        && Object.keys(tech)[0].search(/^@\w+$/) == -1;
    }).map(function(tech) {
      let key = tech.key;
      let tier = tech.tier > 0
          ? ' (Tier ' + tech.tier + ')'
          : ' (Starting)';
      let costClass = tech.area.toLowerCase() + '-research';
      let cost = tech.tier > 0
          ? 'Cost: <span class="' + costClass + '">' + tech.cost + '</span>'
          : '';
      let weight = tech.tier > 0
          ? 'Weight: ' + tech.weight
          : '';
      let category = tech.category + tier;

      return {
        HTMLid: key,
        HTMLclass: tech.area.toLowerCase(),
        data: tech,
        collapsed: tech.key == 'tech_colonization_1',
        innerHTML: '<img src="img/' + key + '.png" />'
          + '<p class="node-name">' + tech.name + '</p>'
          + '<p class="node-title">' + category + '</p>'
          + ( tech.start_tech || tech.tier == 0 ? '' : [cost, weight].join(', '))
        // collapsed: tech.area != 'Society'
      };
    });

    techs = techs.map(function(tech) {
      let key = tech.data.key;

      if ( tech.data.tier === 0 || tech.data.prerequisite === null) {
        tech.parent = rootNode;
      }
      else {
        let parentKey = tech.data.prerequisite;
        tech.parent = parentKey.match('-pseudoParent')
          ? { HTMLid: tech.HTMLid + '-pseudoParent',
              parent: rootNode,
              pseudo: true,
              data: {tier: 0} }
          : techs.filter(function(candidate) {
            return candidate.HTMLid === parentKey;
          })[0];
      }

      let tierDifference = tech.data.tier - tech.parent.data.tier;
      let nestedTech = tech;
      while ( tierDifference > 1 ) {
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

    new Treant( [config, rootNode].concat(techs) );
  });
});
