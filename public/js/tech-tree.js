'use strict';

let config = {
  container: '#tech-tree',
  rootOrientation:  'NORTH', // NORTH || EAST || WEST || SOUTH
  // levelSeparation: 30,
  hideRootNode: true,
  siblingSeparation: 20,
  subTeeSeparation:  20,
  scrollbar: 'None',
  connectors: { type: 'step' },
  node: { HTMLclass: 'tech' }
};
let rootNode = {HTMLid: 'root', data: {tier: 0, subtier: 0}};

$(document).ready(function() {
  $.getJSON('techs.json', function(techData) {
    let techs = techData.filter(function(tech) {
      return (tech.tier == 0 || tech.weight > 0)
        && Object.keys(tech)[0].search(/^@\w+$/) == -1;
    }).map(function(tech) {
      let key = tech['key'];
      return {
        HTMLid: key,
        image: '/img/' + key + '.png',
        data: tech,
        text: {},
        // collapsed: tech.area != 'Society'
      };
    });

    techs = techs.map(function(tech) {
      tech.text.name = tech.data.name;
      let tier = tech.data.tier > 0
          ? ' (Tier ' + tech.data.tier + '-' + tech.data.subtier + ')'
          : ' (Starting)';
      let cost = tech.data.tier > 0
          ? 'Base Cost: ' + tech.data.cost
          : '';
      let category = tech.data.category + tier + '\n';
      tech.text.title = cost
      tech.text.desc = category;

      if ( tech.data.tier === 0 ) {
        tech.parent = rootNode;
      }
      else {
        let parentKey = tech.data.prerequisite === null
            ? tech.HTMLid + '-pseudoParent'
            : tech.data.prerequisite;
        tech.parent = parentKey.match('-pseudoParent')
          ? { HTMLid: tech.HTMLid + '-pseudoParent',
              parent: rootNode,
              pseudo: true,
              data: { tier: 0, subtier: 0 } }
          : techs.filter(function(candidate) {
            return candidate.HTMLid === parentKey;
          })[0];
      }

      let isTier1_1 = tech.data.tier == 1
          && tech.data.subtier == 1
          && tech.parent.data.tier == 0;
      let tierDifference = isTier1_1
          ? 0
          : tech.data.tier - tech.parent.data.tier;
      let subtierDifference = isTier1_1
          ? 0
          : tech.data.subtier - tech.parent.data.subtier;
      let nestedTech = tech;
      while ( tierDifference > 0 ||
              (tech.data.tier > 0 && tierDifference == 0 && subtierDifference > 1) ) {
        if ( tierDifference > 0 ) {
          if ( nestedTech.data.subtier == 1 ) {
            var pseudo = {
              HTMLid: nestedTech.HTMLid + '-pseudoParent',
              parent: nestedTech.parent, pseudo: true,
              data: { tier: nestedTech.data.tier - 1, subtier: 4 }
            };
            tierDifference--;
            subtierDifference = tech.data.subtier - 4;
          }
          else {
            var pseudo = {
              HTMLid: nestedTech.HTMLid + '-pseudoParent',
              parent: nestedTech.parent, pseudo: true,
              data: { tier: nestedTech.data.tier,
                      subtier: nestedTech.data.subtier - 1 }
            };
            subtierDifference --;
          }
        }
        else {
          var pseudo = {
            HTMLid: nestedTech.HTMLid + '-pseudoParent',
            parent: nestedTech.parent, pseudo: true,
            data: { tier: nestedTech.data.tier,
                    subtier: nestedTech.data.subtier - 1 }
          };
          subtierDifference--;
        }

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
