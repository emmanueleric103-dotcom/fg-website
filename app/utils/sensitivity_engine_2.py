
def generate_sensitivity(profile):
    brand = profile.get('brand','others')
    ram = int(profile.get('ram',4))
    iphone_model = profile.get('iphone_model','')
    playstyle = int(profile.get('playstyle',3))
    gyro = profile.get('gyro','none')
    role = profile.get('role','balanced')
    exp = profile.get('experience','intermediate')

    iphone_map = {
        'iphone_7_8_se': 2,
        'iphone_x_xr_11': 3,
        'iphone_12_mini': 4,
        'iphone_12_13_14': 6,
        'iphone_14pro_15': 6,
        'iphone_15promax_16': 8,
        'iphone_15pro_16pro': 8
    }
    effective_ram = ram
    if brand == 'iphone' and iphone_model in iphone_map:
        effective_ram = iphone_map[iphone_model]

    base = {"general":185, "red_dot":175, "scope_2x":155, "scope_4x":135, "sniper":90, "free_look":140, "dpi":400, "fire_button":48}

    ram_adj = {
        2: {"general":12,"red_dot":8,"scope_2x":-12,"scope_4x":-18,"sniper":-12,"free_look":-5,"dpi":25},
        3: {"general":6,"red_dot":4,"scope_2x":-6,"scope_4x":-10,"sniper":-6,"dpi":12},
        4: {},
        6: {"general":-5,"red_dot":-3,"scope_2x":5,"scope_4x":8,"sniper":5,"free_look":3,"dpi":-10},
        8: {"general":-8,"red_dot":-6,"scope_2x":10,"scope_4x":14,"sniper":10,"dpi":-18},
        12: {"general":-12,"red_dot":-10,"scope_2x":14,"scope_4x":18,"sniper":14,"dpi":-28}
    }
    brand_adj = {
        "infinix_smart": {"general":14,"red_dot":12,"scope_2x":-4,"dpi":-5},
        "tecno_spark": {"general":14,"red_dot":12,"scope_2x":-4,"dpi":-5},
        "itel": {"general":16,"red_dot":14,"scope_2x":-6,"dpi":-10},
        "infinix_hot": {"general":7,"red_dot":6,"scope_2x":2,"dpi":5},
        "tecno_camon": {"general":7,"red_dot":6,"scope_2x":2,"dpi":5},
        "samsung": {"general":-4,"red_dot":-3,"scope_2x":2,"sniper":3,"dpi":8},
        "xiaomi": {"general":-3,"red_dot":-3,"scope_2x":3},
        "realme": {"general":-2,"red_dot":-2,"dpi":2},
        "iphone": {"general":-10,"red_dot":-10,"scope_2x":-6,"scope_4x":-4,"sniper":-8,"dpi":-15},
        "others": {}
    }
    play_adj = {2:{"general":-14,"red_dot":-10,"free_look":-12,"fire_button":54},3:{"fire_button":46},4:{"general":10,"red_dot":8,"free_look":14,"fire_button":43}}
    gyro_adj = {"none":{}, "always":{"general":-18,"red_dot":-18,"scope_2x":-18,"scope_4x":-18,"sniper":-22}, "scope_only":{"scope_4x":-10,"sniper":-18}}
    role_adj = {"rusher":{"general":12,"red_dot":12,"scope_2x":10,"scope_4x":-8,"sniper":-18,"free_look":12},"balanced":{}, "sniper":{"general":-12,"red_dot":-10,"scope_2x":-8,"scope_4x":8,"sniper":-24,"free_look":-8}, "support":{"general":-6,"red_dot":-6,"scope_2x":6,"scope_4x":12,"free_look":8}}
    exp_adj = {"beginner":{"general":-22,"red_dot":-18,"scope_2x":-18,"scope_4x":-18,"sniper":-14,"free_look":-12},"intermediate":{}, "pro":{"general":12,"red_dot":10,"scope_2x":10,"scope_4x":6,"sniper":-6,"free_look":6}}

    def apply_adj(target, adj):
        for k,v in adj.items():
            if k in target and k != 'fire_button':
                target[k] += v

    for adj in [ram_adj.get(effective_ram,{}), brand_adj.get(brand,{}), play_adj.get(playstyle,{}), gyro_adj.get(gyro,{}), role_adj.get(role,{}), exp_adj.get(exp,{} )]:
        apply_adj(base, adj)

    if playstyle == 2:
        base['fire_button'] = 56 if effective_ram <=3 else 54
    elif playstyle == 4:
        base['fire_button'] = 43
    else:
        base['fire_button'] = 46

    def clamp(v,mn,mx): return max(mn, min(mx, v))
    base['general']=clamp(base['general'],85,200)
    base['red_dot']=clamp(base['red_dot'],80,200)
    base['scope_2x']=clamp(base['scope_2x'],60,190)
    base['scope_4x']=clamp(base['scope_4x'],50,185)
    base['sniper']=clamp(base['sniper'],20,120)
    base['free_look']=clamp(base['free_look'],60,200)
    base['dpi']=clamp(base['dpi'],360,480)

    iphone_names = {
        'iphone_7_8_se':'iPhone 7/8/SE 2020',
        'iphone_x_xr_11':'iPhone X/XR/11',
        'iphone_12_mini':'iPhone 12 Mini',
        'iphone_12_13_14':'iPhone 12/13/14',
        'iphone_14pro_15':'iPhone 14 Pro/15',
        'iphone_15promax_16':'iPhone 15 Pro Max/16 Pro Max'
    }
    if brand == 'iphone':
        gen_for = f"{iphone_names.get(iphone_model, iphone_model)} | {playstyle} finger | {role} | {exp}"
        tier = 'Low-End' if effective_ram <=2 else 'Mid-Range' if effective_ram <=4 else 'High-End' if effective_ram >=8 else 'Mid-High'
    else:
        gen_for = f"{brand} | {ram}GB RAM | {playstyle} finger | {role} | {exp}"
        tier = 'Low-End' if effective_ram <=3 or brand in ['itel','infinix_smart','tecno_spark'] else 'High-End' if effective_ram >=8 else 'Mid-Range'

    base['meta'] = {"generated_for": gen_for, "device_tier": tier, "effective_ram": effective_ram}
    return base
