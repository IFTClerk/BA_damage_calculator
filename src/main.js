var current_source = {};
var current_target = {};
var current_attack = {};
var current_buff = {};
var buff_list = [];
var equipment_data = {};


// load equipment data from JSON
function loadEquipmentData() {
    fetch(Settings.data_dir + 'equipment.json')
        .then(response => response.json())
        .then(data => { equipment_data = data; })
        .catch(error => console.log(error));
}
// load character data from JSON
function loadCharacterData() {
    const selected = document.getElementById('character_source').value;
    if (selected!=="") {
        fetch(Settings.char_data_dir + selected + '.json')
            .then(response => response.json())
            .then(data => initialiseData(data))
            .catch(error => console.log(error));
    }
}
// initialise character data and display in panel
function initialiseData(json_data) {
    current_source = json_data;
    // print json for debugging
    const json_content = JSON.stringify(current_source);
    document.getElementById('json_content').innerHTML = json_content;
    // initialise all the stats
    setEquipmentNames();
    setUEStatus();
    setBaseStat();
    setBondBonus();
    setUEInnateBonus();
    setUEPassiveBonus();
    setEquipmentBonus();
    // show input panel for unit info
    var source_input = document.getElementById('source_input');
    if (source_input.style.display==='none') {
        source_input.style.display = '';
    }
}
// function to set base stat 
function setBaseStat() {
    // get base stat
    const base_stats = getBaseStat();
    // loop though base stat to fill table
    for (var stat_name of Object.keys(base_stats)) {
        var this_stat = document.getElementById('base_'+stat_name);
        if (this_stat) {
            //console.log('found element');
            this_stat.innerHTML = base_stats[stat_name];
        }
    }
}
// get base stat values
function getBaseStat() {
    // attempt to access base stat from JSON and throw exception if failed
    const base_stats = current_source.status || false;
    if (!base_stats) throw "Cannot access character status";
    // access current level and star number for future
    const current_level = document.getElementById('char_level').value;
    const current_stars = document.getElementById('char_stars').value;
    // initialise return object
    var stats = {};
    // loop through the keys of base stat object
    for (var stat_name of Object.keys(base_stats)) {
        // console.log(key + "->" + base_stats[key]);
        var stat_value = base_stats[stat_name];
        if (complex_stats.includes(stat_name)) {
            stat_value = interpolateStat(stat_value, current_level);
            stat_value *= (1 + star_level_multiplier[stat_name][current_stars - 1])
        }
        stats[stat_name] = Math.ceil(stat_value);
    }
    return stats;
}
// function to set equipment names
function setEquipmentNames() {
    const eq_names = current_source.equipment || ['', '', ''];
    document.getElementById('eq1_name').innerHTML = capitaliseWord(eq_names[0]) || 'Equipment 1';
    document.getElementById('eq2_name').innerHTML = capitaliseWord(eq_names[1]) || 'Equipment 2';
    document.getElementById('eq3_name').innerHTML = capitaliseWord(eq_names[2]) || 'Equipment 3';
}
// function to hide/show UE controls
function setUEStatus() {
    const n_stars = document.getElementById('char_stars').value;
    //const n_stars = char_stars.value;
    if (n_stars==5) {
        // Set UE entries to be visible if 5 starred
        document.getElementById('unique_eq').style.display = '';
        // document.getElementById('ue_tier').value = 1;
    } else if (n_stars>=1 && n_stars<=4) {
        // Set UE entries to be invisible when under 5 stars
        document.getElementById('unique_eq').style.display = 'none';
        document.getElementById('ue_tier').value = 0;
    } else {
        console.log('Uh oh');
    }
    // reset max level if necessary
    setUEMaxLevel();
}
// function to update UE max level based on tier
function setUEMaxLevel() {
    // Set the max UE level according to the tier
    const tier_max = [1, 30, 40, 50, 60, 70];
    const ue_tier = document.getElementById('ue_tier').value;
    const ue_max = tier_max[ue_tier];
    var ue_level = document.getElementById('ue_level');
    ue_level.max = ue_max;
    // cap the UE level
    //if (ue_level.value>ue_max) {
    ue_level.value = ue_max;
    //}
}
// set UE innate bonus stat display
function setUEInnateBonus() {
    var ue_bonus_innate = document.getElementById('ue_bonus_innate');
    const ue_tier = document.getElementById('ue_tier').value;
    if (ue_tier<1) {
        ue_bonus_innate.style.display = 'none';
        return;
    } else if (ue_tier>=1) {
        ue_bonus_innate.style.display = '';
    }
    const ue_bonus_stat = getUEInnateBonus();
    document.getElementById('ue_bonus_innate_value').innerHTML = printBonuses(ue_bonus_stat);
}
// get UE innate stat bonus value
function getUEInnateBonus() {
    // find corresponding stats from UE level
    const ue_level = document.getElementById('ue_level').value;
    const status_bonus = current_source.unique_equipment.innate_status_bonus;
    var bonuses = [];
    for (var i=0; i<status_bonus.length; i++) {
        const this_bonus = status_bonus[i];
        const scaled_value = interpolateStat(this_bonus.value, ue_level);
        bonuses.push({ "status": this_bonus.status, "type": "flat", "value": scaled_value });
    }

    return bonuses;
}
// set UE passive skill bonus stat display
function setUEPassiveBonus() {
    // check if UE Passive Skill bonus is enabled
    var ue_bonus_ps = document.getElementById('ue_bonus_ps');
    const ue_tier = document.getElementById('ue_tier').value;
    if (ue_tier<2) {
        ue_bonus_ps.style.display = 'none';   
        return;
    } else if (ue_tier>=2) {
        ue_bonus_ps.style.display = '';   
    }
    const ue_ps_bonus_stat = getUEPassiveBonus();
    // print bonus to html
    document.getElementById('ue_bonus_ps_value').innerHTML = printBonuses(ue_ps_bonus_stat);
}
// get UE passive skill bonus stat value
function getUEPassiveBonus() {
    // calculate PS stat bonus from UE
    const ps_level = document.getElementById('ps_level').value;
    const ue_stat_bonus = current_source.unique_equipment.ps_status_bonus;
    const stat_name = ue_stat_bonus.status;
    const stat_value = ue_stat_bonus.value[ps_level - 1];
    
    return [{ "status": stat_name, "type": "flat", "value": stat_value }];
}
// set bond bonus stat display in panel
function setBondBonus() {
    var bond_bonus = document.getElementById('bond_bonus');
    // set visible first
    if (bond_bonus.style.display==='none') {
        bond_bonus.style.display = '';
    }
    const bonuses = getBondBonus();
    document.getElementById('bond_bonus_value').innerHTML = printBonuses(bonuses);
}
// get values of bond bonus
function getBondBonus() {
    var bonuses = [];
    // get bond bonus values
    const bond_bonus_info = current_source.bond;
    //console.log(bond_bonus_info);
    // get bond level
    const char_bond = document.getElementById('char_bond').value;
    for (var i=0; i<bond_bonus_info.length; i++) {
        // append the correct bonus values based on level
        const this_bonus = bond_bonus_info[i];
        const bonus_value = this_bonus.value[char_bond-1] ? this_bonus.value[char_bond-1] : 0;
        bonuses.push({ "status": this_bonus.status, "type": "flat", "value": bonus_value });
    }
    return bonuses;
}
// get specialist support bonus stats value
function getSupportBonus() {
    var bonuses = [];
    for (var i=0; i<complex_stats.length; i++) {
        this_stat = complex_stats[i];
        this_spec_bonus = document.getElementById('spec_'+this_stat).value;
        if (this_spec_bonus!=0) {
            bonuses.push({ "status": this_stat, "type": "flat", "value": +this_spec_bonus });
        }
    }
    //console.log(bonuses);
    return bonuses;
}
// set equipment bonus stat display in panel
function setEquipmentBonus() {
    const bonuses = getEquipmentBonus();
    var equipment_bonus_value = document.getElementById('equipment_bonus_value');
    var merged_bonuses = bonuses.reduce(addBonuses, []);
    equipment_bonus_value.innerHTML = printBonuses(merged_bonuses);
}
// get values of equipment bonus
function getEquipmentBonus() {
    const eq_names = current_source.equipment;
    var eq_bonuses = [];
    if (eq_names) {
        // loop through all equipment names
        for (var i=0; i<eq_names.length; i++) {
            // find corresponding entry in equipment data json
            const equipment = equipment_data[eq_names[i]];
            const eq_level = document.getElementById('eq'+(i+1)+'_tier').value;
            for (var j=0; j<equipment.length; j++) {
                const this_bonus = equipment[j];
                // get the right level of bonus
                const value = this_bonus.value[eq_level-1];
                // append individual bonuses to the appropriate return value
                eq_bonuses.push({ "status": this_bonus.status, "type": this_bonus.type, "value": value });
            }
        }
    } 
    return eq_bonuses;
}
// get terrain affinity multiplier
function getTerrainMult() {
    const terrain_index  = document.querySelector('input[name="battle_terrain"]:checked').value;
    const terrain_base_mult = current_source.terrain_mod[terrain_index];
    const ue_tier = document.getElementById('ue_tier').value;
    var terrain_bonus_mult = 0;
    if (ue_tier>=3) {
        terrain_bonus_mult = current_source.unique_equipment.terrain_mod_bonus[terrain_index];
    }
    return (terrain_base_mult + terrain_bonus_mult);
}
// set selected buff max level
function setCurrentBuff() {
    const selected_buff = document.getElementById('buff_select').value;
    if (selected_buff!=="") {
        // look for the buff in buff.json
        fetch(Settings.skill_data_dir + 'buff.json')
            .then(response => response.json())
            .then(data => {
                var buff_button = document.getElementById('button_add_buff');
                buff_button.disabled = true;
                current_buff = data[selected_buff];
                //console.log(current_buff);
                var buff_level = document.getElementById('buff_level');
                buff_level.max = current_buff.value.length;
                buff_level.value = buff_level.max;
                buff_button.disabled = false;
            })
            .catch(error => console.log(error));
    }
}
// add buffs to the buff table
function addBuff() {
    const buff_level = document.getElementById('buff_level').value;
    buff_list.push({ "display_name": current_buff.display_name, "status": current_buff.status, "type": "mult", "value":current_buff.value[buff_level-1] });
    //console.log(buff_list);
    setBuffTable();
}
// remove buff from the buff table and redraws table
function removeBuff(e) {
    var this_row = e.closest('tr');
    // removes the corresponding buff in buff list with splice
    if (this_row.rowIndex >= 0) {
        buff_list.splice((this_row.rowIndex-1), 1);
    }
    setBuffTable();
}
// set buff table contents
function setBuffTable() {
    buff_table = document.getElementById('buff_table_body');
    var all_rows = [];
    //console.log(buff_list);
    for (var i=0; i<buff_list.length; i++) {
        this_buff = buff_list[i];
        const buff_text = printBonuses(this_buff);
        const row = '<tr>' + '<td class="buff-name">' + this_buff.display_name + '</td>' +
            '<td class="buff-value">' + buff_text + '</td>' +
            '<td class="buff-remove"><input type="button" value="Remove" onclick="removeBuff(this)"></td>' + '</tr>';
        all_rows.push(row);
    }
    buff_table.innerHTML = all_rows.join('\r\n');
}
// get current bonuses from buffs
function getBuffBonus() {
    //console.log(buff_list);
    return buff_list;
}
// set attack info based on selected attack
function setCurrentAttack() {
    const selected_attack = document.getElementById('attack_select');
    if (selected_attack.value!=="custom" && selected_attack.value!=="") {
        const category = selected_attack.options[selected_attack.selectedIndex].parentNode.label;
        var json_name = '';
        if (category==='Damage Skills') {
            json_name = 'damage';
        } else if (category==='Heal Skills') {
            json_name = 'heal';
        } else {
            console.log('Invalid Attack selected');
            return;
        }
        fetch(Settings.skill_data_dir + json_name + '.json')
            .then(response => response.json())
            .then(data => {
                current_attack = data[selected_attack.value];
                current_attack.category = json_name;
                var attack_level = document.getElementById('attack_level');
                attack_level.max = current_attack.value.length;
                attack_level.value = attack_level.max;
                setAttackInfo();
            })
            .catch(error => console.log(error));
    }
}
// set attack information based on level
function setAttackInfo() {
    if (!current_attack.value) {
        console.log('No Preset Attack Selected');
        return;
    }
    var attack_mult = document.getElementById('attack_mult');
    var attack_nhits = document.getElementById('attack_nhits');
    const attack_level = document.getElementById('attack_level').value;
    attack_mult.value = Math.round(current_attack.value[attack_level-1] * 100);
    attack_nhits.value = current_attack.nhits || 1; 
    document.getElementById('skill_'+current_attack.category).checked = true;
}
// set attack selector to 'custom' if user modifies the values
function setCustomAttack() {
    var attack_select = document.getElementById('attack_select');
    if (attack_select.value!="custom") {
        attack_select.value = "custom";
    }
    current_attack = {};
}
// get attack multiplier and number of hits from page
function getAttackInfo() {
    const attack_mult = document.getElementById('attack_mult').value / 100;
    const attack_nhits = document.getElementById('attack_nhits').value;
    const attack_category = document.querySelector('input[name="attack_category"]:checked').value;
    return { "multiplier": attack_mult, "n_hits": attack_nhits, "category": attack_category };
}
// collect all the bonuses and return a single list of bonuses
function getTotalBonus() {
    var total_bonus = [];
    // concatenate all the bonuses
    total_bonus = total_bonus.concat(getBondBonus());
    total_bonus = total_bonus.concat(getEquipmentBonus());
    total_bonus = total_bonus.concat(getSupportBonus());
    total_bonus = total_bonus.concat(getBuffBonus());
    if (document.getElementById('char_stars').value==5) {
        const ue_tier = document.getElementById('ue_tier').value;
        if (ue_tier>0) {
            total_bonus = total_bonus.concat(getUEInnateBonus());
        }
        if (ue_tier>=2) {
            total_bonus = total_bonus.concat(getUEPassiveBonus());
        }
    }
    // add together all the bonuses
    //console.log(total_bonus);
    total_bonus = total_bonus.reduce(addBonuses, []);
    return total_bonus;
}
// calculate actual stat after modifiers
function getFinalStat() {
    // get base stat first and assign to return value
    var final_stat = getBaseStat();
    // apply the bonuses to each of the stats
    const comb_bonus = getTotalBonus();
    // split up bonuses into flat and multipliers
    const split_bonus = splitBonuses(comb_bonus);
    const flat_bonus = split_bonus.flat;
    const mult_bonus = split_bonus.mult;
    // apply flat bonuses first
    for (var i=0; i<flat_bonus.length; i++) {
        const this_bonus = flat_bonus[i];
        // only apply if the stat actually exists
        if (final_stat[this_bonus.status]) {
            final_stat[this_bonus.status] += +this_bonus.value;
        }
    }
    // apply multipliers
    for (var j=0; j<mult_bonus.length; j++) {
        const this_bonus = mult_bonus[j];
        // skip crit dmg multiplier because for some fucking reason its applied later
        // if (this_bonus.status=="crit_dmg" && this_bonus.type=="mult") continue;
        // ^^  this was fixed by applying crit_dmg modifiers to crit_dmg_resist later on
        if (final_stat[this_bonus.status]) {
            final_stat[this_bonus.status] *= (1 + this_bonus.value);
            final_stat[this_bonus.status] = Math.ceil(final_stat[this_bonus.status]);
        }
    }
    return final_stat;
}
// gather target info
function getTargetInfo() {
    // initialise return var
    var target_info = {};
    // get armour type
    target_info.armour_type = document.querySelector('input[name="target_armour"]:checked').value;
    // get defensive stats
    target_info.defence = document.getElementById('target_defence').value * 1;
    target_info.evasion = document.getElementById('target_evasion').value * 1;
    target_info.crit_res = document.getElementById('target_crit_res').value * 1;
    target_info.crit_dmg_res = document.getElementById('target_crit_dmg_res').value * 1;
    // get misc modifiers
    target_info.damage_reduction = document.getElementById('damage_reduction').value / 100;
    target_info.additional_modifier = document.getElementById('additional_modifier').value / 100;
    return target_info;
}
// calculate damage and display results
function calculateResults() {
    var results = {};
    // final attacker stats
    const final_stat = getFinalStat();
    // target info
    const target_info = getTargetInfo();
    // attack info
    const attack_info = getAttackInfo();
    // get crit dmg res multiplier from total bonus
    const total_bonus = getTotalBonus();
    const crit_dmg_mult = critDmgMult(total_bonus);
    //console.log(crit_dmg_mult);
    // calculate some useful info
    // damage reduction from target def stat
    const defence_damage_multiplier = 1666.667 / (1666.667 + target_info.defence*1.0); //0.7 * Math.pow(0.99925, target_info.defence) + 0.3;
    results.def_dmg_mult = defence_damage_multiplier;
    // critical hit chance
    const crit_net = Math.max(final_stat.crit - target_info.crit_res, 0.0);
    const crit_chance = Math.min(crit_net / (crit_net + 666.66), 0.8);
    results.crit_chance = crit_chance;
    // critical damage
    const crit_damage = Math.max((final_stat.crit_dmg - target_info.crit_dmg_res) * (1 + crit_dmg_mult) / 10000, 1.0);
    results.crit_damage = crit_damage;
    // damage floor (should have a min here shouldn't it?)
    const damage_floor = Math.min(final_stat.stability / (final_stat.stability + 997) + 0.2, 1.0);
    results.damage_floor = damage_floor;
    // hit chance
    const hit_chance = Math.min(700 / (Math.max(target_info.evasion - final_stat.accuracy, 0.0) + 700), 1.0);
    results.hit_chance = hit_chance;
    // terrain affinity multiplier
    const terr_mult = getTerrainMult();
    // armour type multiplier
    const armour_mult = getArmourMult(current_source.damage_type, target_info.armour_type);
    // calculate damages
    // highest non-crit damage
    const damage_high = final_stat.attack * attack_info.multiplier * terr_mult * armour_mult * defence_damage_multiplier * (1 - target_info.damage_reduction) * (1 + target_info.additional_modifier);
    results.damage_high = damage_high; 
    // lowest non-crit damage
    const damage_low = damage_high * damage_floor;
    results.damage_low = damage_low; 
    // highest crit damage
    const damage_crit_high = damage_high * crit_damage;
    results.damage_crit_high = damage_crit_high; 
    // lowest crit damage
    const damage_crit_low = damage_crit_high * damage_floor;
    results.damage_crit_low = damage_crit_low; 
    // average non-crit damage
    const damage_avg = (damage_high + damage_low) / 2;
    results.damage_avg = damage_avg; 
    // average crit damage
    const damage_crit_avg = (damage_crit_high + damage_crit_low) / 2;
    results.damage_crit_avg = damage_crit_avg; 
    // average damage per hit
    const damage_expectation = (damage_avg * crit_chance * crit_damage) + (damage_avg * (1 - crit_chance));
    results.damage_expectation = damage_expectation; 
    // average damage all hits
    const damage_expectation_nhits = damage_expectation * attack_info.n_hits;
    results.damage_expectation_nhits = damage_expectation_nhits; 
    return results;
}
// display results in the right div
function setResults() {
    var results_div = document.getElementById('results');
    const results = calculateResults();
    var p_rows = [];
    for (var key of Object.keys(results)) {
        p_rows.push('<p>' + key + ': ' + results[key] + '</p>');
    }
    results_div.innerHTML = p_rows.join('\r\n');
}


// limit to numerical inputs only for num-input class
function limitNumInputs() {
    var num_inputs = document.getElementsByClassName('num-input');
    for (var i=0; i<num_inputs.length; i++) {
        ni = num_inputs.item(i);
        ni.oninput = function () {
            const max = parseInt(this.max);
            const min = parseInt(this.min);
            var val = 0;
            if (this.classList.contains('allow-decimal')) {
                val = this.value;
                //console.log(val);
            } else {
                val = Math.round(this.value);
                //console.log(val);
            }
            if (isNaN(val) || !val) {
                //console.log('not a number!');
                val = 0;
            } 
            if (val > max) {
                this.value = max; 
            } else if (val < min) {
                this.value = min; 
            } else {
                this.value = val;
            }
        }
    }
}

// load equipment data
loadEquipmentData();
// functions on load
document.addEventListener("DOMContentLoaded", function() {
    // load character data if already selected
    loadCharacterData();
    limitNumInputs();
    // set attack info if already selected
    setCurrentAttack();
    // set buff info if already selected
    setCurrentBuff();
    // set event listeners
    // change of character selection
    var character_source = document.getElementById('character_source');
    character_source.addEventListener('change', loadCharacterData);
    // change of stars
    var char_stars = document.getElementById('char_stars');
    char_stars.addEventListener('change', setUEStatus);
    char_stars.addEventListener('change', setBaseStat);
    char_stars.addEventListener('change', setUEInnateBonus);
    char_stars.addEventListener('change', setUEPassiveBonus);
    // change of level
    var char_level = document.getElementById('char_level');
    char_level.addEventListener('change', setBaseStat);
    // change of bond level
    var char_bond = document.getElementById('char_bond');
    char_bond.addEventListener('change', setBondBonus);
    // change of equipment tier
    var equip_levels = document.getElementById('equip_levels');
    equip_levels.addEventListener('change', setEquipmentBonus);
    // change of passive skill level
    var ps_level = document.getElementById('ps_level');
    ps_level.addEventListener('change', setUEPassiveBonus);
    // change of UE related stats
    var ue_tier = document.getElementById('ue_tier');
    ue_tier.addEventListener('change', setUEMaxLevel);
    ue_tier.addEventListener('change', setUEInnateBonus);
    ue_tier.addEventListener('change', setUEPassiveBonus);
    var ue_level = document.getElementById('ue_level');
    ue_level.addEventListener('change', setUEInnateBonus);
    var buff_select = document.getElementById('buff_select');
    buff_select.addEventListener('change', setCurrentBuff);
    var buff_button = document.getElementById('button_add_buff');
    buff_button.addEventListener('click', addBuff);
    var attack_select = document.getElementById('attack_select');
    attack_select.addEventListener('change', setCurrentAttack);
    var attack_level = document.getElementById('attack_level');
    attack_level.addEventListener('change', setAttackInfo);
    var attack_details = document.getElementById('attack_details');
    attack_details.addEventListener('change', setCustomAttack);
    var calculate_button = document.getElementById('calculate_button');
    calculate_button.addEventListener('click', setResults);
    //calculate_button.addEventListener('click', function () {
    //    const res = calculateResults();
    //    document.getElementById('test').innerHTML = JSON.stringify(res);
    //});
});
