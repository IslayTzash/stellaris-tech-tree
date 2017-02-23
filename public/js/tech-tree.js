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
      let key = tech['key'];
      return {
        HTMLid: key,
        image: 'img/' + key + '.png',
        HTMLclass: tech.area.toLowerCase(),
        data: tech,
        collapsed: tech.key == 'tech_colonization_1',
        text: {},
        // collapsed: tech.area != 'Society'
      };
    });

    function isTier1_1(tech) {
      return tech.data.tier == 1 && tech.parent.data.tier == 0;
    }

    techs = techs.map(function(tech) {
      tech.text.name = tech.data.name;
      let tier = tech.data.tier > 0
          ? ' (Tier ' + tech.data.tier + ')'
          : ' (Starting)';
      let cost = tech.data.tier > 0
          ? 'Base Cost: ' + tech.data.cost
          : '';
      let weight = tech.data.tier > 0
          ? 'Base Weight: ' + tech.data.weight
          : '';
      let category = tech.data.category + tier + '\n';
      tech.text.title = cost
      tech.text.desc = category;

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

      let tierDifference = isTier1_1(tech)
          ? 0
          : tech.data.tier - tech.parent.data.tier;
      let nestedTech = tech;
      while ( tierDifference > 0 ) {
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
