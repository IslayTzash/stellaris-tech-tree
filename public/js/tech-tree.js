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
        items: 'p.description, p.weight-modifiers[title]',
        content: function() {
          let $button = $(this);
          if ($button.is('p.description')) {
            var contentClass = 'description';
            var header = 'Description';
          }
          if ($button.is('p.weight-modifiers')) {
            var contentClass = 'weight-modifiers';
            var header = 'Weight Modifiers';
          }
          let $contentSpan = $('<span>')
            .addClass(contentClass)
            .html($button.attr('title'));
          return $('<div class="tooltip-header">')
            .html(header)
            .after($contentSpan);
        },
      });
    }
  }
};
let rootNode = {HTMLid: 'root', data: {tier: 0}};

$(document).ready(function() {
  $.getJSON('techs.json', function(techData) {
    let techs = techData.filter(function(tech) {
      return Object.keys(tech)[0].search(/^@\w+$/) == -1;
    }).map(function(tech) {
      if ( tech.key.match(/^tech_akx_worm/) ) {
        console.log(tech.key);
      }
      let key = tech.key;
      let tier = tech.tier > 0
          ? ' (Tier ' + tech.tier + ')'
          : ' (Starting)';
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
        $descBtn.attr('title', tech.desc);
        $descBtn.html('…');

        let weightModifiers = tech.weight_modifiers.length > 0
            ? tech.weight_modifiers.join('')
            : null;

        let $modifiersBtn = $('<p>');
        if ( weightModifiers !== null ) {
          $modifiersBtn.addClass('weight-modifiers');
          $modifiersBtn.attr('title', weightModifiers);
          $modifiersBtn.attr('data-header', 'Weight Modifiers');
        }
        else {
          $modifiersBtn.addClass('weight-modifiers');
          $modifiersBtn.addClass('disabled');
        }
        $modifiersBtn.html('⚄');

        let $extraDataDiv = $('<div class="extraData">');
        $extraDataDiv.append($descBtn);
        $extraDataDiv.append($modifiersBtn);
        return $extraDataDiv;
      }();

      return {
        HTMLid: key,
        HTMLclass: tech.area,
        data: tech,
        innerHTML: '<div class="' + iconClass + '" style="background-image:url(img/' + key + '.png)"></div>'
          + '<p class="node-name">'
          + tech.name
          + '</p>'
          + '<p class="node-title">' + category + '</p>'
          + '<p class="node-desc">' + ( tech.start_tech || tech.tier == 0 ? '<br />' : [cost, weight].join(', ')) + '</p>'
          + $extraDataDiv[0].outerHTML
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

      if ( tech.data.key.match(/^tech_akx_worm/) ) {
        console.log(tech);
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

    new Treant([config, rootNode].concat(techs));
  });
});
