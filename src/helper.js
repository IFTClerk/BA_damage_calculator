// stats that need additional processing
const complex_stats = ['attack', 'hp', 'defence', 'heal'];
// star level bonuses to base stat
const star_level_multiplier = {
    "hp": [0.0, 0.05, 0.12, 0.21, 0.35],
    "attack": [0.0, 0.1, 0.22, 0.36, 0.53],
    "defence": [0.0, 0.0, 0.0, 0.0, 0.0],
    "heal": [0.0, 0.075, 0.175, 0.295, 0.445]
};
const stat_name_map = {
    "hp": "HP",
    "attack": "Attack",
    "defence": "Defence",
    "heal": "Healing",
    "accuracy": "Accuracy",
    "evasion": "Evasion",
    "crit": "Crit",
    "crit_dmg": "Crit Dmg",
    "stability": "Stability",
    "range": "Range",
    "crit_res": "Crit Res",
    "crit_dmg_res": "Crit Dmg Res",
    "cc_strength": "CC Strength",
    "cc_res": "CC Res",
    "recovery": "Recovery"
}
// weapon armour matchup chart
const armour_resists = {
    "red": ["yellow", "purple"],
    "yellow": ["blue", "purple"],
    "blue": ["red", "purple"],
    "purple": ["white", "red", "yellow", "blue"]
}
// function that returns stat at a specific level
function interpolateStat(stat_range, level) {
    var low = stat_range[0];
    var high = stat_range[1];
    // interpolate the stat at specified value
    var s = low + (high - low) / 99 * (level - 1);
    return Math.round(s);
}
// function that capitalises the initial letter in a word
function capitaliseWord(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
}
// function that prints out bonuses as string
function printBonuses(bonus_array) {
    if (bonus_array.constructor !== Array) {
        // make input into an array if it is not
        bonus_array = [bonus_array];
    }
    var bonus_string_array = [];
    for (var i=0; i<bonus_array.length; i++) {
        const this_bonus = bonus_array[i];
        const display_name = stat_name_map[this_bonus.status] ? stat_name_map[this_bonus.status] : this_bonus.status;
        if (stat_name_map[this_bonus.status]) {}
        if (this_bonus.type==='mult') {
            // bonus_string_array.push(stat_name_map[this_bonus.status] + ':&nbsp;+' + (this_bonus.value * 100).toFixed(1) + '&#37;');
            bonus_string_array.push(display_name + ':&nbsp;+' + (this_bonus.value * 100).toFixed(1) + '&#37;');
        } else {
            // bonus_string_array.push(stat_name_map[this_bonus.status] + ':&nbsp;+' + this_bonus.value);
            bonus_string_array.push(display_name + ':&nbsp;+' + this_bonus.value);
        }
    }
    return bonus_string_array.join(', ');
}
// function to add two bonuses
function addBonuses(total_bonus, new_bonus) {
    //console.log(total_bonus);
    if (total_bonus.constructor !== Array) {
        // make input into an array if it is not
        total_bonus = [total_bonus];
    }
    if (total_bonus.length===0) {
        // return with new bonus if array is empty
        // need to create new object to not have reference issues
        total_bonus.push({ "status": new_bonus.status, "type": new_bonus.type, "value": new_bonus.value});
        return total_bonus;
    }
    for (var i=0; i<total_bonus.length; i++) {
        var tbi = total_bonus[i];
        if (new_bonus.status===tbi.status && new_bonus.type===tbi.type) {
            //console.log('Same bonus stat and type');
            tbi.value += +new_bonus.value;
            return total_bonus;
        } else if (new_bonus.status===tbi.status && new_bonus.type!==tbi.type) {
            //console.log('Same bonus stat');
            continue;
        } else {
            //console.log('New bonus stat');
            continue;
        }
    }
    total_bonus.push({ "status": new_bonus.status, "type": new_bonus.type, "value": new_bonus.value});
    return total_bonus;
}
// function to split bonuses into flat and multipliers
function splitBonuses(bonus_array) {
    var flat_bonus_array = [];
    var mult_bonus_array = [];
    for (var i=0; i<bonus_array.length; i++) {
        const this_bonus = bonus_array[i];
        if (this_bonus.type=="flat") {
            flat_bonus_array.push(this_bonus);
        } else if (this_bonus.type=="mult") {
            mult_bonus_array.push(this_bonus);
        } else {
            console.log('Bonus does not have a valid type, defaulting to flat');
            flat_bonus_array.push(this_bonus);
        }
    }
    return { "flat": flat_bonus_array, "mult": mult_bonus_array };
}
// function to extract crit damage multiplier from bonuses
function critDmgMult(bonus_array) {
    for (var i=0; i<bonus_array.length; i++) {
        const this_bonus = bonus_array[i];
        if (this_bonus.status=="crit_dmg" && this_bonus.type=="mult") {
            return this_bonus.value;
        }
    }
    return 0.0;
}
// function to roshambo with armour/weapon colours
function getArmourMult(atk, def) {
    if (atk===def) {
        return 2.0;
    } else if (armour_resists[def].includes(atk)) {
        return 0.5;
    } else {
        return 1.0;
    }
}
