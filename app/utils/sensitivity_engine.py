"""
FG (HefGe) - SensiLab Expert Engine
Based on 2025-2026 pro player data, device touch sampling, RAM optimization research
Source: BitTopup, Sensi-FF, GamingNewsLab, Free Fire MAX OB50-OB55 pro settings
Scale: New FF 0-200 scale (old 0-100 x2)
"""

def clamp(val, min_v, max_v):
    return max(min_v, min(max_v, int(val)))

def generate_sensitivity(profile):
    """
    profile = {
        brand: infinix_smart, infinix_hot, tecno_spark, tecno_camon, samsung, xiaomi, realme, itel, iphone, others
        ram: 2,3,4,6,8,12 (for iPhone mapped from model)
        iphone_model: iphone_7_8_se, iphone_x_xr_11, iphone_12_mini, iphone_12_13_14, iphone_14pro_15, iphone_15promax_16 etc
        playstyle: 2,3,4
        gyro: none, always, scope_only
        role: rusher, balanced, sniper, support
        experience: beginner, intermediate, pro
    }
    """
    brand = profile.get('brand', 'others')
    iphone_model = profile.get('iphone_model', '')
    
    # iPhone mapping - iPhone no dey use RAM like Android, we use model to determine tier
    iphone_ram_map = {
        'iphone_7_8_se': 2,      # A10-A13, 2GB
        'iphone_x_xr_11': 3,     # A11-A13, 3GB
        'iphone_12_mini': 4,     # A14, 4GB
        'iphone_12_13_14': 6,    # A14-A15-A16, 4-6GB
        'iphone_14pro_15': 6,    # A16-A17, 6GB
        'iphone_15promax_16': 8, # A17Pro-A18, 8GB
        'iphone_15pro_16pro': 8,
    }
    if brand == 'iphone' and iphone_model in iphone_ram_map:
        ram = iphone_ram_map[iphone_model]
    else:
        try:
            ram = int(profile.get('ram', 4))
        except:
            ram = 4

    playstyle = int(profile.get('playstyle', 3))
    gyro = profile.get('gyro', 'none')
    role = profile.get('role', 'balanced')
    exp = profile.get('experience', 'intermediate')

    # BASE - mid range, balanced, 3 finger, intermediate (200 scale) - OB55 pro average
    # Based on research: General 95-100 old = 190-200 new, Red Dot 90-95 old = 180-190 new
    # Pro average from research: 185/175/155/135/90/140
    base = {
        'general': 185,
        'red_dot': 175,
        'scope_2x': 155,
        'scope_4x': 135,
        'sniper': 90,
        'free_look': 140,
        'dpi': 400,
        'fire_button': 48
    }

    # RAM adjustments (based on low-end lag research)
    ram_adj = {
        2: {'general': +12, 'red_dot': +8, 'scope_2x': -12, 'scope_4x': -18, 'sniper': -12, 'free_look': -5, 'dpi': +25},
        3: {'general': +6, 'red_dot': +4, 'scope_2x': -6, 'scope_4x': -10, 'sniper': -6, 'dpi': +12},
        4: {'general': 0, 'red_dot': 0, 'scope_2x': 0, 'scope_4x': 0, 'sniper': 0, 'dpi': 0},
        6: {'general': -5, 'red_dot': -3, 'scope_2x': +5, 'scope_4x': +8, 'sniper': +5, 'free_look': +3, 'dpi': -10},
        8: {'general': -8, 'red_dot': -6, 'scope_2x': +10, 'scope_4x': +14, 'sniper': +10, 'dpi': -18},
        12: {'general': -12, 'red_dot': -10, 'scope_2x': +14, 'scope_4x': +18, 'sniper': +14, 'dpi': -28},
    }
    # Brand adjustments (touch sampling & response)
    brand_adj = {
        'infinix_smart': {'general': +14, 'red_dot': +12, 'scope_2x': -4, 'dpi': -5, 'note': 'Infinix Smart low touch response - higher needed'},
        'tecno_spark': {'general': +14, 'red_dot': +12, 'scope_2x': -4, 'dpi': -5, 'note': 'Tecno Spark low touch response'},
        'itel': {'general': +16, 'red_dot': +14, 'scope_2x': -6, 'dpi': -10, 'note': 'Itel very low response'},
        'infinix_hot': {'general': +7, 'red_dot': +6, 'scope_2x': +2, 'dpi': +5, 'note': 'Infinix Hot mid touch'},
        'tecno_camon': {'general': +7, 'red_dot': +6, 'scope_2x': +2, 'dpi': +5, 'note': 'Tecno Camon mid'},
        'samsung': {'general': -4, 'red_dot': -3, 'scope_2x': +2, 'sniper': +3, 'dpi': +8, 'note': 'Samsung good touch sampling'},
        'xiaomi': {'general': -3, 'red_dot': -3, 'scope_2x': +3, 'dpi': 0, 'note': 'Xiaomi/Redmi good response'},
        'realme': {'general': -2, 'red_dot': -2, 'dpi': +2},
        'iphone': {'general': -10, 'red_dot': -10, 'scope_2x': -6, 'scope_4x': -4, 'sniper': -8, 'dpi': -15, 'note': 'iPhone 120Hz high sampling - lower needed'},
        'others': {'general': 0, 'red_dot': 0},
    }
    # Playstyle adjustments
    play_adj = {
        2: {'general': -14, 'red_dot': -10, 'free_look': -12, 'fire_button': 54, 'note': '2 finger needs more control, bigger fire button'},
        3: {'general': 0, 'red_dot': 0, 'fire_button': 46},
        4: {'general': +10, 'red_dot': +8, 'free_look': +14, 'fire_button': 43, 'note': '4 finger claw needs faster'},
    }
    # Gyro
    gyro_adj = {
        'none': {},
        'always': {'general': -18, 'red_dot': -18, 'scope_2x': -18, 'scope_4x': -18, 'sniper': -22, 'note': 'Gyro handles fine aim'},
        'scope_only': {'scope_4x': -10, 'sniper': -18},
    }
    # Role
    role_adj = {
        'rusher': {'general': +12, 'red_dot': +12, 'scope_2x': +10, 'scope_4x': -8, 'sniper': -18, 'free_look': +12},
        'balanced': {},
        'sniper': {'general': -12, 'red_dot': -10, 'scope_2x': -8, 'scope_4x': +8, 'sniper': -24, 'free_look': -8},
        'support': {'general': -6, 'red_dot': -6, 'scope_2x': +6, 'scope_4x': +12, 'free_look': +8},
    }
    # Experience
    exp_adj = {
        'beginner': {'general': -22, 'red_dot': -18, 'scope_2x': -18, 'scope_4x': -18, 'sniper': -14, 'free_look': -12},
        'intermediate': {},
        'pro': {'general': +12, 'red_dot': +10, 'scope_2x': +10, 'scope_4x': +6, 'sniper': -6, 'free_look': +6},
    }

    # Apply all
    result = base.copy()
    # combine adjustments
    all_adjs = [ram_adj.get(ram, {}), brand_adj.get(brand, {}), play_adj.get(playstyle, {}), gyro_adj.get(gyro, {}), role_adj.get(role, {}), exp_adj.get(exp, {})]
    
    for adj in all_adjs:
        for k, v in adj.items():
            if k in result and isinstance(v, int):
                if k == 'fire_button' and playstyle != 2 and playstyle != 4:
                    # don't override if already set by playstyle logic for 3 finger
                    continue
                result[k] += v
            # handle note separately
    # Handle fire_button override for 2/4 finger
    if playstyle == 2:
        result['fire_button'] = 54
        if ram <= 3:
            result['fire_button'] = 56
    elif playstyle == 4:
        result['fire_button'] = 43
    else:
        result['fire_button'] = 46

    # Clamp
    result['general'] = clamp(result['general'], 85, 200)
    result['red_dot'] = clamp(result['red_dot'], 80, 200)
    result['scope_2x'] = clamp(result['scope_2x'], 60, 190)
    result['scope_4x'] = clamp(result['scope_4x'], 50, 185)
    result['sniper'] = clamp(result['sniper'], 20, 120)
    result['free_look'] = clamp(result['free_look'], 60, 200)
    result['dpi'] = clamp(result['dpi'], 360, 480)
    result['fire_button'] = clamp(result['fire_button'], 38, 60)

    # Generate old scale (0-100) for older FF versions
    result['old_scale'] = {
        'general': clamp(result['general'] // 2, 40, 100),
        'red_dot': clamp(result['red_dot'] // 2, 40, 100),
        'scope_2x': clamp(result['scope_2x'] // 2, 30, 95),
        'scope_4x': clamp(result['scope_4x'] // 2, 25, 90),
        'sniper': clamp(result['sniper'] // 2, 10, 60),
        'free_look': clamp(result['free_look'] // 2, 30, 100),
    }

    # HUD recommendation
    hud_map = {
        2: {
            'title': '2-Finger Thumb - Classic',
            'layout': 'Both thumbs do everything. Keep movement left, aim + main fire right. Fire button 50-55% size, close to aim thumb. Jump & crouch near fire so thumb can reach.',
            'code_example': 'Best for: Comfort, long sessions',
            'fire_size': f"{result['fire_button']}%",
            'tips': ['Keep scope and fire separated', 'Use 52-56% fire button for better drag', 'Practice 10 mins in Training']
        },
        3: {
            'title': '3-Finger Claw - Most Popular in Nigeria',
            'layout': 'Left thumb movement, right thumb aim, LEFT INDEX finger fire button top-left (under index). This separates firing from aiming = faster headshots.',
            'code_example': 'Pro setup: Left index fire top-left, right thumb aim',
            'fire_size': f"Left Fire {result['fire_button']}% | Right Fire 48%",
            'tips': ['Left fire button at 46% size, top-left corner', 'Right fire 48% near aim', 'Gloo wall button near left thumb']
        },
        4: {
            'title': '4-Finger Claw - Pro / E-Sports',
            'layout': 'Left thumb move, left index fire, right thumb aim, right index jump/scope/crouch. Both indexes work = you can shoot + jump + gloo at same time.',
            'code_example': 'Left index fire upper-left, right index jump/scope upper-right',
            'fire_size': f"Fire {result['fire_button']}% (small for speed)",
            'tips': ['Need 1 week to master', 'Use 42-46% fire buttons', 'Place scope separate from fire to avoid overlap']
        }
    }

    # Device specific DPI guide
    dpi_guides = {
        'infinix_smart': 'Infinix Smart / Tecno Spark - Touch response is low, use DPI 380-410. Close background apps, turn on High FPS.',
        'tecno_spark': 'Tecno Spark - DPI 380-410 recommended. Use Game Mode.',
        'infinix_hot': 'Infinix Hot / Tecno Camon - DPI 400-440 best. You have better touch, so slightly lower sensitivity works.',
        'itel': 'Itel - Very low touch, DPI 360-400 max, higher sensitivity needed to compensate lag.',
        'samsung': 'Samsung A series - DPI 400-430, touch sampling 180Hz, use slightly lower sensitivity for control.',
        'xiaomi': 'Xiaomi/Redmi - DPI 380-420, good touch response.',
        'iphone': 'iPhone - 120Hz ProMotion, super low latency. Use lower sensitivity for precision. iPhone no need DPI change, iOS handles it.',
        'others': 'Generic Android - DPI 400 is safe starting point.'
    }

    # iPhone model names for display
    iphone_names = {
        'iphone_7_8_se': 'iPhone 7/8/SE 2020',
        'iphone_x_xr_11': 'iPhone X/XR/11',
        'iphone_12_mini': 'iPhone 12 Mini / 12',
        'iphone_12_13_14': 'iPhone 12/13/14',
        'iphone_14pro_15': 'iPhone 14 Pro/15',
        'iphone_15promax_16': 'iPhone 15 Pro Max/16 Pro Max',
        'iphone_15pro_16pro': 'iPhone 15 Pro/16 Pro',
    }

    # Training tips based on role
    tips_by_role = {
        'rusher': ['Practice jump+shot drags in Training Ground', '50 shots on moving target with Red Dot daily', 'Use M1887 + Desi for close drag practice'],
        'sniper': ['Practice 20 sniper one-shots on long range dummies', 'Free Look + Sniper drag combo', 'Lower Sniper scope = steadier long shots'],
        'balanced': ['30 mins daily: 10 mins close, 10 mid, 10 long', 'Test in Clash Squad before Ranked', 'Copy HUD code from pro, then tweak 2-3 days'],
        'support': ['Focus on 4x scope tracking', 'Gloo wall speed > aim speed', 'Support needs better positioning than aim']
    }

    # Build display string - handle iPhone specially (no RAM)
    if brand == 'iphone' and iphone_model:
        display_device = iphone_names.get(iphone_model, iphone_model)
        gen_for = f"{display_device} | {playstyle} finger | {role} | {exp}"
        device_tier = 'Low-End' if ram <=2 else 'Mid-Range' if ram <=4 else 'High-End' if ram >=8 else 'Mid-High'
    else:
        gen_for = f"{brand} | {ram}GB RAM | {playstyle} finger | {role} | {exp}"
        device_tier = 'Low-End' if ram <= 3 or brand in ['itel', 'infinix_smart', 'tecno_spark'] else 'Mid-Range' if ram <=6 else 'High-End'

    result['meta'] = {
        'brand_note': brand_adj.get(brand, {}).get('note', ''),
        'hud': hud_map.get(playstyle, hud_map[3]),
        'dpi_guide': dpi_guides.get(brand, dpi_guides['others']),
        'training_tips': tips_by_role.get(role, tips_by_role['balanced']),
        'device_tier': device_tier,
        'generated_for': gen_for,
        'is_iphone': brand == 'iphone',
        'iphone_model': iphone_model if brand == 'iphone' else ''
    }

    # Old vs new scale note
    result['scale_note'] = "New OB50+ scale is 0-200. If your game still shows 0-100, divide by 2 (we provide both)."

    return result
