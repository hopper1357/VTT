const actions = [
    {
        "id": "sword_attack",
        "label": "Sword Attack",
        "formula": "1d20 + @strength_mod + @proficiency",
        "onSuccess": "damage(target, 1d8 + @strength_mod)"
    }
];

console.log(JSON.stringify(actions, null, 2));
