<!DOCTYPE html>
<?php 
    $data_dir = 'data/';
    $char_data_dir = 'data/characters/';
    $skill_data_dir = 'data/skills/';

    function fillSkillSelector($json_path) {
        // PHP block to get all skill names
        $skill_json = file_get_contents($json_path);
        $data = json_decode($skill_json);
        // loop over the keys of the json and add entry in selector
        foreach ($data as $key => $value) {
            // get display name and add to option list
            echo '<option value="'.$key.'">'.$value->display_name.'</option>';
        }
    }
    if (! function_exists('str_ends_with')) {
    function str_ends_with(string $haystack, string $needle): bool
        {
            $needle_len = strlen($needle);
            return ($needle_len === 0 || 0 === substr_compare($haystack, $needle, - $needle_len));
        }
    }
?>
<html>
    <!-- HEAD -->
    <head>
        <!-- Meta Stuff -->
        <title>Blue Archive Damage Calculator</title>
        <meta charset="UTF-8">
        <meta name="description" content="A prototype damage calculator for Blue Archive in JS.">
        <meta name="keywords" content="blue archive, damage, calculator">
        <meta name="author" content="IFTClerk">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- Stylesheets -->
        <link rel="stylesheet" href="src/styles.css">
        <!-- JS for the site to run-->
        <script>
            var Settings = {
                data_dir: '<?= $data_dir ?>',
                char_data_dir: '<?= $char_data_dir ?>',
                skill_data_dir: '<?= $skill_data_dir ?>'
            }
        </script>
        <script src="src/helper.js"></script>
        <script src="src/main.js"></script>
    </head>
    <!-- BODY -->
	<body>
        <noscript><table id="js_check" width="300px" border="1" bgcolor="red"><tr><td>Your browser does not support JavaScript. Things are not going to work properly.</td></tr></table></noscript>
        <!-- Title -->
        <h1> Blue Archive Damage Calculator v0</h1>
        <hr class="separator">
        <h2> Character </h2>
		<select id="character_source">
		    <option disabled selected value=""> --Select Character-- </option>
            <?php
                // PHP block to retrieve list of characters from folder
                $char_jsons = array();
                // iterate over directory with all the character JSONs
                foreach (new DirectoryIterator($char_data_dir) as $file) {
                    // skip if is directory or is . or ..
                    if (!$file->isDot() && !$file->isDir()) {
                        $fname = $file->getFilename();
                        // check if file name ends with .json
                        if (!str_ends_with($fname, '.json')) continue;
                        // get file name without .json
                        $char_jsons[] = preg_replace('/\.json$/', '', $fname);
                    }
                }
                // sort the names alphabetically for display
                sort($char_jsons);
                // loop over the name list and display in selector
                foreach ($char_jsons as $file) {
                    // get display name and add to option list
                    $json = file_get_contents($char_data_dir . $file . '.json');
                    $data = json_decode($json);
                    echo '<option value="' . $file . '">' . $data->display_name . '</option>';
                }
            ?>
		</select>
        <!-- <p>The content of this JSON is: <br><span id="json_content"></span></p> -->
        <!-- controls to enter various information -->
        <div id="source_input" style="display:none;">
            <!-- Character Details -->
            <div id="stat_levels">
                <p><b>Status:</b></p>
                <label for="char_stars">Stars: </label>
                <input class="num-input" type="number" id="char_stars" name="char_stars" value=3 min=1 max=5>
                <label for="char_level">Level: </label>
                <input class="num-input" type="number" id="char_level" name="char_level" value=70 min=1 max=100>
                <label for="char_bond">Bond: </label>
                <input class="num-input" type="number" id="char_bond" name="char_bond" value=20 min=1 max=50>
            </div>
            <!-- Enter Equipment Information -->
            <div id="equip_levels">
                <p><b>Equipment:</b></p>
                <label for="eq1_tier"><span id="eq1_name">Equipment 1</span> Tier: </label>
                <input class="num-input" type="number" id="eq1_tier" name="eq1_tier" value=5 min=1 max=6>
                <label for="eq2_tier"><span id="eq2_name">Equipment 2</span> Tier: </label>
                <input class="num-input" type="number" id="eq2_tier" name="eq2_tier" value=5 min=1 max=6>
                <label for="eq3_tier"><span id="eq3_name">Equipment 3</span> Tier: </label>
                <input class="num-input" type="number" id="eq3_tier" name="eq3_tier" value=5 min=1 max=6>
            </div>
            <!-- Enter UE Information -->
            <div id="unique_eq" style="display:none;margin-top:5px;">
                <label for="ue_tier">UE Tier: </label>
                <input class="num-input" type="number" id="ue_tier" name="ue_tier" value=1 min=0 max=5>
                <label for="ue_level">UE Level: </label>
                <input class="num-input" type="number" id="ue_level" name="ue_level" value=30 min=1 max=30>
            </div>
        </div>
        <hr class="separator"> 
        <!--------------------------------------------->
        <div id="base_stats"> 
            <h2> Base Stats </h2>
            <!-- Table to show base stat table -->
            <table class="stat-table" id="base_stat_table">
                <tr>
                    <td class="stat-name">HP</td>
                    <td class="stat-value" id="base_hp">-99999</td>
                    <td class="stat-name">Attack</td>
                    <td class="stat-value" id="base_attack">-9999</td>
                    <td class="stat-name">Defence</td>
                    <td class="stat-value" id="base_defence">-9999</td>
                    <td class="stat-name">Healing</td>
                    <td class="stat-value" id="base_heal">-9999</td>
                </tr>
                <tr>
                    <td class="stat-name">Accuracy</td>
                    <td class="stat-value" id="base_accuracy">-999</td>
                    <td class="stat-name">Evasion</td>
                    <td class="stat-value" id="base_evasion">-999</td>
                    <td class="stat-name">Crit</td>
                    <td class="stat-value" id="base_crit">-999</td>
                    <td class="stat-name">Crit Dmg</td>
                    <td class="stat-value" id="base_crit_dmg">-99999</td>
                </tr>
                <tr>
                    <td class="stat-name">Stability</td>
                    <td class="stat-value" id="base_stability">-9999</td>
                    <td class="stat-name">Range</td>
                    <td class="stat-value" id="base_range">-999</td>
                    <td class="stat-name">Crit Res</td>
                    <td class="stat-value" id="base_crit_res">-999</td>
                    <td class="stat-name">Crit Dmg Res</td>
                    <td class="stat-value" id="base_crit_dmg_res">-9999</td>
                </tr>
                <tr>
                    <td class="stat-name">CC Strength</td>
                    <td class="stat-value" id="base_cc_strength">-999</td>
                    <td class="stat-name">CC Res</td>
                    <td class="stat-value" id="base_cc_res">-999</td>
                    <td class="stat-name">Recovery</td>
                    <td class="stat-value" id="base_recovery">-99999</td>
                </tr>
            </table>
            <hr class="separator">
        </div>
        <!-- Display Various Stat Bonuses -->
        <div id="stat_bonuses" style="display:none;">
            <h2> Stat Bonuses </h2>
            <div id="equipment_bonus">
                <p> Equipment Bonus: <span id="equipment_bonus_value"></span> </p>
            </div>
            <div id="specialist_bonus">
                <p> Specialist Bonus: </p> 
                <table class="stat-table" id="support_stat_table">
                    <tr>
                        <td>HP</td>
                        <td><input class="num-input double-width" type="number" id="spec_hp" name="spec_hp" value=0 min=0></td>
                        <td>Attack</td>
                        <td><input class="num-input double-width" type="number" id="spec_attack" name="spec_attack" value=0 min=0></td>
                        <td>Defence</td>
                        <td><input class="num-input double-width" type="number" id="spec_defence" name="spec_defence" value=0 min=0></td>
                        <td>Healing</td>
                        <td><input class="num-input double-width" type="number" id="spec_heal" name="spec_heal" value=0 min=0></td>
                    </tr>
                </table>
            </div>
            <div> 
                <p id="bond_bonus">Bond Bonus: <span id="bond_bonus_value"></span></p>
            </div>
            <div>
                <p id="ue_bonus_innate">UE Bonus: <span id="ue_bonus_innate_value"></span></p>
                <div id="ue_bonus_ps" style="display:none;">
                    <label for="ps_level">Passive Skill: </label>
                    <input class="num-input" type="number" id="ps_level" name="ps_level" value=10 min=1 max=10>
                    UE Passive Skill Bonus: <span id="ue_bonus_ps_value"></span>
                </div>
            </div>
            <hr class="separator">
        </div>
        <!-- Enter Battle Related Information -->
        <div id="battle_info">
            <h2>Battle Info</h2>
            <div id="terrain">
                Terrain:
                <input checked type="radio" id="terrain_urban" name="battle_terrain" value=0>
                <label for="terrain_urban">Urban</label>
                <input type="radio" id="terrain_outdoor" name="battle_terrain" value=1>
                <label for="terrain_outdoor">Outdoor</label>
                <input type="radio" id="terrain_indoor" name="battle_terrain" value=2>
                <label for="terrain_indoor">Indoor</label>
            </div>
            <div id="buff_info">
                <h3> Buffs & Debuffs </h3>
                <table class="buff-table">
                    <tr> 
                        <th class="buff-name">Source</th>
                        <th class="buff-value">Buff</th>
                        <th class="buff-remove"></th>
                    </tr>
                    <tbody id="buff_table_body">
                    <tr> 
                        <td class="buff-name"></td>
                        <td class="buff-value"></td>
                        <td class="buff-remove"></td>
                    </tr>
                    </tbody>
                </table><br>
                <label for="buff_select">Buff Presets: </label>
		        <select id="buff_select">
		            <option selected disabled value=""> --Select a (de)buff to apply--</option>
                    <optgroup label="Buffs">
                    <?php
                        fillSkillSelector($skill_data_dir."buff.json");
                    ?>
                    </optgroup>
                    <optgroup label="Debuffs">
                    <?php
                        fillSkillSelector($skill_data_dir."debuff.json");
                    ?>
                    </optgroup>
                </select>
                <label for="buff_level"> Buff skill level: </label>
                <input class="num-input" type="number" id="buff_level" name="buff_level" value=1 min=1 max=10>
                <input type="button" id="button_add_buff" value="Add" disabled>
            </div>
            <hr class="separator">
        </div>
        <!-- Enter Attack Information -->
        <div id="attack_info">
            <h2>Attack Info</h2>
            <label for="attack_select">Attack Presets: </label>
		    <select id="attack_select">
		        <option selected disabled value=""> --Select a Skill--</option>
                <optgroup label="Damage Skills">
                <?php
                    fillSkillSelector($skill_data_dir.'damage.json');
                ?>
                </optgroup>
                <optgroup label="Heal Skills">
                <?php
                    fillSkillSelector($skill_data_dir.'heal.json');
                ?>
                </optgroup>
		        <option value="custom"> Custom </option>
            </select>
            <label for="attack_level">Attack Level: </label>
            <input class="num-input" type="number" id="attack_level" name="attack_level" value=1 min=1 max=5>
            <div id="attack_details">
                Action:
                <input checked type="radio" id="skill_damage" name="attack_action" value="damage">
                <label for="skill_damage">Damage</label>
                <input type="radio" id="skill_heal" name="attack_action" value="heal">
                <label for="skill_heal">Heal</label><br>
                <label for="attack_mult">Attack Multiplier: </label>
                <input class="num-input allow-decimal double-width" type="number" id="attack_mult" name="attack_mult" value=0 min=0>&#37;
            </div>
            <label for="attack_nhits">No. of Hits:</label>
            <input class="num-input" type="number" id="attack_nhits" name="attack_nhits" value=1 min=1>
            <hr class="separator">
        </div>
        <!-- Enter Target Information -->
        <div id="target_info">
            <h2>Target Info</h2>
            <div id="target_armour_info">
                Target Armour Type:
                <input checked type="radio" id="armour_red" name="target_armour" value="red">
                <label for="target_armour">Light</label>
                <input type="radio" id="armour_yellow" name="target_armour" value="yellow">
                <label for="target_armour">Heavy</label>
                <input type="radio" id="amour_blue" name="target_armour" value="blue">
                <label for="target_armour">Special</label>
            </div>
            <table class="stat-table" id="target_stat_table">
                <tr>
                    <td>Defence</td>
                    <td><input class="num-input double-width" type="number" id="target_defence" name="target_defence" value=0 min=0></td>
                    <td>Evasion</td>
                    <td><input class="num-input double-width" type="number" id="target_evasion" name="target_evasion" value=0 min=0></td>
                    <td>Crit Res</td>
                    <td><input class="num-input double-width" type="number" id="target_crit_res" name="target_crit_res" value=100 min=0></td>
                    <td>Crit Dmg Res</td>
                    <td><input class="num-input double-width" type="number" id="target_crit_dmg_res" name="target_crit_dmg_res" value=5000 min=0></td>
                    <td>Recovery</td>
                    <td><input class="num-input double-width" type="number" id="target_recovery" name="target_recovery" value=10000 min=0></td>
                </tr>
            </table>
            <label for="damage_reduction">Damage Reduction Modifier:</label>
            <input class="num-input allow-decimal double-width" type="number" id="damage_reduction" name="damage_reduction" value=0>&#37;<br>
            <label for="additional_reduction">Additional Damage Modifier:</label>
            <input class="num-input allow-decimal double-width" type="number" id="additional_modifier" name="additional_modifier" value=0>&#37;
            <hr class="separator">
        </div>
		<input type="button" id="calculate_button" value="Calculate!">
        <!-- Display Formatted Results -->
        <div> 
            <h2>Results</h2>
            <div id="results" class="results-container"></div>
            <hr class="separator">
        </div>
	</body>
</html>
